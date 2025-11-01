# サマリー

import datetime

from django.utils.timezone import make_aware


def this_month():
    now = datetime.datetime.now()
    this_month = make_aware(datetime.datetime(now.year, now.month, 1, 0, 0))
    return this_month


def yearly_count_list(monthly_count_list):
    # データが存在しない場合は空のリストを返す
    if not monthly_count_list:
        return []

    # monthly_count_list から最小年と最大年を動的に計算
    monthly_list = list(monthly_count_list)
    if not monthly_list:
        return []

    # 4月始まりの年度として考慮して最小年・最大年を計算
    min_date = min(monthly_list, key=lambda x: x['monthly_date'])['monthly_date']
    max_date = max(monthly_list, key=lambda x: x['monthly_date'])['monthly_date']

    # 4月始まりの年度として考慮（3月以前は前年度扱い）
    min_year = min_date.year if min_date.month >= 4 else min_date.year - 1
    max_year = max_date.year if max_date.month >= 4 else max_date.year - 1

    yearly_count_list = []
    target_year = max_year  # こっちが最大値
    while target_year >= min_year:  # こちらが最小値
        yearly = yearly_count(monthly_list, target_year)
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
