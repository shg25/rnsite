from urllib.parse import quote

from django import template

from common.util.datetime_extensions import *

register = template.Library()


@register.filter
def air_date_label_text(air_started_at):
    days = air_started_diff_days(air_started_at)

    # 例 現在時刻 2023/02/15 5:00〜28:59（= 2023/02/16 4:59）
    if days >= 2:  # 例 2023/02/17 5:00〜
        return '明後日以降'
    elif days == 1:  # 例 2023/02/16 5:00〜28:59（= 2023/02/17 4:59）
        return '明日'
    elif days == 0:  # 例 22023/02/15 5:00〜28:59（= 2023/02/16 4:59）
        return '今日'
    elif days >= -6:  # 例 2023/02/09〜02/14 → 例 2023/02/09 5:00〜
        return '今週'
    elif days == -7:  # 例 2023/02/08 → 例 2023/02/08 5:00〜
        return 'ちょうど1週間前'
    elif days >= -14:  # 例 2023/02/01〜02/07 → 例 2023/02/01 5:00〜
        return '先週'
    else:
        return ''  # 先週より前の場合は非表示


@register.filter
def air_date_label_class(air_started_at):
    days = air_started_diff_days(air_started_at)

    # 例 現在時刻 2023/02/15 5:00〜28:59（= 2023/02/16 4:59）
    if days >= 2:  # 例 2023/02/17 5:00〜
        return 'uk-label-danger'  # 明後日以降
    elif days == 1:  # 例 2023/02/16 5:00〜28:59（= 2023/02/17 4:59）
        return 'uk-label-danger'  # 明日
    elif days == 0:  # 例 22023/02/15 5:00〜28:59（= 2023/02/16 4:59）
        return 'uk-label-danger'  # 今日
    elif days >= -6:  # 例 2023/02/09〜02/14 → 例 2023/02/09 5:00〜
        return 'uk-label-success'  # 今週
    elif days == -7:  # 例 2023/02/08 → 例 2023/02/08 5:00〜
        return 'uk-label-success'  # ちょうど1週間前
    elif days >= -14:  # 例 2023/02/01〜02/07 → 例 2023/02/01 5:00〜
        return 'uk-label-warning'  # 先週
    else:
        return 'uk-hidden'  # 先週より前の場合は非表示


@register.filter
def rn_regroup_date(dt):
    dt_date_initialized = initialize_date(dt)
    return datetime.date(dt_date_initialized.year, dt_date_initialized.month, dt_date_initialized.day)


@register.filter
def rn_regrouped_date_weekday(dt_date_initialized):
    return output_weekday(dt_date_initialized)


@register.filter
def rn_regrouped_date_md(dt_date_initialized):
    return output_md(dt_date_initialized)


@register.filter
def rn_ymdhm(dt):
    dt_date_initialized = initialize_date(dt)
    return output_ymdhm(dt_date_initialized)


@register.filter
def init_rn_datetime(started, ended):
    return RNDatetime(started, ended)


class RNDatetime:
    def __init__(self, started, ended):
        self.airtime = output_diff_minutes(started, ended)  # 放送開始日時と放送終了日時の差分から放送時間を取得

        started_date_initialized = initialize_date(started)

        self.weekday = output_weekday(started_date_initialized)
        self.md = output_md(started_date_initialized)
        self.hm = output_hm(started_date_initialized)


@register.filter
def radiko_url(started, radiko_identifier):
    return output_radiko_url(started, radiko_identifier)


@register.filter
def radiko_url_next_week(started, radiko_identifier):
    return output_radiko_url_next_week(started, radiko_identifier)


@register.filter
def encoded_radiko_url_next_week(started, radiko_identifier):
    return quote(radiko_url_next_week(started, radiko_identifier), safe='')
