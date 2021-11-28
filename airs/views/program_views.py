from django.views import generic

from ..models import Program


class ProgramsListView(generic.ListView):
    model = Program
    paginate_by = 40
    # TODO 放送登録日時降順で表示


class ProgramDetailView(generic.DetailView):
    model = Program
