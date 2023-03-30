import datetime
import json

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import make_aware
from django.urls import reverse

from ...models import FormattedName, Broadcaster, Program, Air
from ...views.air_views import pickRadikoUrlFromShareText, pickAirFromRadikoPageTitle, pickAirFromRadikoPageTitleApi, air_create_by_title

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
        url = self.air.get_absolute_url()
        response = self.client.get(url)

        self.assertContains(response, self.air.name)
        self.assertNotContains(response, '+放送登録')
        self.assertNotContains(response, '満足何卒？')
        self.assertNotContains(response, '何卒？')
        self.assertNotContains(response, '感想編集')

    def test_連絡詳細_ログインして何卒してない(self):
        # ログイン
        self.user = UserModel.objects.create(username='test', email='test@test.com', password='123456', last_name='ABC')
        self.client.force_login(self.user)

        url = self.air.get_absolute_url()
        response = self.client.get(url)

        self.assertContains(response, self.air.name)
        self.assertContains(response, '+放送登録')
        self.assertContains(response, 'ABC')
        self.assertContains(response, '満足何卒？')
        self.assertContains(response, '何卒？')
        self.assertNotContains(response, '感想編集')

    def test_連絡詳細_ログインして何卒した(self):
        # ログイン
        self.user = UserModel.objects.create(username='test', email='test@test.com', password='123456', last_name='ABC')
        self.client.force_login(self.user)

        # 登録した放送に何卒
        self.air.nanitozo_set.create(user=self.user)

        url = self.air.get_absolute_url()
        response = self.client.get(url)

        self.assertContains(response, self.air.name)
        self.assertContains(response, '+放送登録')
        self.assertContains(response, 'ABC')
        self.assertNotContains(response, '満足何卒？')
        self.assertNotContains(response, '何卒？')
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


class PickRadikoUrlFromShareTextTest(TestCase):

    def test_一般的な処理(self):
        share_text = 'オードリーのオールナイトニッポン | ニッポン放送 | 2023/02/04/土  25:00-27:00 https://radiko.jp/share/?sid=LFR&t=20230205010000'
        result = pickRadikoUrlFromShareText(share_text)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['radiko_url'], 'https://radiko.jp/share/?sid=LFR&t=20230205010000')

    def test_間違って2つペーストしたとかでURLが2つ含まれている場合は先のURLを取得(self):
        share_text = '沈黙の金曜日 | FM FUJI | 2023/02/03/金  21:00-23:00 https://radiko.jp/share/?sid=FM-FUJI&t=20230203210000 オードリーのオールナイトニッポン | ニッポン放送 | 2023/02/04/土  25:00-27:00 https://radiko.jp/share/?sid=LFR&t=20230205010000'
        result = pickRadikoUrlFromShareText(share_text)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['radiko_url'], 'https://radiko.jp/share/?sid=FM-FUJI&t=20230203210000')

    def test_3つURLがあったとしてradikoのURLだけを取得して先にセットしたほうを取得(self):
        share_text = '1つめ（not radiko） https://twitter.com/home 2つめ（radiko） https://radiko.jp/share/?sid=FM-FUJI&t=20230203210000 3つめ（radiko） https://radiko.jp/share/?sid=LFR&t=20230205010000'
        result = pickRadikoUrlFromShareText(share_text)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['radiko_url'], 'https://radiko.jp/share/?sid=FM-FUJI&t=20230203210000')

    def test_URLが1つもない場合はfail(self):
        share_text = 'オードリーのオールナイトニッポン | ニッポン放送 | 2023/02/04/土  25:00-27:00'
        result = pickRadikoUrlFromShareText(share_text)
        self.assertEqual(result['status'], 'fail')
        self.assertEqual(result['data']['title'], 'URLが見つかりません')

    def test_radikoのURLが1つもない場合はfail(self):
        share_text = 'オードリーのオールナイトニッポン | ニッポン放送 | 2023/02/04/土  25:00-27:00 https://twitter.com/home'
        result = pickRadikoUrlFromShareText(share_text)
        self.assertEqual(result['status'], 'fail')
        self.assertEqual(result['data']['title'], 'radikoのURLが見つかりません')


