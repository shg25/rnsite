from django.contrib.auth.models import User
from django.db.models import Count
from django.views import generic

from ..models import Program


class ProgramsListView(generic.ListView):
    model = Program
    paginate_by = 40

    def get_queryset(self):
        return Program.objects.annotate(
            air_count=Count('air', distinct=True),
            nanitozo_count=Count('air__nanitozo', distinct=True)
        ).filter(nanitozo_count__gt=0).order_by('-nanitozo_count', 'name')


class ProgramDetailView(generic.DetailView):
    model = Program

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 番組全体の統計情報
        program_stats = Program.objects.filter(pk=self.object.pk).annotate(
            air_count=Count('air', distinct=True),
            nanitozo_count=Count('air__nanitozo', distinct=True)
        ).first()

        context['program_air_count'] = program_stats.air_count
        context['program_nanitozo_count'] = program_stats.nanitozo_count

        # ユーザーごとの何卒数ランキング
        user_nanitozo_ranking = User.objects.filter(
            nanitozo__air__program=self.object
        ).annotate(
            nanitozo_count=Count('nanitozo')
        ).order_by('-nanitozo_count', 'last_name')

        context['user_nanitozo_ranking'] = user_nanitozo_ranking
        return context
