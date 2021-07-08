from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Air, Nanitozo

# def index(request):
#     latest_air_list = Air.objects.order_by('-started')[:5]
#     context = {'latest_air_list': latest_air_list}
#     return render(request, 'airs/index.html', context)
class IndexView(generic.ListView):
    template_name = 'airs/index.html'
    context_object_name = 'latest_air_list'

    def get_queryset(self):
        """
        Return the last five started airs (not including those set to be started in the future).
        """
        return Air.objects.filter(started__lte=timezone.now()).order_by('-started')[:5]


class NsView(generic.ListView):
    template_name = 'airs/ns.html'
    context_object_name = 'latest_air_list'

    def get_queryset(self):
        """
        Return the last five started airs (not including those set to be started in the future).
        """
        return Air.objects.filter(started__lte=timezone.now()).order_by('-started')[:5]


class NCreateView(generic.TemplateView):  # TODO Form系のViewにする
    template_name = 'airs/n_create.html'


class NUpdateView(generic.TemplateView):  # TODO Form系のViewにする
    template_name = 'airs/n_update.html'


class UsersView(generic.ListView):
    template_name = 'airs/users.html'
    context_object_name = 'latest_air_list'

    def get_queryset(self):
        """
        Return the last five started airs (not including those set to be started in the future).
        """
        return Air.objects.filter(started__lte=timezone.now()).order_by('-started')[:5]


class BroadcastersView(generic.ListView):
    template_name = 'airs/broadcasters.html'
    context_object_name = 'latest_air_list'

    def get_queryset(self):
        """
        Return the last five started airs (not including those set to be started in the future).
        """
        return Air.objects.filter(started__lte=timezone.now()).order_by('-started')[:5]


class ProgramsView(generic.ListView):
    template_name = 'airs/programs.html'
    context_object_name = 'latest_air_list'

    def get_queryset(self):
        """
        Return the last five started airs (not including those set to be started in the future).
        """
        return Air.objects.filter(started__lte=timezone.now()).order_by('-started')[:5]


class CastsView(generic.ListView):
    template_name = 'airs/casts.html'
    context_object_name = 'latest_air_list'

    def get_queryset(self):
        """
        Return the last five started airs (not including those set to be started in the future).
        """
        return Air.objects.filter(started__lte=timezone.now()).order_by('-started')[:5]


class UserView(generic.DetailView):
    model = Air
    template_name = 'airs/user.html'

    def get_queryset(self):
        """
        Excludes any airs that aren't started yet.
        """
        return Air.objects.filter(started__lte=timezone.now())


class BroadcasterView(generic.DetailView):
    model = Air
    template_name = 'airs/broadcaster.html'

    def get_queryset(self):
        """
        Excludes any airs that aren't started yet.
        """
        return Air.objects.filter(started__lte=timezone.now())


class ProgramView(generic.DetailView):
    model = Air
    template_name = 'airs/program.html'

    def get_queryset(self):
        """
        Excludes any airs that aren't started yet.
        """
        return Air.objects.filter(started__lte=timezone.now())


class CastView(generic.DetailView):
    model = Air
    template_name = 'airs/cast.html'

    def get_queryset(self):
        """
        Excludes any airs that aren't started yet.
        """
        return Air.objects.filter(started__lte=timezone.now())

# def detail(request, air_id):
#     air = get_object_or_404(Air, pk=air_id)
#     return render(request, 'airs/detail.html', {'air': air})
class DetailView(generic.DetailView):
    model = Air
    template_name = 'airs/detail.html'

    def get_queryset(self):
        """
        Excludes any airs that aren't started yet.
        """
        return Air.objects.filter(started__lte=timezone.now())

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
