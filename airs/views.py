from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import Air, Nanitozo

# def index(request):
#     latest_air_list = Air.objects.order_by('-started')[:5]
#     context = {'latest_air_list': latest_air_list}
#     return render(request, 'airs/index.html', context)
class IndexView(generic.ListView):
    template_name = 'airs/index.html'
    context_object_name = 'latest_air_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Air.objects.order_by('-started')[:5]


# def detail(request, air_id):
#     air = get_object_or_404(Air, pk=air_id)
#     return render(request, 'airs/detail.html', {'air': air})
class DetailView(generic.DetailView):
    model = Air
    template_name = 'airs/detail.html'

# def results(request, air_id):
#     air = get_object_or_404(Air, pk=air_id)
#     return render(request, 'airs/results.html', {'air': air})
class ResultsView(generic.DetailView):
    model = Air
    template_name = 'airs/results.html'

def vote(request, air_id):
    air = get_object_or_404(Air, pk=air_id)
    try:
        selected_nanitozo = air.nanitozo_set.get(pk=request.POST['nanitozo'])
    except (KeyError, Nanitozo.DoesNotExist):
        # Redisplay the air voting form.
        return render(request, 'airs/detail.html', {
            'air': air,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_nanitozo.comment += "追加！"
        selected_nanitozo.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('airs:results', args=(air.id,)))
