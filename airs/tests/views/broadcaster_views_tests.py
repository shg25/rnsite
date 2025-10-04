import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from ...models import Broadcaster, Program, Air, Nanitozo

UserModel = get_user_model()


class BroadcasterListViewTests(TestCase):
    def setUp(self):
        # ユーザー作成
        self.user1 = UserModel.objects.create_user(
            username='test_user1',
            last_name='TST'
        )
        self.user2 = UserModel.objects.create_user(
            username='test_user2',
            last_name='USR'
        )

    def test_データなし(self):
        response = self.client.get(reverse('airs:broadcasters'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'データなし（ありえない）')
        self.assertQuerysetEqual(response.context['broadcaster_list'], [])

    def test_放送局のみで何卒なし_表示されない(self):
        # 放送局のみ作成（airなし、nanitozoなし）
        broadcaster = Broadcaster.objects.create(
            radiko_identifier='TBS',
            name='TBSラジオ',
            abbreviation='TBS',
            address='東京都'
        )

        response = self.client.get(reverse('airs:broadcasters'))
        self.assertEqual(response.status_code, 200)
        # 何卒数が0なので表示されない
        self.assertNotContains(response, 'TBSラジオ')
        self.assertQuerysetEqual(response.context['broadcaster_list'], [])

    def test_何卒数の降順ソート(self):
        # 放送局作成
        broadcaster1 = Broadcaster.objects.create(
            radiko_identifier='TBS',
            name='TBSラジオ',
            abbreviation='TBS',
            address='東京都'
        )
        broadcaster2 = Broadcaster.objects.create(
            radiko_identifier='QRR',
            name='文化放送',
            abbreviation='QRR',
            address='東京都'
        )
        broadcaster3 = Broadcaster.objects.create(
            radiko_identifier='LFR',
            name='ニッポン放送',
            abbreviation='LFR',
            address='東京都'
        )

        # 番組作成
        program1 = Program.objects.create(name='番組A')
        program2 = Program.objects.create(name='番組B')
        program3 = Program.objects.create(name='番組C')

        # Air作成
        now = timezone.now()
        air1_1 = Air.objects.create(
            broadcaster=broadcaster1,
            program=program1,
            name='TBS番組A第1回',
            started_at=now - datetime.timedelta(days=3),
            ended_at=now - datetime.timedelta(days=3, hours=-1)
        )
        air1_2 = Air.objects.create(
            broadcaster=broadcaster1,
            program=program1,
            name='TBS番組A第2回',
            started_at=now - datetime.timedelta(days=2),
            ended_at=now - datetime.timedelta(days=2, hours=-1)
        )
        air2_1 = Air.objects.create(
            broadcaster=broadcaster2,
            program=program2,
            name='QRR番組B第1回',
            started_at=now - datetime.timedelta(days=1),
            ended_at=now - datetime.timedelta(days=1, hours=-1)
        )
        air3_1 = Air.objects.create(
            broadcaster=broadcaster3,
            program=program3,
            name='LFR番組C第1回',
            started_at=now - datetime.timedelta(days=4),
            ended_at=now - datetime.timedelta(days=4, hours=-1)
        )

        # Nanitozo作成
        # TBS: 3何卒（air1_1に2件、air1_2に1件）
        Nanitozo.objects.create(air=air1_1, user=self.user1, comment='コメント1')
        Nanitozo.objects.create(air=air1_1, user=self.user2, comment='コメント2')
        Nanitozo.objects.create(air=air1_2, user=self.user1, comment='コメント3')

        # QRR: 1何卒
        Nanitozo.objects.create(air=air2_1, user=self.user1, comment='コメント4')

        # LFR: 2何卒
        Nanitozo.objects.create(air=air3_1, user=self.user1, comment='コメント5')
        Nanitozo.objects.create(air=air3_1, user=self.user2, comment='コメント6')

        response = self.client.get(reverse('airs:broadcasters'))
        self.assertEqual(response.status_code, 200)

        # 何卒数降順: TBS(3) > LFR(2) > QRR(1)
        self.assertQuerysetEqual(
            response.context['broadcaster_list'],
            [broadcaster1, broadcaster3, broadcaster2],
            transform=lambda x: x
        )

    def test_air_countとnanitozo_countの集計(self):
        # 放送局作成
        broadcaster = Broadcaster.objects.create(
            radiko_identifier='TBS',
            name='TBSラジオ',
            abbreviation='TBS',
            address='東京都'
        )

        # 番組作成
        program1 = Program.objects.create(name='番組A')
        program2 = Program.objects.create(name='番組B')

        # Air作成（3件）
        now = timezone.now()
        air1 = Air.objects.create(
            broadcaster=broadcaster,
            program=program1,
            name='第1回',
            started_at=now - datetime.timedelta(days=3),
            ended_at=now - datetime.timedelta(days=3, hours=-1)
        )
        air2 = Air.objects.create(
            broadcaster=broadcaster,
            program=program1,
            name='第2回',
            started_at=now - datetime.timedelta(days=2),
            ended_at=now - datetime.timedelta(days=2, hours=-1)
        )
        air3 = Air.objects.create(
            broadcaster=broadcaster,
            program=program2,
            name='第3回',
            started_at=now - datetime.timedelta(days=1),
            ended_at=now - datetime.timedelta(days=1, hours=-1)
        )

        # Nanitozo作成（5件）
        Nanitozo.objects.create(air=air1, user=self.user1, comment='コメント1')
        Nanitozo.objects.create(air=air1, user=self.user2, comment='コメント2')
        Nanitozo.objects.create(air=air2, user=self.user1, comment='コメント3')
        Nanitozo.objects.create(air=air2, user=self.user2, comment='コメント4')
        Nanitozo.objects.create(air=air3, user=self.user1, comment='コメント5')

        response = self.client.get(reverse('airs:broadcasters'))
        self.assertEqual(response.status_code, 200)

        broadcaster_in_list = response.context['broadcaster_list'][0]
        self.assertEqual(broadcaster_in_list.air_count, 3)
        self.assertEqual(broadcaster_in_list.nanitozo_count, 5)

        # テンプレートでの表示確認（HTML構造に依存しない数値のみチェック）
        self.assertContains(response, '5<small>何卒</small>')
        self.assertContains(response, '3<small>放送</small>')

    def test_何卒数0の放送局は除外される(self):
        # 放送局作成
        broadcaster_with_nanitozo = Broadcaster.objects.create(
            radiko_identifier='TBS',
            name='何卒ありラジオ',
            abbreviation='TBS',
            address='東京都'
        )
        broadcaster_without_nanitozo = Broadcaster.objects.create(
            radiko_identifier='QRR',
            name='何卒なしラジオ',
            abbreviation='QRR',
            address='東京都'
        )

        # 番組作成
        program = Program.objects.create(name='番組A')

        # Air作成
        now = timezone.now()
        air1 = Air.objects.create(
            broadcaster=broadcaster_with_nanitozo,
            program=program,
            name='第1回',
            started_at=now - datetime.timedelta(days=1),
            ended_at=now - datetime.timedelta(days=1, hours=-1)
        )
        air2 = Air.objects.create(
            broadcaster=broadcaster_without_nanitozo,
            program=program,
            name='第2回',
            started_at=now - datetime.timedelta(days=2),
            ended_at=now - datetime.timedelta(days=2, hours=-1)
        )

        # air1のみ何卒作成
        Nanitozo.objects.create(air=air1, user=self.user1, comment='コメント')

        response = self.client.get(reverse('airs:broadcasters'))
        self.assertEqual(response.status_code, 200)

        # 何卒ありの放送局のみ表示される
        self.assertQuerysetEqual(
            response.context['broadcaster_list'],
            [broadcaster_with_nanitozo],
            transform=lambda x: x
        )
        self.assertContains(response, '何卒ありラジオ')
        self.assertNotContains(response, '何卒なしラジオ')

    def test_同じ何卒数の場合_名前昇順ソート(self):
        # 放送局作成
        broadcaster1 = Broadcaster.objects.create(
            radiko_identifier='TBS',
            name='Cラジオ',
            abbreviation='TBS',
            address='東京都'
        )
        broadcaster2 = Broadcaster.objects.create(
            radiko_identifier='QRR',
            name='Aラジオ',
            abbreviation='QRR',
            address='東京都'
        )
        broadcaster3 = Broadcaster.objects.create(
            radiko_identifier='LFR',
            name='Bラジオ',
            abbreviation='LFR',
            address='東京都'
        )

        # 番組作成
        program = Program.objects.create(name='番組A')

        # Air作成（各局1件ずつ）
        now = timezone.now()
        air1 = Air.objects.create(
            broadcaster=broadcaster1,
            program=program,
            name='第1回',
            started_at=now - datetime.timedelta(days=3),
            ended_at=now - datetime.timedelta(days=3, hours=-1)
        )
        air2 = Air.objects.create(
            broadcaster=broadcaster2,
            program=program,
            name='第2回',
            started_at=now - datetime.timedelta(days=2),
            ended_at=now - datetime.timedelta(days=2, hours=-1)
        )
        air3 = Air.objects.create(
            broadcaster=broadcaster3,
            program=program,
            name='第3回',
            started_at=now - datetime.timedelta(days=1),
            ended_at=now - datetime.timedelta(days=1, hours=-1)
        )

        # 全局1何卒ずつ
        Nanitozo.objects.create(air=air1, user=self.user1, comment='コメント1')
        Nanitozo.objects.create(air=air2, user=self.user1, comment='コメント2')
        Nanitozo.objects.create(air=air3, user=self.user1, comment='コメント3')

        response = self.client.get(reverse('airs:broadcasters'))
        self.assertEqual(response.status_code, 200)

        # 名前昇順: Aラジオ -> Bラジオ -> Cラジオ
        broadcaster_list = response.context['broadcaster_list']
        self.assertEqual(len(broadcaster_list), 3)
        self.assertEqual(broadcaster_list[0], broadcaster2)  # Aラジオ
        self.assertEqual(broadcaster_list[1], broadcaster3)  # Bラジオ
        self.assertEqual(broadcaster_list[2], broadcaster1)  # Cラジオ


class BroadcasterDetailViewTests(TestCase):
    def setUp(self):
        # 放送局作成
        self.broadcaster = Broadcaster.objects.create(
            radiko_identifier='TBS',
            name='TBSラジオ',
            abbreviation='TBS',
            address='東京都',
            site_url='https://www.tbsradio.jp/',
            wikipedia_url='https://ja.wikipedia.org/wiki/TBS%E3%83%A9%E3%82%B8%E3%82%AA'
        )

        # ユーザー作成
        self.user1 = UserModel.objects.create_user(
            username='test_user1',
            last_name='AAA'
        )
        self.user2 = UserModel.objects.create_user(
            username='test_user2',
            last_name='BBB'
        )

    def test_放送局詳細の基本表示(self):
        response = self.client.get(reverse('airs:broadcaster', kwargs={'pk': self.broadcaster.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TBSラジオ')
        # abbreviationはコメントアウトされているため表示されない
        # （ただしnameに「TBS」が含まれているため、TBSという文字列自体は存在する）

    def test_統計情報の集計_何卒あり(self):
        # 番組作成
        program1 = Program.objects.create(name='番組A')
        program2 = Program.objects.create(name='番組B')

        # Air作成（3件）
        now = timezone.now()
        air1 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=program1,
            name='第1回',
            started_at=now - datetime.timedelta(days=3),
            ended_at=now - datetime.timedelta(days=3, hours=-1)
        )
        air2 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=program1,
            name='第2回',
            started_at=now - datetime.timedelta(days=2),
            ended_at=now - datetime.timedelta(days=2, hours=-1)
        )
        air3 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=program2,
            name='第3回',
            started_at=now - datetime.timedelta(days=1),
            ended_at=now - datetime.timedelta(days=1, hours=-1)
        )

        # Nanitozo作成（5件）
        Nanitozo.objects.create(air=air1, user=self.user1, comment='コメント1')
        Nanitozo.objects.create(air=air1, user=self.user2, comment='コメント2')
        Nanitozo.objects.create(air=air2, user=self.user1, comment='コメント3')
        Nanitozo.objects.create(air=air2, user=self.user2, comment='コメント4')
        Nanitozo.objects.create(air=air3, user=self.user1, comment='コメント5')

        response = self.client.get(reverse('airs:broadcaster', kwargs={'pk': self.broadcaster.pk}))
        self.assertEqual(response.status_code, 200)

        # コンテキスト変数の確認
        self.assertEqual(response.context['broadcaster_air_count'], 3)
        self.assertEqual(response.context['broadcaster_nanitozo_count'], 5)

        # テンプレートでの表示確認
        self.assertContains(response, '5何卒')
        self.assertContains(response, '3放送')

    def test_統計情報の集計_何卒なし(self):
        # Airのみ作成（何卒なし）
        program = Program.objects.create(name='番組A')
        now = timezone.now()
        Air.objects.create(
            broadcaster=self.broadcaster,
            program=program,
            name='第1回',
            started_at=now - datetime.timedelta(days=1),
            ended_at=now - datetime.timedelta(days=1, hours=-1)
        )

        response = self.client.get(reverse('airs:broadcaster', kwargs={'pk': self.broadcaster.pk}))
        self.assertEqual(response.status_code, 200)

        # 何卒0件でも統計情報は表示される
        self.assertEqual(response.context['broadcaster_air_count'], 1)
        self.assertEqual(response.context['broadcaster_nanitozo_count'], 0)
        self.assertContains(response, '0何卒')
        self.assertContains(response, '1放送')

    def test_番組別何卒ランキングの表示(self):
        # 番組作成
        program1 = Program.objects.create(name='番組A')
        program2 = Program.objects.create(name='番組B')
        program3 = Program.objects.create(name='番組C')

        # Air作成
        now = timezone.now()
        air1_1 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=program1,
            name='番組A第1回',
            started_at=now - datetime.timedelta(days=5),
            ended_at=now - datetime.timedelta(days=5, hours=-1)
        )
        air1_2 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=program1,
            name='番組A第2回',
            started_at=now - datetime.timedelta(days=4),
            ended_at=now - datetime.timedelta(days=4, hours=-1)
        )
        air2_1 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=program2,
            name='番組B第1回',
            started_at=now - datetime.timedelta(days=3),
            ended_at=now - datetime.timedelta(days=3, hours=-1)
        )
        air3_1 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=program3,
            name='番組C第1回',
            started_at=now - datetime.timedelta(days=2),
            ended_at=now - datetime.timedelta(days=2, hours=-1)
        )

        # Nanitozo作成
        # program1: 3何卒
        Nanitozo.objects.create(air=air1_1, user=self.user1, comment='コメント1')
        Nanitozo.objects.create(air=air1_1, user=self.user2, comment='コメント2')
        Nanitozo.objects.create(air=air1_2, user=self.user1, comment='コメント3')
        # program2: 2何卒
        Nanitozo.objects.create(air=air2_1, user=self.user1, comment='コメント4')
        Nanitozo.objects.create(air=air2_1, user=self.user2, comment='コメント5')
        # program3: 1何卒
        Nanitozo.objects.create(air=air3_1, user=self.user1, comment='コメント6')

        response = self.client.get(reverse('airs:broadcaster', kwargs={'pk': self.broadcaster.pk}))
        self.assertEqual(response.status_code, 200)

        # ランキング順序の確認（何卒数降順、同数の場合name昇順）
        ranking = response.context['program_nanitozo_ranking']
        self.assertEqual(len(ranking), 3)
        self.assertEqual(ranking[0], program1)
        self.assertEqual(ranking[0].nanitozo_count, 3)
        self.assertEqual(ranking[1], program2)
        self.assertEqual(ranking[1].nanitozo_count, 2)
        self.assertEqual(ranking[2], program3)
        self.assertEqual(ranking[2].nanitozo_count, 1)

        # テンプレートでの表示確認
        self.assertContains(response, '番組A')
        self.assertContains(response, '番組B')
        self.assertContains(response, '番組C')
        # 放送回数も表示される
        self.assertEqual(ranking[0].air_count, 2)  # 番組Aは2回放送
        self.assertEqual(ranking[1].air_count, 1)  # 番組Bは1回放送
        self.assertEqual(ranking[2].air_count, 1)  # 番組Cは1回放送

    def test_何卒0件の場合_番組ランキング非表示(self):
        response = self.client.get(reverse('airs:broadcaster', kwargs={'pk': self.broadcaster.pk}))
        self.assertEqual(response.status_code, 200)

        # ランキングが空
        ranking = response.context['program_nanitozo_ranking']
        self.assertEqual(len(ranking), 0)

    def test_番組ランキング_トップ10のみ表示(self):
        # 15番組作成
        programs = []
        for i in range(1, 16):
            programs.append(Program.objects.create(name=f'番組{i:02d}'))

        # 各番組に異なる数の何卒を作成（番組01が15何卒、番組02が14何卒...）
        now = timezone.now()
        for idx, program in enumerate(programs):
            nanitozo_count = 15 - idx
            air = Air.objects.create(
                broadcaster=self.broadcaster,
                program=program,
                name=f'{program.name}第1回',
                started_at=now - datetime.timedelta(days=idx+1),
                ended_at=now - datetime.timedelta(days=idx+1, hours=-1)
            )
            # 何卒を作成（user1とuser2を交互に使用）
            for j in range(nanitozo_count):
                user = self.user1 if j % 2 == 0 else self.user2
                # 同じairに同じuserが複数何卒できないので、追加のairを作成
                if j > 0:
                    air = Air.objects.create(
                        broadcaster=self.broadcaster,
                        program=program,
                        name=f'{program.name}第{j+1}回',
                        started_at=now - datetime.timedelta(days=idx+1, hours=j),
                        ended_at=now - datetime.timedelta(days=idx+1, hours=j-1)
                    )
                Nanitozo.objects.create(air=air, user=user, comment=f'コメント{j}')

        response = self.client.get(reverse('airs:broadcaster', kwargs={'pk': self.broadcaster.pk}))
        self.assertEqual(response.status_code, 200)

        # トップ10のみ表示される
        ranking = response.context['program_nanitozo_ranking']
        self.assertEqual(len(ranking), 10)

        # 1位から10位まで確認
        for i in range(10):
            self.assertEqual(ranking[i], programs[i])
            self.assertEqual(ranking[i].nanitozo_count, 15 - i)

        # 11位以降は表示されない
        self.assertNotContains(response, '番組11')
        self.assertNotContains(response, '番組15')
