import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from ...models import Broadcaster, Program, Air, Nanitozo

UserModel = get_user_model()


class UserListViewTests(TestCase):
    def setUp(self):
        # 放送局作成
        self.broadcaster = Broadcaster.objects.create(
            radiko_identifier='TBS',
            name='TBSラジオ',
            abbreviation='TBS',
            address='東京都'
        )

        # 番組作成
        self.program = Program.objects.create(name='番組A')

    def test_データなし(self):
        response = self.client.get(reverse('airs:users'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'データなし（ありえない）')
        self.assertQuerysetEqual(response.context['user_list'], [])

    def test_ユーザーのみで何卒なし_表示されない(self):
        # ユーザーのみ作成（nanitozoなし）
        user = UserModel.objects.create_user(
            username='test_user1',
            last_name='TST'
        )

        response = self.client.get(reverse('airs:users'))
        self.assertEqual(response.status_code, 200)
        # 何卒数が0なので表示されない
        self.assertNotContains(response, 'TST')
        self.assertQuerysetEqual(response.context['user_list'], [])

    def test_何卒数の降順ソート(self):
        # ユーザー作成
        user1 = UserModel.objects.create_user(
            username='test_user1',
            last_name='AAA'
        )
        user2 = UserModel.objects.create_user(
            username='test_user2',
            last_name='BBB'
        )
        user3 = UserModel.objects.create_user(
            username='test_user3',
            last_name='CCC'
        )

        # Air作成
        now = timezone.now()
        air1 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=self.program,
            name='第1回',
            started_at=now - datetime.timedelta(days=3),
            ended_at=now - datetime.timedelta(days=3, hours=-1)
        )
        air2 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=self.program,
            name='第2回',
            started_at=now - datetime.timedelta(days=2),
            ended_at=now - datetime.timedelta(days=2, hours=-1)
        )
        air3 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=self.program,
            name='第3回',
            started_at=now - datetime.timedelta(days=1),
            ended_at=now - datetime.timedelta(days=1, hours=-1)
        )

        # Nanitozo作成
        # user1: 3何卒
        Nanitozo.objects.create(air=air1, user=user1, comment='コメント1')
        Nanitozo.objects.create(air=air2, user=user1, comment='コメント2')
        Nanitozo.objects.create(air=air3, user=user1, comment='コメント3')

        # user2: 1何卒
        Nanitozo.objects.create(air=air1, user=user2, comment='コメント4')

        # user3: 2何卒
        Nanitozo.objects.create(air=air1, user=user3, comment='コメント5')
        Nanitozo.objects.create(air=air2, user=user3, comment='コメント6')

        response = self.client.get(reverse('airs:users'))
        self.assertEqual(response.status_code, 200)

        # 何卒数降順: user1(3) > user3(2) > user2(1)
        self.assertQuerysetEqual(
            response.context['user_list'],
            [user1, user3, user2],
            transform=lambda x: x
        )

    def test_program_countとnanitozo_countの集計(self):
        # ユーザー作成
        user = UserModel.objects.create_user(
            username='test_user1',
            last_name='TST'
        )

        # 番組作成（2つ）
        program2 = Program.objects.create(name='番組B')

        # Air作成（番組Aが2件、番組Bが1件）
        now = timezone.now()
        air1 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=self.program,
            name='第1回',
            started_at=now - datetime.timedelta(days=3),
            ended_at=now - datetime.timedelta(days=3, hours=-1)
        )
        air2 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=self.program,
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

        # Nanitozo作成（3件、2番組）
        Nanitozo.objects.create(air=air1, user=user, comment='コメント1')
        Nanitozo.objects.create(air=air2, user=user, comment='コメント2')
        Nanitozo.objects.create(air=air3, user=user, comment='コメント3')

        response = self.client.get(reverse('airs:users'))
        self.assertEqual(response.status_code, 200)

        user_in_list = response.context['user_list'][0]
        self.assertEqual(user_in_list.nanitozo_count, 3)
        self.assertEqual(user_in_list.program_count, 2)

        # テンプレートでの表示確認（HTML構造に依存しない数値のみチェック）
        self.assertContains(response, '3<small>何卒</small>')
        self.assertContains(response, '2<small>番組</small>')

    def test_何卒数0のユーザーは除外される(self):
        # ユーザー作成
        user_with_nanitozo = UserModel.objects.create_user(
            username='test_user1',
            last_name='AAA'
        )
        user_without_nanitozo = UserModel.objects.create_user(
            username='test_user2',
            last_name='BBB'
        )

        # Air作成
        now = timezone.now()
        air = Air.objects.create(
            broadcaster=self.broadcaster,
            program=self.program,
            name='第1回',
            started_at=now - datetime.timedelta(days=1),
            ended_at=now - datetime.timedelta(days=1, hours=-1)
        )

        # user_with_nanitozoのみ何卒作成
        Nanitozo.objects.create(air=air, user=user_with_nanitozo, comment='コメント')

        response = self.client.get(reverse('airs:users'))
        self.assertEqual(response.status_code, 200)

        # 何卒ありのユーザーのみ表示される
        self.assertQuerysetEqual(
            response.context['user_list'],
            [user_with_nanitozo],
            transform=lambda x: x
        )
        self.assertContains(response, 'AAA')
        self.assertNotContains(response, 'BBB')

    def test_スーパーユーザーは除外される(self):
        # 通常ユーザー作成
        normal_user = UserModel.objects.create_user(
            username='test_user1',
            last_name='AAA'
        )
        # スーパーユーザー作成
        super_user = UserModel.objects.create_superuser(
            username='admin',
            last_name='ADMIN',
            password='password'
        )

        # Air作成
        now = timezone.now()
        air1 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=self.program,
            name='第1回',
            started_at=now - datetime.timedelta(days=2),
            ended_at=now - datetime.timedelta(days=2, hours=-1)
        )
        air2 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=self.program,
            name='第2回',
            started_at=now - datetime.timedelta(days=1),
            ended_at=now - datetime.timedelta(days=1, hours=-1)
        )

        # 両方のユーザーに何卒作成
        Nanitozo.objects.create(air=air1, user=normal_user, comment='コメント1')
        Nanitozo.objects.create(air=air2, user=super_user, comment='コメント2')

        response = self.client.get(reverse('airs:users'))
        self.assertEqual(response.status_code, 200)

        # 通常ユーザーのみ表示される
        self.assertQuerysetEqual(
            response.context['user_list'],
            [normal_user],
            transform=lambda x: x
        )
        self.assertContains(response, 'AAA')
        self.assertNotContains(response, 'ADMIN')

    def test_同じ何卒数の場合_last_name昇順ソート(self):
        # ユーザー作成
        user1 = UserModel.objects.create_user(
            username='test_user1',
            last_name='CCC'
        )
        user2 = UserModel.objects.create_user(
            username='test_user2',
            last_name='AAA'
        )
        user3 = UserModel.objects.create_user(
            username='test_user3',
            last_name='BBB'
        )

        # Air作成
        now = timezone.now()
        air1 = Air.objects.create(
            broadcaster=self.broadcaster,
            program=self.program,
            name='第1回',
            started_at=now - datetime.timedelta(days=3),
            ended_at=now - datetime.timedelta(days=3, hours=-1)
        )

        # 全員1何卒ずつ
        Nanitozo.objects.create(air=air1, user=user1, comment='コメント1')
        Nanitozo.objects.create(air=air1, user=user2, comment='コメント2')
        Nanitozo.objects.create(air=air1, user=user3, comment='コメント3')

        response = self.client.get(reverse('airs:users'))
        self.assertEqual(response.status_code, 200)

        # last_name昇順: AAA -> BBB -> CCC
        user_list = response.context['user_list']
        self.assertEqual(len(user_list), 3)
        self.assertEqual(user_list[0], user2)  # AAA
        self.assertEqual(user_list[1], user3)  # BBB
        self.assertEqual(user_list[2], user1)  # CCC