class PickAirFromRadikoPageTitleTest(TestCase):

    def setUp(self):
        self.formattedNameProgram1 = FormattedName.objects.create(id=2, name='ｻｽﾍﾟﾝﾀﾞｰｽﾞのﾓｰﾌﾟｯｼｭ!!')
        self.formattedNameBroadcaster1 = FormattedName.objects.create(id=1, name='sbsﾗｼﾞｵ')

        program1 = Program.objects.create(name="サスペンダーズのモープッシュ！！")
        program1.formatted_names.set([self.formattedNameProgram1])
        self.program1 = program1

        broadcaster1 = Broadcaster.objects.create(radiko_identifier='SBS', name='SBSラジオ')
        broadcaster1.formatted_names.set([self.formattedNameBroadcaster1])
        self.broadcaster1 = broadcaster1

    def test_配信が終了した番組(self):
        title = 'この番組の配信は終了しました'
        result = pickAirFromRadikoPageTitle(title)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['message'], '配信が終了した放送\nどうにか登録したいならサイト管理者に相談を')

    def test_縦棒が3つない(self):
        title = '2023年1月29日（日）8:00～8:30  サスペンダーズのモープッシュ！！  SBSラジオ | radiko'
        result = pickAirFromRadikoPageTitle(title)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['message'], 'なぜかエラー！\n送信内容をサイト管理者に伝えてください')

    def test_全てのデータが揃っている場合(self):
        title = '2023年1月29日（日）8:00～8:30 | サスペンダーズのモープッシュ！！ | SBSラジオ | radiko'
        result = pickAirFromRadikoPageTitle(title)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['program_name'], 'サスペンダーズのモープッシュ！！')
        self.assertEqual(result['data']['program'], self.program1)
        self.assertEqual(result['data']['broadcaster'], self.broadcaster1)
        self.assertEqual(result['data']['started_at'], make_aware(datetime.datetime(2023, 1, 29, 8, 0)))
        self.assertEqual(result['data']['ended_at'], make_aware(datetime.datetime(2023, 1, 29, 8, 30)))

    def test_全てのデータが揃っている場合_24時から30分(self):
        title = '2023年1月29日（日）24:00～24:30 | サスペンダーズのモープッシュ！！ | SBSラジオ | radiko'
        result = pickAirFromRadikoPageTitle(title)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['program_name'], 'サスペンダーズのモープッシュ！！')
        self.assertEqual(result['data']['program'], self.program1)
        self.assertEqual(result['data']['broadcaster'], self.broadcaster1)
        self.assertEqual(result['data']['started_at'], make_aware(datetime.datetime(2023, 1, 30, 0, 0)))
        self.assertEqual(result['data']['ended_at'], make_aware(datetime.datetime(2023, 1, 30, 0, 30)))

    def test_全てのデータが揃っている場合_深夜4時から朝6時(self):
        title = '2023年1月29日（日）28:00～30:00 | サスペンダーズのモープッシュ！！ | SBSラジオ | radiko'
        result = pickAirFromRadikoPageTitle(title)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['program_name'], 'サスペンダーズのモープッシュ！！')
        self.assertEqual(result['data']['program'], self.program1)
        self.assertEqual(result['data']['broadcaster'], self.broadcaster1)
        self.assertEqual(result['data']['started_at'], make_aware(datetime.datetime(2023, 1, 30, 4, 0)))
        self.assertEqual(result['data']['ended_at'], make_aware(datetime.datetime(2023, 1, 30, 6, 0)))

    def test_存在しないprogramの場合_24時から30分(self):
        title = '2023年1月29日（日）24:00～24:30 | 存在しない番組名 | SBSラジオ | radiko'
        result = pickAirFromRadikoPageTitle(title)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['program_name'], '存在しない番組名')
        self.assertEqual(result['data']['program'], None)
        self.assertEqual(result['data']['broadcaster'], self.broadcaster1)
        self.assertEqual(result['data']['started_at'], make_aware(datetime.datetime(2023, 1, 30, 0, 0)))
        self.assertEqual(result['data']['ended_at'], make_aware(datetime.datetime(2023, 1, 30, 0, 30)))

    def test_存在しないbroadcasterの場合_24時から30分(self):
        title = '2023年1月29日（日）24:00～24:30 | サスペンダーズのモープッシュ！！ | 存在しないブロードキャスト | radiko'
        result = pickAirFromRadikoPageTitle(title)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['message'], '予想外の放送局名なのでエラー！\n送信内容をサイト管理者に伝えてください')

    def test_なぜか番組名がない(self):
        title = '2023年1月29日（日）24:00～24:30 || 存在しないブロードキャスト | radiko'
        result = pickAirFromRadikoPageTitle(title)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['message'], 'パースエラー！\n送信内容をサイト管理者に伝えてください')

    def test_なぜか終了時間が開始時間より早い時間になっている(self):
        title = '2023年1月29日（日）8:30～8:00 | サスペンダーズのモープッシュ！！ | SBSラジオ | radiko'
        result = pickAirFromRadikoPageTitle(title)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['message'], 'パースエラー！\n送信内容をサイト管理者に伝えてください')


