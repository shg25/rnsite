from django.views import generic
from django.contrib.auth.models import User
from django.db.models.functions import TruncMonth
from django.db.models import Count

from common.util.summary_extensions import this_month, yearly_count_list

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
        monthly_count_list = Nanitozo.objects.filter(user=context['user'])\
            .annotate(monthly_date=TruncMonth('created_at')).values('monthly_date')\
            .annotate(count=Count('id'),).values('monthly_date', 'count')\
            .order_by('monthly_date')

        context['yearly_count_list'] = yearly_count_list(monthly_count_list)

        # 今月分のデータの色変え用のデータ
        context['this_month'] = this_month()
        return context
