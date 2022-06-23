import datetime

from django.test import TestCase
from django.utils import timezone

from ...models import Air, Broadcaster, Program


class AirModelUnNanitozoThisWeekTests(TestCase):
    def setUp(self):
        self.broadcaster_a = Broadcaster(name='放送局A')
        self.broadcaster_b = Broadcaster(name='放送局B')
        self.program_a = Program(name='番組A')
        self.program_b = Program(name='番組B')

        self.now = timezone.now()

        time = self.now + datetime.timedelta(days=-10)
        self.future_air = Air(
            broadcaster=self.broadcaster_a,
            name='テスト放送',
            started_at=time
        )
        # print('time: ' + str(time))

    def test_同じ曜日_同じ時分_同じ放送局_違う放送名_then_False(self):
        list = [
            Air(
                broadcaster=self.broadcaster_a,
                name='今週のテスト放送',
                started_at=self.now + datetime.timedelta(days=-3)
            )
        ]
        # print('item: ' + str(list[0].started_at))
        self.assertIs(self.future_air.un_nanitozo_this_week(list), False)

    def test_同じ曜日_同じ時分_違う放送局_違う放送名_then_True(self):
        list = [
            Air(
                broadcaster=self.broadcaster_b,  # ←ここ
                name='今週のテスト放送',
                started_at=self.now + datetime.timedelta(days=-3)
            )
        ]
        # print('item: ' + str(list[0].started_at))
        self.assertIs(self.future_air.un_nanitozo_this_week(list), True)

    def test_同じ曜日_違う時分_同じ放送局_同じ放送名_then_False(self):
        list = [
            Air(
                broadcaster=self.broadcaster_a,
                name='テスト放送',
                started_at=self.now + datetime.timedelta(days=-3, hours=+1)
            )
        ]
        # print('item: ' + str(list[0].started_at))
        self.assertIs(self.future_air.un_nanitozo_this_week(list), False)

    def test_今週の放送がゼロ_then_True(self):
        list = []
        self.assertIs(self.future_air.un_nanitozo_this_week(list), True)


class AirModelAiredAtTests(TestCase):

    def test_was_aired_this_week_with_future_started(self):
        """
        現在日時より未来の場合はFalse
        """
        now = timezone.now()
        time = now + datetime.timedelta(days=1)
        # 確認
        # print("now : " + str(now))
        # print("time: " + str(time))
        future_air = Air(started_at=time)
        self.assertIs(future_air.was_aired_this_week(), False)

    def test_was_aired_this_week_with_old_started(self):
        """
        現在日時から1週間以上前の場合はFalse
        """
        now = timezone.now()
        time = now + datetime.timedelta(days=-7)
        # time = now + datetime.timedelta(days=-7, seconds=-1)
        # 確認
        # print("now : " + str(now))
        # print("time: " + str(time))
        old_air = Air(started_at=time)
        self.assertIs(old_air.was_aired_this_week(), False)

    def test_was_aired_this_week_with_week1_started(self):
        """
        現在日時から1週間以内の場合はTrue
        """
        now = timezone.now()
        # time = now + datetime.timedelta(days=-7)
        time = now + datetime.timedelta(days=-6, hours=-23, minutes=-59, seconds=-59)
        # 確認
        # print("now : " + str(now))
        # print("time: " + str(time))
        recent_air = Air(started_at=time)
        self.assertIs(recent_air.was_aired_this_week(), True)


def create_air(broadcaster, name, started_at, ended_at):
    return Air.objects.create(broadcaster=broadcaster, name=name, started_at=started_at, ended_at=ended_at)


class AirModelObjectsTests(TestCase):

    def setUp(self):
        self.broadcaster1 = Broadcaster.objects.create(radiko_identifier='BUN1', name='文化放送')
        self.broadcaster2 = Broadcaster.objects.create(radiko_identifier='BUN2', name='大文化放送')
        self.broadcaster3 = Broadcaster.objects.create(radiko_identifier='BUN3', name='超文化放送')

    def test_データなし(self):
        list = Air.objects_two_week.all()
        self.assertEqual(len(list), 0)

    def test_今週の放送が1件(self):
        # 4日前の1時間番組
        started = timezone.now() + datetime.timedelta(days=-4, hours=-1)
        ended = timezone.now() + datetime.timedelta(days=-4)
        air = create_air(self.broadcaster1, '酒井健太ANN0', started, ended)

        list = Air.objects_two_week.all()
        self.assertEqual(len(list), 1)
        self.assertEqual(list[0].name, air.name)

    def test_未来の放送が1件と今週の放送が1件(self):
        # 4日後の1時間放送
        started1 = timezone.now() + datetime.timedelta(days=4, hours=-1)
        ended1 = timezone.now() + datetime.timedelta(days=4)
        air1 = create_air(self.broadcaster2, '赤もみじANN0', started1, ended1)

        # 4日前の1時間放送
        started2 = timezone.now() + datetime.timedelta(days=-4, hours=-1)
        ended2 = timezone.now() + datetime.timedelta(days=-4)
        air2 = create_air(self.broadcaster1, '酒井健太ANN0', started2, ended2)

        list = Air.objects_two_week.all()
        self.assertEqual(len(list), 2)
        self.assertEqual(list[0].name, air1.name)
        self.assertEqual(list[1].name, air2.name)

    def test_今週の放送が1件と先週の放送が1件(self):
        # 12日前の1時間番組
        started1 = timezone.now() + datetime.timedelta(days=-12, hours=-1)
        ended1 = timezone.now() + datetime.timedelta(days=-12)
        air1 = create_air(self.broadcaster1, '酒井健太ANN0', started1, ended1)

        # 4日前の1時間番組
        started2 = timezone.now() + datetime.timedelta(days=-4, hours=-1)
        ended2 = timezone.now() + datetime.timedelta(days=-4)
        air2 = create_air(self.broadcaster2, '赤もみじANN0', started2, ended2)

        list = Air.objects_two_week.all()
        self.assertEqual(len(list), 2)
        self.assertEqual(list[0].name, air2.name)
        self.assertEqual(list[1].name, air1.name)

    def test_放送局と開始日時で放送を検索(self):
        # 12日前の1時間番組
        started1 = timezone.now() + datetime.timedelta(days=-12, hours=-1)
        ended1 = timezone.now() + datetime.timedelta(days=-12)
        create_air(self.broadcaster1, '酒井健太ANN0', started1, ended1)

        # 4日前の1時間番組
        started2 = timezone.now() + datetime.timedelta(days=-4, hours=-1)
        ended2 = timezone.now() + datetime.timedelta(days=-4)
        create_air(self.broadcaster2, '赤もみじANN0', started2, ended2)

        # ↑と同じ時間の他局
        air3 = create_air(self.broadcaster3, 'ネガポジ2', started2, ended2)

        saved_air = Air.objects_identification.get(self.broadcaster3, started2).first()
        self.assertEqual(saved_air.name, air3.name)
