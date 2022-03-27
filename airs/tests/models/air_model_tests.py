import datetime

from django.test import TestCase
from django.utils import timezone

from ...models import Air

class AirModelTests(TestCase):

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

