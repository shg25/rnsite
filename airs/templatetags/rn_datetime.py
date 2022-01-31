from django import template

from common.util.datetime_extensions import *

register = template.Library()


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
def radiko_link(started, radiko_identifier):
    return output_radiko_link(started, radiko_identifier)


@register.filter
def radiko_link_next_week(started, radiko_identifier):
    return output_radiko_link_next_week(started, radiko_identifier)