class PickAirFromRadikoPageTitleApiTest(TestCase):

    def setUp(self):
        self.formattedNameProgram1 = FormattedName.objects.create(id=2, name='ｻｽﾍﾟﾝﾀﾞｰｽﾞのﾓｰﾌﾟｯｼｭ!!')
        self.formattedNameBroadcaster1 = FormattedName.objects.create(id=1, name='sbsﾗｼﾞｵ')

        program1 = Program.objects.create(name="サスペンダーズのモープッシュ！！")
        program1.formatted_names.set([self.formattedNameProgram1])
        self.program1 = program1

        broadcaster1 = Broadcaster.objects.create(radiko_identifier='SBS', name='SBSラジオ')
        broadcaster1.formatted_names.set([self.formattedNameBroadcaster1])
        self.broadcaster1 = broadcaster1

    def test_配信が終了した番組(self):
        title = 'この番組の配信は終了しました'
        result = pickAirFromRadikoPageTitleApi(title)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['message'], '配信が終了した放送\nどうにか登録したいならサイト管理者に相談を')

    def test_縦棒が3つない(self):
        title = '2023年1月29日（日）8:00～8:30  サスペンダーズのモープッシュ！！  SBSラジオ | radiko'
        result = pickAirFromRadikoPageTitleApi(title)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['message'], 'なぜかエラー！\n送信内容をサイト管理者に伝えてください')

    def test_全てのデータが揃っている場合(self):
        title = '2023年1月29日（日）8:00～8:30 | サスペンダーズのモープッシュ！！ | SBSラジオ | radiko'
        result = pickAirFromRadikoPageTitleApi(title)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['program_name'], 'サスペンダーズのモープッシュ！！')
        self.assertEqual(result['data']['program'], self.program1.name)
        self.assertEqual(result['data']['broadcaster'], self.broadcaster1.name)
        self.assertEqual(result['data']['started_at'], '2023/01/29 8:00')
        self.assertEqual(result['data']['ended_at'], '2023/01/29 8:30')
        self.assertEqual(result['data']['radiko_title'], title)

    def test_全てのデータが揃っている場合_24時から30分(self):
        title = '2023年1月29日（日）24:00～24:30 | サスペンダーズのモープッシュ！！ | SBSラジオ | radiko'
        result = pickAirFromRadikoPageTitleApi(title)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['program_name'], 'サスペンダーズのモープッシュ！！')
        self.assertEqual(result['data']['program'], self.program1.name)
        self.assertEqual(result['data']['broadcaster'], self.broadcaster1.name)
        self.assertEqual(result['data']['started_at'], '2023/01/30 24:00')
        self.assertEqual(result['data']['ended_at'], '2023/01/30 24:30')
        self.assertEqual(result['data']['radiko_title'], title)

    def test_全てのデータが揃っている場合_深夜4時から朝6時(self):
        title = '2023年1月29日（日）28:00～30:00 | サスペンダーズのモープッシュ！！ | SBSラジオ | radiko'
        result = pickAirFromRadikoPageTitleApi(title)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['program_name'], 'サスペンダーズのモープッシュ！！')
        self.assertEqual(result['data']['program'], self.program1.name)
        self.assertEqual(result['data']['broadcaster'], self.broadcaster1.name)
        self.assertEqual(result['data']['started_at'], '2023/01/30 28:00')
        self.assertEqual(result['data']['ended_at'], '2023/01/30 6:00')
        self.assertEqual(result['data']['radiko_title'], title)

    def test_存在しないprogramの場合_24時から30分(self):
        title = '2023年1月29日（日）24:00～24:30 | 存在しない番組名 | SBSラジオ | radiko'
        result = pickAirFromRadikoPageTitleApi(title)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['program_name'], '存在しない番組名')
        self.assertEqual(result['data']['program'], None)
        self.assertEqual(result['data']['broadcaster'], self.broadcaster1.name)
        self.assertEqual(result['data']['started_at'], '2023/01/30 24:00')
        self.assertEqual(result['data']['ended_at'], '2023/01/30 24:30')
        self.assertEqual(result['data']['radiko_title'], title)

    def test_存在しないbroadcasterの場合_24時から30分(self):
        title = '2023年1月29日（日）24:00～24:30 | サスペンダーズのモープッシュ！！ | 存在しないブロードキャスト | radiko'
        result = pickAirFromRadikoPageTitleApi(title)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['message'], '予想外の放送局名なのでエラー！\n送信内容をサイト管理者に伝えてください')

    def test_なぜか番組名がない(self):
        title = '2023年1月29日（日）24:00～24:30 || 存在しないブロードキャスト | radiko'
        result = pickAirFromRadikoPageTitleApi(title)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['message'], 'パースエラー！\n送信内容をサイト管理者に伝えてください')

    def test_なぜか終了時間が開始時間より早い時間になっている(self):
        title = '2023年1月29日（日）8:30～8:00 | サスペンダーズのモープッシュ！！ | SBSラジオ | radiko'
        result = pickAirFromRadikoPageTitleApi(title)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['message'], 'パースエラー！\n送信内容をサイト管理者に伝えてください')


