import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from ...models import Air

UserModel = get_user_model()


def create_air(name, started_at, ended_at):
    return Air.objects.create(name=name, started_at=started_at, ended_at=ended_at)


class AirIndexViewTests(TestCase):
    def test_データなし(self):
        response = self.client.get(reverse('airs:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '今週なし')
        self.assertContains(response, '先週なし')
        self.assertQuerysetEqual(response.context['this_week_list'], [])
        self.assertQuerysetEqual(response.context['last_week_list'], [])

    def test_今週の放送が1件(self):
        # 4日前の1時間番組
        started = timezone.now() + datetime.timedelta(days=-4, hours=-1)
        ended = timezone.now() + datetime.timedelta(days=-4)
        air = create_air('酒井健太ANN0', started, ended)

        response = self.client.get(reverse('airs:index'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '今週なし')
        self.assertContains(response, '先週なし')
        self.assertQuerysetEqual(response.context['this_week_list'], [air], transform=lambda x: x)  # 「transform=lambda x: x」はおまじない的な
        self.assertQuerysetEqual(response.context['last_week_list'], [])

    def test_未来の放送が1件と今週の放送が1件(self):
        # 4日後の1時間放送
        started1 = timezone.now() + datetime.timedelta(days=4, hours=-1)
        ended1 = timezone.now() + datetime.timedelta(days=4)
        air1 = create_air('赤もみじANN0', started1, ended1)

        # 4日前の1時間放送
        started2 = timezone.now() + datetime.timedelta(days=-4, hours=-1)
        ended2 = timezone.now() + datetime.timedelta(days=-4)
        air2 = create_air('酒井健太ANN0', started2, ended2)

        response = self.client.get(reverse('airs:index'))
        self.assertNotContains(response, '今週なし')
        self.assertContains(response, '先週なし')
        self.assertQuerysetEqual(response.context['this_week_list'], [air1, air2], transform=lambda x: x)  # 「transform=lambda x: x」はおまじない的な
        self.assertQuerysetEqual(response.context['last_week_list'], [])

    def test_今週の放送が1件と先週の放送が1件(self):
        # 12日前の1時間番組
        started1 = timezone.now() + datetime.timedelta(days=-12, hours=-1)
        ended1 = timezone.now() + datetime.timedelta(days=-12)
        air1 = create_air('酒井健太ANN0', started1, ended1)

        # 4日前の1時間番組
        started2 = timezone.now() + datetime.timedelta(days=-4, hours=-1)
        ended2 = timezone.now() + datetime.timedelta(days=-4)
        air2 = create_air('赤もみじANN0', started2, ended2)

        response = self.client.get(reverse('airs:index'))
        self.assertNotContains(response, '今週なし')
        self.assertNotContains(response, '先週なし')
        self.assertQuerysetEqual(response.context['this_week_list'], [air2], transform=lambda x: x)  # 「transform=lambda x: x」はおまじない的な
        self.assertQuerysetEqual(response.context['last_week_list'], [air1], transform=lambda x: x)  # 「transform=lambda x: x」はおまじない的な


class AirDetailViewTests(TestCase):

    def setUp(self):
        started = timezone.now() + datetime.timedelta(days=-7, hours=-1)
        ended = timezone.now() + datetime.timedelta(days=-7)
        self.air = create_air('酒井健太ANN0', started, ended)

    def test_連絡詳細_ゲスト(self):
        url = reverse('airs:detail', args=(self.air.id,))
        response = self.client.get(url)

        self.assertContains(response, self.air.name)
        self.assertNotContains(response, '+放送登録')
        self.assertNotContains(response, '何卒編集')

    def test_連絡詳細_ログインして何卒してない(self):
        # ログイン
        self.user = UserModel.objects.create(username='test', email='test@test.com', password='123456', last_name='ABC')
        self.client.force_login(self.user)

        url = reverse('airs:detail', args=(self.air.id,))
        response = self.client.get(url)

        self.assertContains(response, self.air.name)
        self.assertContains(response, '+放送登録')
        self.assertContains(response, 'ABC')
        self.assertNotContains(response, '何卒編集')

    def test_連絡詳細_ログインして何卒した(self):
        # ログイン
        self.user = UserModel.objects.create(username='test', email='test@test.com', password='123456', last_name='ABC')
        self.client.force_login(self.user)

        # 登録した放送に何卒
        self.air.nanitozo_set.create(user=self.user)

        url = reverse('airs:detail', args=(self.air.id,))
        response = self.client.get(url)

        self.assertContains(response, self.air.name)
        self.assertContains(response, '+放送登録')
        self.assertContains(response, 'ABC')
        self.assertContains(response, '何卒編集')
