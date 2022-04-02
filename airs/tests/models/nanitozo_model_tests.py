import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ...models import Air, Broadcaster, Nanitozo

UserModel = get_user_model()


def create_user(username, email, password, last_name):
    return UserModel.objects.create(username=username, email=email, password=password, last_name=last_name)


def create_air(name, started_at, ended_at):
    return Air.objects.create(name=name, started_at=started_at, ended_at=ended_at)


def create_airs(name, timedelta_day):
    started = timezone.now() + datetime.timedelta(days=-timedelta_day, hours=-1)
    ended = timezone.now() + datetime.timedelta(days=-timedelta_day)
    return create_air(name, started, ended)


def create_nanitozo(air, user, good, comment_open, created_at):
    return Nanitozo.objects.create(air=air, user=user, good=good, comment_open=comment_open, created_at=created_at)


class NanitozoModelHasCommentTests(TestCase):

    def setUp(self):
        self.air = create_airs('放送1', 1)
        self.user = create_user('test1', 'test1@test.com', 't11111', 'ABC')
        self.created_at = timezone.now() + datetime.timedelta(days=-1, hours=-1)

    def test_非公開_コメントなし_then_False(self):
        nanitozo = Nanitozo.objects.create(
            air=self.air, user=self.user, good=True,
            comment_open=False,
            comment_recommend='',
            comment='',
            comment_negative='',
            created_at=self.created_at, updated_at=self.created_at,
        )
        self.assertEqual(nanitozo.has_comment(), False)

    def test_非公開_comment_recommendあり_then_False(self):
        nanitozo = Nanitozo.objects.create(
            air=self.air, user=self.user, good=True,
            comment_open=False,
            comment_recommend='あいうえお',
            comment='',
            comment_negative='',
            created_at=self.created_at, updated_at=self.created_at,
        )
        self.assertEqual(nanitozo.has_comment(), False)

    def test_非公開_感想あり_then_False(self):
        nanitozo = Nanitozo.objects.create(
            air=self.air, user=self.user, good=True,
            comment_open=False,
            comment_recommend='',
            comment='あいうえお',
            comment_negative='',
            created_at=self.created_at, updated_at=self.created_at,
        )
        self.assertEqual(nanitozo.has_comment(), False)

    def test_非公開_ネガコメあり_then_False(self):
        nanitozo = Nanitozo.objects.create(
            air=self.air, user=self.user, good=True,
            comment_open=False,
            comment_recommend='',
            comment='',
            comment_negative='あいうえお',
            created_at=self.created_at, updated_at=self.created_at,
        )
        self.assertEqual(nanitozo.has_comment(), False)

    def test_公開_コメントなし_then_False(self):
        nanitozo = Nanitozo.objects.create(
            air=self.air, user=self.user, good=True,
            comment_open=True,
            comment_recommend='',
            comment='',
            comment_negative='',
            created_at=self.created_at, updated_at=self.created_at,
        )
        self.assertEqual(nanitozo.has_comment(), False)

    def test_公開_comment_recommendあり_then_True(self):
        nanitozo = Nanitozo.objects.create(
            air=self.air, user=self.user, good=True,
            comment_open=True,
            comment_recommend='あいうえお',
            comment='',
            comment_negative='',
            created_at=self.created_at, updated_at=self.created_at,
        )
        self.assertEqual(nanitozo.has_comment(), True)

    def test_公開_感想あり_then_True(self):
        nanitozo = Nanitozo.objects.create(
            air=self.air, user=self.user, good=True,
            comment_open=True,
            comment_recommend='',
            comment='あいうえお',
            comment_negative='',
            created_at=self.created_at, updated_at=self.created_at,
        )
        self.assertEqual(nanitozo.has_comment(), True)

    def test_公開_ネガコメあり_then_True(self):
        nanitozo = Nanitozo.objects.create(
            air=self.air, user=self.user, good=True,
            comment_open=True,
            comment_recommend='',
            comment='',
            comment_negative='あいうえお',
            created_at=self.created_at, updated_at=self.created_at,
        )
        self.assertEqual(nanitozo.has_comment(), True)


class NanitozoModelObjectsTests(TestCase):

    def setUp(self):
        self.user1 = create_user('test1', 'test1@test.com', 't11111', 'ABC')
        self.user2 = create_user('test2', 'test2@test.com', 't22222', 'BCD')
        self.user3 = create_user('test3', 'test3@test.com', 't33333', 'CDE')
        self.air1 = create_airs('放送1', 1)
        self.air2 = create_airs('放送2', 2)
        self.air3 = create_airs('放送3', 3)
        self.air4 = create_airs('放送4', 4)
        self.air5 = create_airs('放送5', 5)

    def test_データなし(self):
        # 新着
        list = Nanitozo.objects.all()
        self.assertEqual(len(list), 0)
        # 自分の
        self_list = Nanitozo.objects_self.get(None)
        self.assertEqual(len(self_list), 0)
        # 下書き
        close_list = Nanitozo.objects_close.get(None)
        self.assertEqual(len(close_list), 0)

    def test_放送1つに3人で公開何卒(self):
        created_at = timezone.now() + datetime.timedelta(days=-1, hours=-1)
        create_nanitozo(self.air1, self.user1, False, True, created_at)
        created_at = timezone.now() + datetime.timedelta(days=-2, hours=-1)
        create_nanitozo(self.air1, self.user2, False, True, created_at)
        created_at = timezone.now() + datetime.timedelta(days=-3, hours=-1)
        create_nanitozo(self.air1, self.user3, False, True, created_at)

        # 新着
        list = Nanitozo.objects.all()
        self.assertEqual(len(list), 3)
        # 自分の
        self_list = Nanitozo.objects_self.get(self.user1)
        self.assertEqual(len(self_list), 1)
        # 下書き
        close_list = Nanitozo.objects_close.get(self.user1)
        self.assertEqual(len(close_list), 0)

    def test_放送1つに3人で下書き何卒(self):
        created_at = timezone.now() + datetime.timedelta(days=-1, hours=-1)
        create_nanitozo(self.air1, self.user1, False, False, created_at)
        created_at = timezone.now() + datetime.timedelta(days=-2, hours=-1)
        create_nanitozo(self.air1, self.user2, False, False, created_at)
        created_at = timezone.now() + datetime.timedelta(days=-3, hours=-1)
        create_nanitozo(self.air1, self.user3, False, False, created_at)

        # 新着
        list = Nanitozo.objects.all()
        self.assertEqual(len(list), 3)
        # 自分の
        self_list = Nanitozo.objects_self.get(self.user1)
        self.assertEqual(len(self_list), 1)
        # 下書き
        close_list = Nanitozo.objects_close.get(self.user1)
        self.assertEqual(len(close_list), 1)
