from django.views import generic
from django.contrib.auth.models import User
from django.db.models.functions import TruncMonth, TruncYear
from django.db.models import Count

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

        # TODO TruncYearとTruncMonthそれぞれで取得してるけど、TruncMonthだけとってYearは計算したほうが良いかも？
        nanitozo_trunc_year = Nanitozo.objects.filter(user=context['user']).annotate(
            monthly_date=TruncYear('created_at')
        ).values('monthly_date').annotate(
            count=Count('id'),
        ).values('monthly_date', 'count').order_by('-monthly_date')

        nanitozo_trunc_month = Nanitozo.objects.filter(user=context['user']).annotate(
            monthly_date=TruncMonth('created_at')
        ).values('monthly_date').annotate(
            count=Count('id'),
        ).values('monthly_date', 'count').order_by('monthly_date')

        context = {
            'nanitozo_trunc_year': nanitozo_trunc_year,
            'nanitozo_trunc_month': nanitozo_trunc_month,
        }

        return context
