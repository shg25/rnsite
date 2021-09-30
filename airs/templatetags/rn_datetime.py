import datetime

from django import template
from math import floor
from pytz import timezone as pytztimezone

register = template.Library()


weekday_list = ['月', '火', '水', '木', '金', '土', '日']


@register.filter
def rn_regroup_date(dt):
    dt = timedelta_midnight_date(dt)
    return datetime.date(dt.year, dt.month, dt.day)


@register.filter
def rn_weekday(dt):
    return weekday_list[dt.weekday()]


@register.filter
def rn_md(dt):
    return str(dt.month) + '/' + str(dt.day)


@register.filter
def rn_hm(dt):
    # 0〜4時は[+24h]で表示する（0→24、1→25、2→26、3→27、4→28）
    # 終了時刻が5時の場合はラジコ上の終了時刻は29時と表記されるが、当サイトでは終了時刻は表示しないので不要
    if is_midnight(dt):
        hour = str(dt.hour + 24)
    else:
        hour = str(dt.hour)
    return str(hour) + ':' + str(dt.strftime("%M"))

@register.filter
def init_rn_datetime(started, ended):
    return RNDatetime(started, ended)


class RNDatetime:
    def __init__(self, started, ended):
        self.airtime = diff_minutes(started, ended)  # 放送開始日時と放送終了日時の差分から放送時間を取得

        started = astimezone_tokyo(started)  # 日本時間にしておく
        started = timedelta_midnight_date(started)

        self.weekday = rn_weekday(started)
        self.md = rn_md(started)
        self.hm = rn_hm(started)


def astimezone_tokyo(dt):
    return dt.astimezone(pytztimezone('Asia/Tokyo'))


def is_midnight(dt):
    return dt.hour < 5


def timedelta_midnight_date(dt):
    if is_midnight(dt):
        dt = dt + datetime.timedelta(days=-1)  # 0〜4時は日付を[-1日]で表示する
    return dt


def diff_minutes(before, after):
    return floor(((after - before).seconds / 60))  # 時間差を[timedelta]で取得して分数を算出して小数点以下は切り捨て
