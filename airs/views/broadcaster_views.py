from django.views import generic

from ..models import Broadcaster


class BroadcasterListView(generic.ListView):
    model = Broadcaster
    paginate_by = 40


class BroadcasterDetailView(generic.DetailView):
    model = Broadcaster
