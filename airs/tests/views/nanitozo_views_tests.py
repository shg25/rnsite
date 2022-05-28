import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from ...models import Air

UserModel = get_user_model()


def create_air(name, started_at, ended_at):
    return Air.objects.create(name=name, started_at=started_at, ended_at=ended_at)


class NanitozoLoginRequiredViewByGuestTests(TestCase):

    def setUp(self):
        # 4日前の1時間番組
        started = timezone.now() + datetime.timedelta(days=-7, hours=-1)
        ended = timezone.now() + datetime.timedelta(days=-7)
        self.air = create_air('酒井健太ANN0', started, ended)

        nanitozo_user = UserModel.objects.create(username='test', email='test@test.com', password='123456', last_name='ABC')
        self.setted_nanitozo = self.air.nanitozo_set.create(user=nanitozo_user)

    def test_何卒登録(self):
        url = reverse('airs:nanitozo_create', args=(self.air.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_何卒取消(self):
        url = reverse('airs:nanitozo_delete', args=(self.air.id, self.setted_nanitozo.id))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_感想更新(self):
        url = reverse('airs:nanitozo_update', args=(self.air.id, self.setted_nanitozo.id))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_感想更新(self):
        url = reverse('airs:nanitozo_update', args=(self.air.id, self.setted_nanitozo.id))
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_満足(self):
        url = reverse('airs:nanitozo_apply_good', args=(self.air.id, self.setted_nanitozo.id))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_満足取消(self):
        url = reverse('airs:nanitozo_cancel_good', args=(self.air.id, self.setted_nanitozo.id))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


class NanitozoCreateTests(TestCase):
    def setUp(self):
        # 4日前の1時間番組
        started = timezone.now() + datetime.timedelta(days=-7, hours=-1)
        ended = timezone.now() + datetime.timedelta(days=-7)
        self.air = create_air('酒井健太ANN0', started, ended)

    def test_何卒登録(self):
        # ログイン
        self.user = UserModel.objects.create(username='test', email='test@test.com', password='123456', last_name='ABC')
        self.client.force_login(self.user)

        # 何卒登録
        url = reverse('airs:nanitozo_create', args=(self.air.id,))
        response = self.client.get(url)

        # 自分自身の何卒が1件あるはず
        air = Air.objects.get(pk=self.air.id)
        nanitozo_list = air.nanitozo_set.all()
        my_nanitozo_list = list(filter(lambda x: x.user == self.user, nanitozo_list))
        self.assertEqual(len(my_nanitozo_list), 1)
        self.assertEqual(response.status_code, 302)


class NanitozoDeleteTests(TestCase):

    def setUp(self):
        # 4日前の1時間番組
        started = timezone.now() + datetime.timedelta(days=-7, hours=-1)
        ended = timezone.now() + datetime.timedelta(days=-7)
        self.air = create_air('酒井健太ANN0', started, ended)

        # ログイン
        self.user = UserModel.objects.create(username='test', email='test@test.com', password='123456', last_name='ABC')
        self.client.force_login(self.user)

        # 何卒登録（通常の何卒登録と同じくairとuser以外は初期値）
        self.air.nanitozo_set.create(user=self.user)

        # 登録した何卒を保持
        self.my_nanitozo = self.air.nanitozo_set.filter(user=self.user).first()

    def test_何卒取消(self):
        # 何卒を取り消す
        url = reverse('airs:nanitozo_delete', args=(self.air.id, self.my_nanitozo.id))
        response = self.client.get(url)

        # 自分自身の何卒がないはず
        air = Air.objects.get(pk=self.air.id)
        my_nanitozo = air.nanitozo_set.filter(user=self.user).first()
        self.assertEqual(my_nanitozo, None)

        self.assertEqual(response.status_code, 302)


class NanitozoUpdateTests(TestCase):

    def setUp(self):
        # ログインしておく（ログインしない処理は別途記載）
        self.user = UserModel.objects.create(username='test', email='test@test.com', password='123456', last_name='ABC')
        self.client.force_login(self.user)

        # 4日前の1時間番組
        started = timezone.now() + datetime.timedelta(days=-7, hours=-1)
        ended = timezone.now() + datetime.timedelta(days=-7)
        self.air = create_air('酒井健太ANN0', started, ended)

        # 何卒登録（通常の何卒登録と同じくairとuser以外は初期値）
        self.air.nanitozo_set.create(user=self.user)

        # 登録した何卒を保持
        self.my_nanitozo = self.air.nanitozo_set.filter(user=self.user).first()

    def test_感想編集_get_then_405(self):
        url = reverse('airs:nanitozo_update', args=(self.air.id, self.my_nanitozo.id))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_感想編集_post_内容ナシ_対象の項目が空になる(self):
        data = {}
        url = reverse('airs:nanitozo_update', args=(self.air.id, self.my_nanitozo.id))
        response = self.client.post(url, data)

        # 対象のカラムを空にするとデータも空になる
        air = Air.objects.get(pk=self.air.id)
        my_nanitozo = air.nanitozo_set.filter(user=self.user).first()

        self.assertEqual(my_nanitozo.comment_open, False)  # boolはFlaseになる → NOTE 処理で空の場合はブロックするべき？
        self.assertEqual(my_nanitozo.comment_recommend, '')
        self.assertEqual(my_nanitozo.comment, '')
        self.assertEqual(my_nanitozo.comment_negative, '')
        self.assertEqual(response.status_code, 302)

    def test_感想編集_post_想定通りのフィールド名(self):
        data = {
            'comment_open': False,
            'comment_recommend': '推薦文を更新した',
            'comment': '感想文を更新した',
            'comment_negative': 'ネガを更新した',
        }
        url = reverse('airs:nanitozo_update', args=(self.air.id, self.my_nanitozo.id))
        response = self.client.post(url, data)

        # 更新成功の確認
        air = Air.objects.get(pk=self.air.id)
        my_nanitozo = air.nanitozo_set.filter(user=self.user).first()

        self.assertEqual(my_nanitozo.comment_open, False)
        self.assertEqual(my_nanitozo.comment_recommend, '推薦文を更新した')
        self.assertEqual(my_nanitozo.comment, '感想文を更新した')
        self.assertEqual(my_nanitozo.comment_negative, 'ネガを更新した')

        self.assertEqual(response.status_code, 302)

    def test_感想編集_post_想定外のフィールド名(self):
        data = {
            'good': True,
            'comment_open': True,
            'comment_recommend': '推薦文を更新した',
            'comment': '感想文を更新した',
            'comment_negative': 'ネガを更新した',
        }
        url = reverse('airs:nanitozo_update', args=(self.air.id, self.my_nanitozo.id))
        response = self.client.post(url, data)

        air = Air.objects.get(pk=self.air.id)
        my_nanitozo = air.nanitozo_set.filter(user=self.user).first()

        # goodは対象外なので変わらない
        self.assertEqual(my_nanitozo.good, False)
        self.assertEqual(my_nanitozo.comment_open, True)
        self.assertEqual(my_nanitozo.comment_recommend, '推薦文を更新した')
        self.assertEqual(my_nanitozo.comment, '感想文を更新した')
        self.assertEqual(my_nanitozo.comment_negative, 'ネガを更新した')

        self.assertEqual(response.status_code, 302)

    def test_感想編集_post_別ユーザー(self):
        # 別ユーザーでログイン
        self.user = UserModel.objects.create(username='test2', email='test2@test.com', password='123456', last_name='BCD')
        self.client.force_login(self.user)

        data = {}
        url = reverse('airs:nanitozo_update', args=(self.air.id, self.my_nanitozo.id))
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 403)


class NanitozoGoodApplyCancelTests(TestCase):

    def setUp(self):
        # ログインしておく（ログインしない処理は別途記載）
        self.user = UserModel.objects.create(username='test', email='test@test.com', password='123456', last_name='ABC')
        self.client.force_login(self.user)

        # 4日前の1時間番組
        started = timezone.now() + datetime.timedelta(days=-7, hours=-1)
        ended = timezone.now() + datetime.timedelta(days=-7)
        self.air = create_air('酒井健太ANN0', started, ended)

        # 何卒登録（通常の何卒登録と同じくairとuser以外は初期値）
        self.air.nanitozo_set.create(user=self.user)

        # 登録した何卒を保持
        self.my_nanitozo = self.air.nanitozo_set.filter(user=self.user).first()

    def test_満足からの満足取り消し(self):
        self.assertEqual(self.my_nanitozo.good, False)

        # 満足
        url = reverse('airs:nanitozo_apply_good', args=(self.air.id, self.my_nanitozo.id))
        response = self.client.get(url)

        air = Air.objects.get(pk=self.air.id)
        my_nanitozo = air.nanitozo_set.filter(user=self.user).first()
        self.assertEqual(my_nanitozo.good, True)
        self.assertEqual(response.status_code, 302)

        # 取消
        url = reverse('airs:nanitozo_cancel_good', args=(self.air.id, self.my_nanitozo.id))
        response = self.client.get(url)

        air = Air.objects.get(pk=self.air.id)
        my_nanitozo = air.nanitozo_set.filter(user=self.user).first()
        self.assertEqual(my_nanitozo.good, False)
        self.assertEqual(response.status_code, 302)

    def test_満足_get_別ユーザー(self):
        # 別ユーザーでログイン
        self.user = UserModel.objects.create(username='test2', email='test2@test.com', password='123456', last_name='BCD')
        self.client.force_login(self.user)

        url = reverse('airs:nanitozo_apply_good', args=(self.air.id, self.my_nanitozo.id))
        response = self.client.get(url)

        # Guestの場合と同じ結果になってしまう TODO Viewを今のリダイレクト形式から変えたら書き換える
        self.assertEqual(response.status_code, 302)