class AirCreateByTitleForTestTest(TestCase):

    def setUp(self):
        self.formattedNameProgram1 = FormattedName.objects.create(id=2, name='ｻｽﾍﾟﾝﾀﾞｰｽﾞのﾓｰﾌﾟｯｼｭ!!')
        self.formattedNameBroadcaster1 = FormattedName.objects.create(id=1, name='sbsﾗｼﾞｵ')

        program1 = Program.objects.create(name="サスペンダーズのモープッシュ！！")
        program1.formatted_names.set([self.formattedNameProgram1])
        self.program1 = program1

        broadcaster1 = Broadcaster.objects.create(radiko_identifier='SBS', name='SBSラジオ')
        broadcaster1.formatted_names.set([self.formattedNameBroadcaster1])
        self.broadcaster1 = broadcaster1

        self.user = UserModel.objects.create(username='test', email='test@test.com', password='123456', last_name='ABC')
        self.client.force_login(self.user)

    def test_配信が終了した番組(self):
        title = 'この番組の配信は終了しました'
        params = {'radiko_title': title}
        response = self.client.post(reverse('airs:air_create_by_title'), params)
        request = response.wsgi_request

        result = air_create_by_title(request)

        result = json.loads(result.content)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['message'], '配信が終了した放送\nどうにか登録したいならサイト管理者に相談を')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), '配信が終了した放送\nどうにか登録したいならサイト管理者に相談を')

    def test_縦棒が3つない(self):
        title = '2023年1月29日（日）8:00～8:30  サスペンダーズのモープッシュ！！  SBSラジオ | radiko'
        params = {'radiko_title': title}
        response = self.client.post(reverse('airs:air_create_by_title'), params)
        request = response.wsgi_request

        result = air_create_by_title(request)

        result = json.loads(result.content)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['message'], 'なぜかエラー！\n送信内容をサイト管理者に伝えてください')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'なぜかエラー！\n送信内容をサイト管理者に伝えてください')

    def test_全てのデータが揃っている場合(self):
        title = '2023年1月29日（日）8:00～8:30 | サスペンダーズのモープッシュ！！ | SBSラジオ | radiko'
        params = {'radiko_title': title}
        response = self.client.post(reverse('airs:air_create_by_title'), params)
        request = response.wsgi_request

        result = air_create_by_title(request)

        result = json.loads(result.content)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['message'], '何卒処理まで完了')
        self.assertTrue(result['data']['next_url'].startswith('/'))
        self.assertTrue(result['data']['next_url'].endswith('/'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), '放送登録完了！')
        self.assertEqual(str(messages[1]), '何卒！')

    def test_登録済み_and_何卒済みの放送の場合(self):
        title = '2023年1月29日（日）8:00～8:30 | サスペンダーズのモープッシュ！！ | SBSラジオ | radiko'
        params = {'radiko_title': title}
        response = self.client.post(reverse('airs:air_create_by_title'), params)
        request = response.wsgi_request

        result = air_create_by_title(request)

        result = json.loads(result.content)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['message'], '何卒処理まで完了')
        self.assertTrue(result['data']['next_url'].startswith('/'))
        self.assertTrue(result['data']['next_url'].endswith('/'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), '放送登録完了！')
        self.assertEqual(str(messages[1]), '何卒！')

        # もう1回POSTする
        response = self.client.post(reverse('airs:air_create_by_title'), params)
        request = response.wsgi_request

        result = air_create_by_title(request)

        result = json.loads(result.content)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['message'], '何卒処理まで完了')
        self.assertTrue(result['data']['next_url'].startswith('/'))
        self.assertTrue(result['data']['next_url'].endswith('/'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[2]), '登録済みの放送')
        self.assertEqual(str(messages[3]), '何卒済みの放送')

    def test_存在しないprogramの場合_24時から30分(self):
        title = '2023年1月29日（日）24:00～24:30 | 存在しない番組名 | SBSラジオ | radiko'
        params = {'radiko_title': title}
        response = self.client.post(reverse('airs:air_create_by_title'), params)
        request = response.wsgi_request

        result = air_create_by_title(request)

        result = json.loads(result.content)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['data']['message'], '何卒処理まで完了')
        self.assertTrue(result['data']['next_url'].startswith('/'))
        self.assertTrue(result['data']['next_url'].endswith('/'))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), '放送登録完了！')
        self.assertEqual(str(messages[1]), '何卒！')

    def test_存在しないbroadcasterの場合_24時から30分(self):
        title = '2023年1月29日（日）24:00～24:30 | サスペンダーズのモープッシュ！！ | 存在しないブロードキャスト | radiko'
        params = {'radiko_title': title}
        response = self.client.post(reverse('airs:air_create_by_title'), params)
        request = response.wsgi_request

        result = air_create_by_title(request)

        result = json.loads(result.content)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['message'], '予想外の放送局名なのでエラー！\n送信内容をサイト管理者に伝えてください')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), '予想外の放送局名なのでエラー！\n送信内容をサイト管理者に伝えてください')

    def test_なぜか番組名がない(self):
        title = '2023年1月29日（日）24:00～24:30 || 存在しないブロードキャスト | radiko'
        params = {'radiko_title': title}
        response = self.client.post(reverse('airs:air_create_by_title'), params)
        request = response.wsgi_request

        result = air_create_by_title(request)

        result = json.loads(result.content)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['message'], 'パースエラー！\n送信内容をサイト管理者に伝えてください')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'パースエラー！\n送信内容をサイト管理者に伝えてください')

    def test_なぜか終了時間が開始時間より早い時間になっている(self):
        title = '2023年1月29日（日）8:30～8:00 | サスペンダーズのモープッシュ！！ | SBSラジオ | radiko'
        params = {'radiko_title': title}
        response = self.client.post(reverse('airs:air_create_by_title'), params)
        request = response.wsgi_request

        result = air_create_by_title(request)

        result = json.loads(result.content)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['message'], 'パースエラー！\n送信内容をサイト管理者に伝えてください')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'パースエラー！\n送信内容をサイト管理者に伝えてください')
