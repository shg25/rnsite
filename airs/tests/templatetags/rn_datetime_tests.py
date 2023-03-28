import freezegun

from django.test import TestCase
from django.utils import timezone

from ...templatetags.rn_datetime import *


class AirDateLabelTests(TestCase):

    # 以下、freeze_time → not深夜

    @freezegun.freeze_time('2023-02-15 5:30:00')
    def test_2日後の日中の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 17, 12, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '明後日以降')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-danger')

    @freezegun.freeze_time('2023-02-15 5:30:00')
    def test_2日後の深夜の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 18, 1, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '明後日以降')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-danger')

    @freezegun.freeze_time('2023-02-15 5:30:00')
    def test_1日後の日中の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 16, 12, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '明日')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-danger')

    @freezegun.freeze_time('2023-02-15 5:30:00')
    def test_1日後の深夜の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 17, 1, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '明日')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-danger')

    @freezegun.freeze_time('2023-02-15 5:30:00')
    def test_今日の日中の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 15, 12, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '今日')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-danger')

    @freezegun.freeze_time('2023-02-15 5:30:00')
    def test_今日の深夜の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 16, 1, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '今日')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-danger')

    @freezegun.freeze_time('2023-02-15 5:30:00')
    def test_昨日の日中の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 14, 12, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '昨日')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-success')

    @freezegun.freeze_time('2023-02-15 5:30:00')
    def test_昨日の深夜の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 15, 1, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '昨日')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-success')

    @freezegun.freeze_time('2023-02-15 5:30:00')
    def test_昨日の日中の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 13, 12, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '今週')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-success')

    @freezegun.freeze_time('2023-02-15 5:30:00')
    def test_昨日の深夜の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 14, 1, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '今週')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-success')

    @freezegun.freeze_time('2023-02-15 5:30:00')
    def test_6日前の日中の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 9, 12, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '今週')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-success')

    @freezegun.freeze_time('2023-02-15 5:30:00')
    def test_6日前の深夜の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 10, 1, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '今週')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-success')

    @freezegun.freeze_time('2023-02-15 5:30:00')
    def test_7日前の日中の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 8, 12, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, 'ちょうど1週間前')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-success')

    @freezegun.freeze_time('2023-02-15 5:30:00')
    def test_7日前の深夜の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 9, 1, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, 'ちょうど1週間前')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-success')

    @freezegun.freeze_time('2023-02-15 5:30:00')
    def test_8日前の日中の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 7, 12, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '先週')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-warning')

    @freezegun.freeze_time('2023-02-15 5:30:00')
    def test_8日前の深夜の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 8, 1, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '先週')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-warning')

    @freezegun.freeze_time('2023-02-15 5:30:00')
    def test_14日前の日中の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 1, 12, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '先週')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-warning')

    @freezegun.freeze_time('2023-02-15 5:30:00')
    def test_14日前の深夜の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 2, 1, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '先週')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-warning')

    @freezegun.freeze_time('2023-02-15 5:30:00')
    def test_15日前の日中の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 1, 31, 12, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-hidden')

    @freezegun.freeze_time('2023-02-15 5:30:00')
    def test_15日前の深夜の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 1, 1, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-hidden')

    # ここまで、freeze_time → not深夜

    # 以下、freeze_time → is深夜

    @freezegun.freeze_time('2023-02-16 4:59:00')
    def test_深夜から2日後の日中の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 17, 12, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '明後日以降')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-danger')

    @freezegun.freeze_time('2023-02-16 4:59:00')
    def test_深夜から2日後の深夜の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 18, 1, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '明後日以降')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-danger')

    @freezegun.freeze_time('2023-02-16 4:59:00')
    def test_深夜から1日後の日中の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 16, 12, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '明日')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-danger')

    @freezegun.freeze_time('2023-02-16 4:59:00')
    def test_深夜から1日後の深夜の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 17, 1, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '明日')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-danger')

    @freezegun.freeze_time('2023-02-16 4:59:00')
    def test_深夜から今日の日中の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 15, 12, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '今日')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-danger')

    @freezegun.freeze_time('2023-02-16 4:59:00')
    def test_深夜から今日の深夜の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 16, 1, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '今日')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-danger')

    @freezegun.freeze_time('2023-02-16 4:59:00')
    def test_深夜から昨日の日中の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 14, 12, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '昨日')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-success')

    @freezegun.freeze_time('2023-02-16 4:59:00')
    def test_深夜から昨日の深夜の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 15, 1, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '昨日')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-success')

    @freezegun.freeze_time('2023-02-16 4:59:00')
    def test_深夜から昨日の日中の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 13, 12, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '今週')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-success')

    @freezegun.freeze_time('2023-02-16 4:59:00')
    def test_深夜から昨日の深夜の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 14, 1, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '今週')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-success')

    @freezegun.freeze_time('2023-02-16 4:59:00')
    def test_深夜から6日前の日中の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 9, 12, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '今週')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-success')

    @freezegun.freeze_time('2023-02-16 4:59:00')
    def test_深夜から6日前の深夜の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 10, 1, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '今週')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-success')

    @freezegun.freeze_time('2023-02-16 4:59:00')
    def test_深夜から7日前の日中の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 8, 12, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, 'ちょうど1週間前')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-success')

    @freezegun.freeze_time('2023-02-16 4:59:00')
    def test_深夜から7日前の深夜の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 9, 1, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, 'ちょうど1週間前')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-success')

    @freezegun.freeze_time('2023-02-16 4:59:00')
    def test_深夜から8日前の日中の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 7, 12, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '先週')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-warning')

    @freezegun.freeze_time('2023-02-16 4:59:00')
    def test_深夜から8日前の深夜の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 8, 1, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '先週')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-warning')

    @freezegun.freeze_time('2023-02-16 4:59:00')
    def test_深夜から14日前の日中の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 1, 12, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '先週')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-warning')

    @freezegun.freeze_time('2023-02-16 4:59:00')
    def test_深夜から14日前の深夜の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 2, 1, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '先週')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-label-warning')

    @freezegun.freeze_time('2023-02-16 4:59:00')
    def test_深夜から15日前の日中の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 1, 31, 12, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-hidden')

    @freezegun.freeze_time('2023-02-16 4:59:00')
    def test_深夜から15日前の深夜の放送(self):
        air_started_at = timezone.make_aware(timezone.datetime(2023, 2, 1, 1, 0))
        response = air_date_label_text(air_started_at)
        self.assertEqual(response, '')
        response = air_date_label_class(air_started_at)
        self.assertEqual(response, 'uk-hidden')

    # ここまで、freeze_time → is深夜
