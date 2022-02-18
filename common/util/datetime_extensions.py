# 日時の出力を司る

import datetime

from django.utils.timezone import make_aware

from pytz import timezone as pytztimezone
from math import floor


def output_diff_minutes(before, after):
    return str(floor(((after - before).seconds / 60)))  # 時間差を[timedelta]で取得して分数を算出して小数点以下は切り捨て


def __is_midnight(dt):  # 0〜4時は深夜（= 1日前にシフト & Hourを[+24h]で表記する）
    return dt.hour < 5


def __timedelta_midnight_date(dt):
    if __is_midnight(dt):
        dt = timedelta_days(dt, -1)  # 0〜4時は日付を[-1日]で表示する
    return dt


def initialize_date(dt):
    dt_tokyo = dt.astimezone(pytztimezone('Asia/Tokyo'))  # タイムゾーンを日本時間にする
    dt_date_initialized = __timedelta_midnight_date(dt_tokyo)  # 深夜の場合は1日前にシフトする（時間表示は別途対応）
    return dt_date_initialized


def output_ymdhm(dt_date_initialized):
    return str(dt_date_initialized.strftime('%Y/%m/%d')) + " " + output_hm(dt_date_initialized)


def output_md(dt_date_initialized):
    return str(dt_date_initialized.month) + '/' + str(dt_date_initialized.day)


def output_hm(dt_date_initialized):
    # 0〜4時は[+24h]で表示する（0→24、1→25、2→26、3→27、4→28）
    # 終了時刻が5時の場合はradiko上の終了時刻は29時と表記されるが、当サイトでは終了時刻は表示しないので不要
    if __is_midnight(dt_date_initialized):
        str_hour_initialized = str(dt_date_initialized.hour + 24)
    else:
        str_hour_initialized = str(dt_date_initialized.hour)
    return str_hour_initialized + ':' + str(dt_date_initialized.strftime('%M'))


def output_weekday(dt_date_initialized):
    weekday_list = ['月', '火', '水', '木', '金', '土', '日']
    return weekday_list[dt_date_initialized.weekday()]


#


def output_radiko_link(dt, radiko_identifier):
    dt_tokyo = dt.astimezone(pytztimezone('Asia/Tokyo'))  # タイムゾーンを日本時間にする
    return __create_radiko_link(dt_tokyo, radiko_identifier)


def output_radiko_link_next_week(dt, radiko_identifier):
    dt_tokyo = dt.astimezone(pytztimezone('Asia/Tokyo'))  # タイムゾーンを日本時間にする
    dt_tokyo = timedelta_days(dt_tokyo, 7)
    return __create_radiko_link(dt_tokyo, radiko_identifier)


def __create_radiko_link(dt_tokyo, radiko_identifier):
    return 'http://radiko.jp/share/?sid=' + radiko_identifier + '&t=' + str(dt_tokyo.strftime('%Y%m%d%H%M')) + '00'


#


def this_week_started():
    now = __datetime_now()
    if __is_midnight(now):
        dt = timedelta_days(now, -8)
    else:
        dt = timedelta_days(now, -7)
    return new_datetime(dt.year, dt.month, dt.day, 5, 0)


def last_week_started():
    now = __datetime_now()
    if __is_midnight(now):
        dt = timedelta_days(now, -15)
    else:
        dt = timedelta_days(now, -14)
    return new_datetime(dt.year, dt.month, dt.day, 5, 0)


#
# import datetime 関連の処理

def __datetime_now():
    return datetime.datetime.now()


def new_datetime(year, month, day, hour, minute):
    return make_aware(datetime.datetime(year, month, day, hour, minute))


def new_date(year, month, day):
    return make_aware(datetime.datetime(year, month, day))


def timedelta_days(dt, delta_days):
    return dt + datetime.timedelta(days=delta_days)
