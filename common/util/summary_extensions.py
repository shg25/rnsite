# サマリー

import datetime

from django.utils.timezone import make_aware


MAX_YEAR = 2023
MIN_YEAR = 2022


def this_month():
    now = datetime.datetime.now()
    this_month = make_aware(datetime.datetime(now.year, now.month, 1, 0, 0))
    return this_month


def yearly_count_list(monthly_count_list):
    yearly_count_list = []
    target_year = MAX_YEAR  # こっちが最大値（例：2023年まで）
    while target_year >= MIN_YEAR:  # こちらが最小値（例：2021年から）
        yearly = yearly_count(monthly_count_list, target_year)
        yearly_count_list.append(yearly)
        target_year -= 1
    return yearly_count_list


def yearly_count(monthly_count_list, target_year):
    target_year_started = make_aware(datetime.datetime(target_year, 4, 1, 0, 0))
    next_year_started = make_aware(datetime.datetime((target_year + 1), 4, 1, 0, 0))
    monthly_count_list = list(filter(lambda x: x['monthly_date'] >= target_year_started and x['monthly_date'] < next_year_started, monthly_count_list))
    count = 0
    for m in monthly_count_list:
        count += m['count']
    return {
        'year': target_year,
        'count': count,
        'monthly_count_list': monthly_count_list,
    }
