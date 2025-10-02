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
