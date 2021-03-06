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
        self.assertNotContains(response, '感想編集')

    def test_連絡詳細_ログインして何卒してない(self):
        # ログイン
        self.user = UserModel.objects.create(username='test', email='test@test.com', password='123456', last_name='ABC')
        self.client.force_login(self.user)

        url = reverse('airs:detail', args=(self.air.id,))
        response = self.client.get(url)

        self.assertContains(response, self.air.name)
        self.assertContains(response, '+放送登録')
        self.assertContains(response, 'ABC')
        self.assertNotContains(response, '感想編集')

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
        self.assertContains(response, '感想編集')


class AirUpdateTests(TestCase):

    def setUp(self):
        started = timezone.now() + datetime.timedelta(days=-7, hours=-1)
        ended = timezone.now() + datetime.timedelta(days=-7)
        self.air = Air.objects.create(
            name='酒井健太ANN0',
            started_at=started,
            ended_at=ended,
            overview_before='事前告知の初期値',
            overview_after='放送内容の初期値',
        )

    def test_連絡概要編集_get_ゲスト_then_302(self):
        url = reverse('airs:air_update', args=(self.air.id,))
        response = self.client.get(url)
        # [login_required]で処理前に弾かれる
        self.assertEqual(response.status_code, 302)

    def test_連絡概要編集_post_ゲスト_then_302(self):
        url = reverse('airs:air_update', args=(self.air.id,))
        response = self.client.post(url, {})
        # [login_required]で処理前に弾かれる
        self.assertEqual(response.status_code, 302)

    def test_連絡概要編集_get_then_405(self):
        # ログイン
        self.user = UserModel.objects.create(username='test', email='test@test.com', password='123456', last_name='ABC')
        self.client.force_login(self.user)

        url = reverse('airs:air_update', args=(self.air.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_連絡概要編集_post_内容ナシ_対象の項目が空になる(self):
        # ログイン
        self.user = UserModel.objects.create(username='test', email='test@test.com', password='123456', last_name='ABC')
        self.client.force_login(self.user)

        # この時点では初期値が取得できる
        air = Air.objects.get(pk=self.air.id)
        self.assertEqual(air.overview_before, '事前告知の初期値')
        self.assertEqual(air.overview_after, '放送内容の初期値')

        data = {}
        url = reverse('airs:air_update', args=(self.air.id,))
        response = self.client.post(url, data)

        # 対象のカラムを空にするとデータも空になる
        air = Air.objects.get(pk=self.air.id)
        self.assertEqual(air.overview_before, '')
        self.assertEqual(air.overview_after, '')

        self.assertEqual(response.status_code, 302)

    def test_連絡概要編集_post_想定通りのフィールド名(self):
        # ログイン
        self.user = UserModel.objects.create(username='test', email='test@test.com', password='123456', last_name='ABC')
        self.client.force_login(self.user)

        data = {
            'overview_before': '事前告知を更新した',
            'overview_after': '放送内容を更新した'
        }
        url = reverse('airs:air_update', args=(self.air.id,))
        response = self.client.post(url, data)

        # 更新成功の確認
        air = Air.objects.get(pk=self.air.id)
        self.assertEqual(air.overview_before, '事前告知を更新した')
        self.assertEqual(air.overview_after, '放送内容を更新した')

        self.assertEqual(response.status_code, 302)

    def test_連絡概要編集_post_想定外のフィールド名(self):
        # ログイン
        self.user = UserModel.objects.create(username='test', email='test@test.com', password='123456', last_name='ABC')
        self.client.force_login(self.user)

        data = {
            'name': '名前をPOSTしてみる',
            'overview_before': '事前告知を更新した',
            'overview_after': '放送内容を更新した'
        }
        url = reverse('airs:air_update', args=(self.air.id,))
        response = self.client.post(url, data)

        # nameは対象外なので変わらない
        air = Air.objects.get(pk=self.air.id)
        self.assertNotEqual(air.name, '名前をPOSTしてみる')
        self.assertEqual(air.name, '酒井健太ANN0')
        self.assertEqual(air.overview_before, '事前告知を更新した')
        self.assertEqual(air.overview_after, '放送内容を更新した')

        self.assertEqual(response.status_code, 302)
