import datetime

from django.views import generic

from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.utils.timezone import make_aware

from ..models import Broadcaster, Air


class BroadcasterListView(generic.ListView):
    model = Broadcaster
    paginate_by = 40


class BroadcasterDetailView(generic.DetailView):
    model = Broadcaster

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # TODO 理想としては、完全に月で区切らずに5:00〜4:59で区切りたいが個別にcountしていくとコスパが悪かったりするかも & 大きく変わるわけではないので優先度低
        monthly_count_list = Air.objects.filter(broadcaster=context['broadcaster'])\
            .annotate(monthly_date=TruncMonth('started_at')).values('monthly_date')\
            .annotate(count=Count('id')).values('monthly_date', 'count')\
            .order_by('monthly_date')

        yearly_count_list = []
        target_year = 2023  # こっちが最大値（例：2023年まで）
        while target_year >= 2022:  # こちらが最小値（例：2021年から）
            yearly_count = self.yearly_count(monthly_count_list, target_year)
            yearly_count_list.append(yearly_count)
            target_year -= 1
        context['yearly_count_list'] = yearly_count_list

        # 今月分のデータの色変え用のデータ
        now = datetime.datetime.now()
        this_month = make_aware(datetime.datetime(now.year, now.month, 1, 0, 0))
        context['this_month'] = this_month

        return context

    def yearly_count(self, monthly_count_list, target_year):
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
