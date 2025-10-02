import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from ...models import Broadcaster, Program, Air, Nanitozo

UserModel = get_user_model()


class ProgramsListViewTests(TestCase):
    def setUp(self):
        # 放送局作成
        self.broadcaster = Broadcaster.objects.create(
            radiko_identifier='TBS',
            name='TBSラジオ',
            abbreviation='TBS',
            address='東京都'
        )

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
        response = self.client.get(reverse('airs:programs'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'データなし（ありえない）')
        self.assertQuerysetEqual(response.context['program_list'], [])

    def test_番組のみで何卒なし_表示されない(self):
        # 番組のみ作成（airなし、nanitozoなし）
        program = Program.objects.create(name='番組A')

        response = self.client.get(reverse('airs:programs'))
        self.assertEqual(response.status_code, 200)
        # 何卒数が0なので表示されない
        self.assertNotContains(response, '番組A')
        self.assertQuerysetEqual(response.context['program_list'], [])

    def test_何卒数の降順ソート(self):
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
            started_at=now - datetime.timedelta(days=3),
            ended_at=now - datetime.timedelta(days=3, hours=-1)
        )
        air1_2 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=program1,
            name='番組A第2回',
            started_at=now - datetime.timedelta(days=2),
            ended_at=now - datetime.timedelta(days=2, hours=-1)
        )
        air2_1 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=program2,
            name='番組B第1回',
            started_at=now - datetime.timedelta(days=1),
            ended_at=now - datetime.timedelta(days=1, hours=-1)
        )
        air3_1 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=program3,
            name='番組C第1回',
            started_at=now - datetime.timedelta(days=4),
            ended_at=now - datetime.timedelta(days=4, hours=-1)
        )

        # Nanitozo作成
        # 番組A: 3何卒（air1_1に2件、air1_2に1件）
        Nanitozo.objects.create(air=air1_1, user=self.user1, comment='コメント1')
        Nanitozo.objects.create(air=air1_1, user=self.user2, comment='コメント2')
        Nanitozo.objects.create(air=air1_2, user=self.user1, comment='コメント3')

        # 番組B: 1何卒
        Nanitozo.objects.create(air=air2_1, user=self.user1, comment='コメント4')

        # 番組C: 2何卒
        Nanitozo.objects.create(air=air3_1, user=self.user1, comment='コメント5')
        Nanitozo.objects.create(air=air3_1, user=self.user2, comment='コメント6')

        response = self.client.get(reverse('airs:programs'))
        self.assertEqual(response.status_code, 200)

        # 何卒数降順: 番組A(3) > 番組C(2) > 番組B(1)
        self.assertQuerysetEqual(
            response.context['program_list'],
            [program1, program3, program2],
            transform=lambda x: x
        )

    def test_air_countとnanitozo_countの集計(self):
        # 番組作成
        program = Program.objects.create(name='テスト番組')

        # Air作成（3件）
        now = timezone.now()
        air1 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=program,
            name='第1回',
            started_at=now - datetime.timedelta(days=3),
            ended_at=now - datetime.timedelta(days=3, hours=-1)
        )
        air2 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=program,
            name='第2回',
            started_at=now - datetime.timedelta(days=2),
            ended_at=now - datetime.timedelta(days=2, hours=-1)
        )
        air3 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=program,
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

        response = self.client.get(reverse('airs:programs'))
        self.assertEqual(response.status_code, 200)

        program_in_list = response.context['program_list'][0]
        self.assertEqual(program_in_list.air_count, 3)
        self.assertEqual(program_in_list.nanitozo_count, 5)

        # テンプレートでの表示確認
        self.assertContains(response, '5何卒（3放送）')

    def test_何卒数0の番組は除外される(self):
        # 番組作成
        program_with_nanitozo = Program.objects.create(name='何卒あり番組')
        program_without_nanitozo = Program.objects.create(name='何卒なし番組')

        # Air作成
        now = timezone.now()
        air1 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=program_with_nanitozo,
            name='第1回',
            started_at=now - datetime.timedelta(days=1),
            ended_at=now - datetime.timedelta(days=1, hours=-1)
        )
        air2 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=program_without_nanitozo,
            name='第2回',
            started_at=now - datetime.timedelta(days=2),
            ended_at=now - datetime.timedelta(days=2, hours=-1)
        )

        # air1のみ何卒作成
        Nanitozo.objects.create(air=air1, user=self.user1, comment='コメント')

        response = self.client.get(reverse('airs:programs'))
        self.assertEqual(response.status_code, 200)

        # 何卒ありの番組のみ表示される
        self.assertQuerysetEqual(
            response.context['program_list'],
            [program_with_nanitozo],
            transform=lambda x: x
        )
        self.assertContains(response, '何卒あり番組')
        self.assertNotContains(response, '何卒なし番組')
