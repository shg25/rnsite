from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib.auth.models import User

from .models import Broadcaster, Program, Air, Nanitozo

class IndexView(generic.ListView):
    model = Air
    queryset = Air.objects.filter(started__lte=timezone.now()).order_by('-started') # オススメの放送を取得する

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        w1_list = Air.objects.filter(started__lte=timezone.now()).order_by('-started')[:4] # TODO 今週分を取得する ダミーで4件取得にしてる
        w2_list = Air.objects.filter(started__lte=timezone.now()).order_by('-started')[4:10] # TODO 先週分を取得する ダミーで4件目以降取得にしてる
        context['w1_list'] = w1_list
        context['w2_list'] = w2_list
        return context
        # TODO  全面的に filter(started__lte=timezone.now()) の値を調整する、実際は事前登録も可とするので、現在時刻との比較は不要


class NsView(generic.ListView):
    model = Nanitozo
    queryset = Nanitozo.objects.order_by('-created')[:40]

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['close_list'] = Nanitozo.objects.filter(comment_open__lte=False).order_by('-created')[:40]
        return context


class NCreateView(generic.TemplateView):  # TODO Form系のViewにする
    template_name = 'airs/n_create.html'


class NUpdateView(generic.TemplateView):  # TODO Form系のViewにする
    template_name = 'airs/n_update.html'


class UsersView(generic.ListView):
    model = User
    # ページネーションなしの全件表示でいける想定
    # 将来的には何卒した日時を保存して降順で表示するなど検討したいが、Djangoのauthでできるかどうか


class BroadcastersView(generic.ListView):
    model = Broadcaster
    paginate_by = 40


class ProgramsView(generic.ListView):
    model = Program
    paginate_by = 40
    # 将来的には登録があった日時を保存して降順で表示するなど検討


class UserView(generic.DetailView):
    model = User


class BroadcasterView(generic.DetailView):
    model = Broadcaster


class ProgramView(generic.DetailView):
    model = Program


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
