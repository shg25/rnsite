import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Air


class AirModelTests(TestCase):

    def test_was_aired_this_week_with_future_started(self):
        """
        現在日時と6日前を比較するとTrueになる
        """
        now = timezone.now()
        time = now + datetime.timedelta(days=-6)
        print("now: " + str(now))
        print("time: " + str(time))
        future_air = Air(started=time)
        self.assertIs(future_air.was_aired_this_week(), True)
