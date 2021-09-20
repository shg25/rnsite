import datetime

from django import template
from math import floor
from pytz import timezone as pytztimezone

register = template.Library()


@register.filter
def init_rn_datetime(started, ended):
    return RNDatetime(started, ended)


class RNDatetime:
    weekday_list = ['月', '火', '水', '木', '金', '土', '日']

    def __init__(self, started, ended):
        self.airtime = diff_minutes(started, ended)  # 放送開始日時と放送終了日時の差分から放送時間を取得

        started = astimezone_tokyo(started)  # 日本時間にしておく

        # 0〜4時は 日付を[-1日] 時間は[+24h]で表示する（0→24、1→25、2→26、3→27、4→28）
        # 終了時刻が5時の場合はラジコ上の終了時刻は29時と表記されるが、当サイトでは終了時刻は表示しないので不要
        if is_midnight(started):
            started = started + datetime.timedelta(days=-1)  # -1日
            hour = str(started.hour + 24)
        else:
            hour = str(started.hour)

        self.md = str(started.month) + '/' + str(started.day)
        self.weekday = self.weekday_list[started.weekday()]
        self.hm = str(hour) + ':' + str(started.strftime("%M"))


def astimezone_tokyo(dt):
    return dt.astimezone(pytztimezone('Asia/Tokyo'))


def is_midnight(dt):
    return dt.hour < 5


def diff_minutes(before, after):
    return floor(((after - before).seconds / 60))  # 時間差を[timedelta]で取得して分数を算出して小数点以下は切り捨て
