from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from ..models import Air, Nanitozo


class NanitozoListView(generic.ListView):
    model = Nanitozo
    queryset = Nanitozo.objects.order_by('-created')[:40]

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.request.user.is_authenticated:
            context['self_list'] = Nanitozo.objects.filter(user=self.request.user).order_by('-created')[:40]
            context['close_list'] = Nanitozo.objects.filter(user=self.request.user).filter(comment_open=False).order_by('-created')[:40]
        return context


@method_decorator(login_required, name='dispatch')  # TODO 本人しか更新できないようにする
class NanitozoUpdateView(generic.UpdateView):
    model = Nanitozo
    fields = ['good', 'comment_open', 'comment_recommend', 'comment', 'comment_negative']
    template_name = 'airs/nanitozo_update.html'

    def get_success_url(self):
        return reverse('airs:detail', kwargs={'pk': self.object.air.id})


@login_required
def nanitozo_create(request, air_id):
    air = get_object_or_404(Air, pk=air_id)
    try:
        air.nanitozo_set.create(user=request.user)
    except:
        messages.error(request, '既に何卒してました！')
        return HttpResponseRedirect(reverse('airs:detail', args=(air.id,)))
    else:
        messages.success(request, '何卒！')
        return HttpResponseRedirect(reverse('airs:detail', args=(air.id,)))


@login_required
def nanitozo_delete(request, air_id, pk):
    try:
        Nanitozo.objects.get(pk=pk).delete()
    except:
        messages.error(request, '既に何卒を取り消してました！')
        return HttpResponseRedirect(reverse('airs:detail', args=(air_id,)))
    else:
        messages.success(request, '何卒を取り消しました！')
        return HttpResponseRedirect(reverse('airs:detail', args=(air_id,)))
