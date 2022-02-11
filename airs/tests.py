import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from pytz import timezone as pytztimezone  # TODO どこかにまとめる

from .models import Air, Program


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


def create_air(program_name, started_at, ended_at):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    create_program = Program.objects.create(name=program_name)
    return Air.objects.create(program=create_program, started_at=started_at, ended_at=ended_at)


class AirIndexViewTests(TestCase):
    def test_no_air(self):
        """
        If no airs exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('airs:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "何卒0(ZERO)")
        self.assertQuerysetEqual(response.context['latest_air_list'], [])

    def test_past_air(self):
        """
        Airs with a started in the past are displayed on the index page.
        """
        started = timezone.now() + datetime.timedelta(days=-7, hours=-1)
        ended = timezone.now() + datetime.timedelta(days=-7)
        create_air(program_name="酒井健太ANN0", started_at=started, ended_at=ended)

        response = self.client.get(reverse('airs:index'))
        self.assertEqual(response.status_code, 200)

        startedstr = str(started.astimezone(pytztimezone('Asia/Tokyo')))
        self.assertQuerysetEqual(response.context['latest_air_list'], ['<Air: 酒井健太ANN0 ' + startedstr + '>'])

    def test_future_air(self):
        """
        Airs with a started in the future aren't displayed on the index page.
        """
        started = timezone.now() + datetime.timedelta(days=7, hours=-1)
        ended = timezone.now() + datetime.timedelta(days=7)
        create_air(program_name="赤もみじANN0", started_at=started, ended_at=ended)
        response = self.client.get(reverse('airs:index'))
        self.assertContains(response, "何卒0(ZERO)")
        self.assertQuerysetEqual(response.context['latest_air_list'], [])

    def test_future_question_and_past_air(self):
        """
        Even if both past and future airs exist, only past airs are displayed.
        """
        startedpast = timezone.now() + datetime.timedelta(days=-7, hours=-1)
        endedpast = timezone.now() + datetime.timedelta(days=-7)
        create_air(program_name="酒井健太ANN0", started_at=startedpast, ended_at=endedpast)

        startedfuture = timezone.now() + datetime.timedelta(days=7, hours=-1)
        endedfuture = timezone.now() + datetime.timedelta(days=7)
        create_air(program_name="赤もみじANN0", started_at=startedfuture, ended_at=endedfuture)

        response = self.client.get(reverse('airs:index'))
        startedstr = str(startedpast.astimezone(pytztimezone('Asia/Tokyo')))
        self.assertQuerysetEqual(response.context['latest_air_list'], ['<Air: 酒井健太ANN0 ' + startedstr + '>'])

    def test_two_past_airs(self):
        """
        The questions index page may display multiple questions.
        """
        startedpast7 = timezone.now() + datetime.timedelta(days=-7, hours=-1)
        endedpast7 = timezone.now() + datetime.timedelta(days=-7)
        create_air(program_name="酒井健太ANN0", started_at=startedpast7, ended_at=endedpast7)

        startedpast6 = timezone.now() + datetime.timedelta(days=-6, hours=-1)
        endedpast6 = timezone.now() + datetime.timedelta(days=-6)
        create_air(program_name="赤もみじANN0", started_at=startedpast6, ended_at=endedpast6)

        response = self.client.get(reverse('airs:index'))

        startedpast7str = str(startedpast7.astimezone(pytztimezone('Asia/Tokyo')))
        startedpast6str = str(startedpast6.astimezone(pytztimezone('Asia/Tokyo')))
        self.assertQuerysetEqual(
            response.context['latest_air_list'],
            ['<Air: 赤もみじANN0 ' + startedpast6str + '>', '<Air: 酒井健太ANN0 ' + startedpast7str + '>']
        )


class AirDetailViewTests(TestCase):
    def test_future_air(self):
        """
        The detail view of a air with a started in the future returns a 404 not found.
        """
        startedfuture = timezone.now() + datetime.timedelta(days=7, hours=-1)
        endedfuture = timezone.now() + datetime.timedelta(days=7)
        future_air = create_air(program_name="赤もみじANN0", started_at=startedfuture, ended_at=endedfuture)

        url = reverse('airs:detail', args=(future_air.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_air(self):
        """
        The detail view of a air with a started in the past displays the air's text.
        """
        startedpast7 = timezone.now() + datetime.timedelta(days=-7, hours=-1)
        endedpast7 = timezone.now() + datetime.timedelta(days=-7)
        past_air = create_air(program_name="酒井健太ANN0", started_at=startedpast7, ended_at=endedpast7)

        url = reverse('airs:detail', args=(past_air.id,))
        response = self.client.get(url)
        self.assertContains(response, past_air.program.name)
