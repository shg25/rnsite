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

        # テンプレートでの表示確認
        self.assertContains(response, '5何卒（3放送）')

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
