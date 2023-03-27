from django.views import generic

from django.db.models.functions import TruncMonth
from django.db.models import Count

from common.util.summary_extensions import this_month, yearly_count_list

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
        context['yearly_count_list'] = yearly_count_list(monthly_count_list)

        # 今月分のデータの色変え用のデータ
        context['this_month'] = this_month()
        return context
