import datetime

from django.views import generic
from django.contrib.auth.models import User
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.utils.timezone import make_aware

from ..models import Nanitozo


class UserListView(generic.ListView):
    model = User
    # NOTE ページネーションなしで問題ない範囲しかユーザーを登録しない想定
    # TODO ユーザー名昇順で表示
    # TODO 何卒した日時を保存して降順で表示（DjangoのAuthで可能であれば）


class UserDetailView(generic.DetailView):
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # TODO 理想としては、完全に月で区切らずに5:00〜4:59で区切りたいが個別にcountしていくとコスパが悪かったりするかも & 大きく変わるわけではないので優先度低
        nanitozo_trunc_month = Nanitozo.objects.filter(user=context['user']).annotate(
            monthly_date=TruncMonth('created_at')
        ).values('monthly_date').annotate(
            count=Count('id'),
        ).values('monthly_date', 'count').order_by('monthly_date')

        nanitozo_monthly = []
        target_year = 2023 # こっちが最大値（例：2022年まで）
        while target_year >= 2022: # こちらが最小値（例：2021年から）
            monthly_list = self.monthly_list_filtering_target_year(nanitozo_trunc_month, target_year)
            nanitozo_monthly.append(monthly_list)
            target_year -= 1

        context['nanitozo_monthly'] = nanitozo_monthly

        # 今月分のデータの色変え用のデータ
        now = datetime.datetime.now()
        this_month = make_aware(datetime.datetime(now.year, now.month, 1, 0, 0))
        context['this_month'] = this_month

        return context

    def monthly_list_filtering_target_year(self, nanitozo_trunc_month, target_year):
        start_target_year = make_aware(datetime.datetime(target_year, 4, 1, 0, 0))
        start_next_year = make_aware(datetime.datetime((target_year + 1), 4, 1, 0, 0))
        nanitozo_trunc_month = list(filter(lambda x: x['monthly_date'] >= start_target_year and x['monthly_date'] < start_next_year, nanitozo_trunc_month))
        target_year_sum = 0
        for n in nanitozo_trunc_month:
            target_year_sum += n['count']
        return {
            'year': target_year,
            'sum': target_year_sum,
            'nanitozo_trunc_month': nanitozo_trunc_month,
        }
