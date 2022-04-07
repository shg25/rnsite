from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from ..models import Air, Nanitozo

_NANITOZO_LIST_LIMIT = 40


class NanitozoListView(generic.ListView):
    model = Nanitozo
    queryset = Nanitozo.objects.all()[:_NANITOZO_LIST_LIMIT]

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.request.user.is_authenticated:
            context['self_list'] = Nanitozo.objects_self.get(self.request.user)[:_NANITOZO_LIST_LIMIT]
            context['close_list'] = Nanitozo.objects_close.get(self.request.user)[:_NANITOZO_LIST_LIMIT]
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
    except IntegrityError:
        messages.warning(request, '何卒済みの放送')
    except Exception as err:
        messages.error(request, '何卒登録エラー：' + str(type(err)))
    else:
        messages.success(request, '何卒！')
    return HttpResponseRedirect(reverse('airs:detail', args=(air.id,)))


@login_required
def nanitozo_apply_good(request, air_id, pk):
    change_for = True

    nanitozo = get_object_or_404(Nanitozo, pk=pk)

    if nanitozo.good == change_for:  # 変更する必要があるか確認
        messages.warning(request, 'もう満足してますね')
    elif nanitozo.user != request.user:  # ログインしているユーザーが一致しているか確認
        messages.error(request, 'あなたは誰…？')  # HttpResponseForbidden()を返した方が適切かもだけどメッセージだけで充分と判断
    else:  # 問題なさそうなのでnanitozoをアップデート
        nanitozo.good = change_for
        nanitozo.save(update_fields=['good'])
        messages.success(request, '満足！')

    return HttpResponseRedirect(reverse('airs:detail', args=(air_id,)))


@login_required
def nanitozo_cancel_good(request, air_id, pk):
    change_for = False

    nanitozo = get_object_or_404(Nanitozo, pk=pk)

    if nanitozo.good == change_for:  # 変更する必要があるか確認
        messages.warning(request, '既に満足がキャンセルされてました')
    elif nanitozo.user != request.user:  # ログインしているユーザーが一致しているか確認
        messages.error(request, 'あなたは誰…？')  # HttpResponseForbidden()を返した方が適切かもだけどメッセージだけで充分と判断
    else:  # 問題なさそうなのでnanitozoをアップデート
        nanitozo.good = change_for
        nanitozo.save(update_fields=['good'])
        messages.success(request, '満足 has been キャンセルド！')

    return HttpResponseRedirect(reverse('airs:detail', args=(air_id,)))


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
