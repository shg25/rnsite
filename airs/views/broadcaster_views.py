from django.views import generic

from django.db.models.functions import TruncMonth
from django.db.models import Count

from common.util.summary_extensions import this_month, yearly_count_list

from ..models import Broadcaster, Air


class BroadcasterListView(generic.ListView):
    model = Broadcaster
    paginate_by = 40

    def get_queryset(self):
        return Broadcaster.objects.annotate(
            air_count=Count('air', distinct=True),
            nanitozo_count=Count('air__nanitozo', distinct=True)
        ).filter(nanitozo_count__gt=0).order_by('-nanitozo_count', 'name')


class BroadcasterDetailView(generic.DetailView):
    model = Broadcaster

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 放送局全体の統計情報
        broadcaster_stats = Broadcaster.objects.filter(pk=self.object.pk).aggregate(
            air_count=Count('air', distinct=True),
            nanitozo_count=Count('air__nanitozo', distinct=True)
        )

        context['broadcaster_air_count'] = broadcaster_stats['air_count']
        context['broadcaster_nanitozo_count'] = broadcaster_stats['nanitozo_count']

        # 番組ごとの何卒数ランキング（トップ10）
        from ..models import Program
        program_nanitozo_ranking = Program.objects.filter(
            air__broadcaster=self.object
        ).annotate(
            air_count=Count('air', distinct=True),
            nanitozo_count=Count('air__nanitozo', distinct=True)
        ).filter(nanitozo_count__gt=0).order_by('-nanitozo_count', 'name')[:10]

        context['program_nanitozo_ranking'] = program_nanitozo_ranking

        # TODO 理想としては、完全に月で区切らずに5:00〜4:59で区切りたいが個別にcountしていくとコスパが悪かったりするかも & 大きく変わるわけではないので優先度低
        monthly_count_list = Air.objects.filter(broadcaster=context['broadcaster'])\
            .annotate(monthly_date=TruncMonth('started_at')).values('monthly_date')\
            .annotate(count=Count('id')).values('monthly_date', 'count')\
            .order_by('monthly_date')
        context['yearly_count_list'] = yearly_count_list(monthly_count_list)

        # 今月分のデータの色変え用のデータ
        context['this_month'] = this_month()
        return context
