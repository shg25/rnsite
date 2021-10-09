import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import Broadcaster, Program, Air, Nanitozo
from .forms import AirCreateByShareTextForm


class IndexView(generic.ListView):
    model = Air
    queryset = Air.objects.filter(started__lte=timezone.now()).order_by('-started')  # オススメの放送を取得する

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        w1_list = Air.objects.filter(started__lte=timezone.now()).order_by('-started')[:4]  # TODO 今週分を取得する ダミーで4件取得にしてる
        w2_list = Air.objects.filter(started__lte=timezone.now()).order_by('-started')[4:10]  # TODO 先週分を取得する ダミーで4件目以降取得にしてる
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


class AirCreateByShareTextView(generic.FormView):
    template_name = 'airs/air_create.html'
    form_class = AirCreateByShareTextForm
    success_url = '/'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        # print('\n-- form_valid ここから --\n')

        share_text = form.cleaned_data['share_text']
        # TODO シェアテキストを使ってスクレイピングしてタイトルを取得する

        # これだけだとデータを差し替えられない
        # form.cleaned_data['name'] = '番組名をセット'
        # print(form.cleaned_data)

        # [overview_before]と[overview_after]以外をセット TODO 全てスクレイピングしたタイトルを元にセットする
        form.instance.name = '確認用のダミー番組名4'
        form.instance.program = Program.objects.filter(search_index__contains='ｱﾙｺ').first()  # ヒットしない場合は[None]が入ってDBには[null]で保存
        form.instance.broadcaster = Broadcaster.objects.filter(search_index__contains='luckyfm').first()  # ヒットしない場合は[None]が入ってDBには[null]で保存
        form.instance.started = datetime.datetime(2021, 8, 30, 20, 0)  # 日本時刻で登録される模様 → DBは2021-08-30T06:00:00Z
        form.instance.ended = datetime.datetime(2021, 8, 30, 21, 0)  # 日本時刻で登録される模様 → DBは2021-08-30T07:00:00Z
        saved_air = form.save()

        # TODO saveエラー時の処理（被りとか）

        # 続けて何卒をデフォルト値で登録
        user = self.request.user  # ログイン中のユーザー情報
        saved_air.nanitozo_set.create(user=user)

        # TODO createエラー時の処理（被りとか）

        # print('\n-- form_valid ここまで --\n')
        # return redirect('detail', id=saved_air.id) # TODO 詳細画面にリダイレクトするサンプルの引用だけど、form_valid内で適切かどうかは確認が必要 （renderを使うとか？）
        return super().form_valid(form)


class NanitozoUpdateView(generic.UpdateView):
    model = Nanitozo
    fields = ['good', 'comment_open', 'comment_recommend', 'comment', 'comment_negative']
    template_name = 'airs/nanitozo_update.html'

    def get_success_url(self):
        return reverse('airs:detail', kwargs={'pk': self.object.air.id})


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


@method_decorator(login_required, name='dispatch')
class AirUpdateView(generic.UpdateView):
    model = Air
    fields = ['overview_before', 'overview_after']
    template_name = 'airs/air_update.html'

    def get_success_url(self):
        return reverse('airs:detail', kwargs={'pk': self.kwargs['pk']})


class DetailView(generic.DetailView):
    model = Air

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        air = context.get('object')
        nanitozo_list = air.nanitozo_set.all()
        context['nanitozo_list'] = nanitozo_list
        context['good_nanitozo_list'] = list(filter(lambda x: x.good == True, nanitozo_list))
        context['comment_open_recommend_nanitozo_list'] = list(filter(lambda x: x.comment_open == True and x.comment_recommend != None and len(x.comment_recommend) != 0, nanitozo_list))
        context['comment_open_nanitozo_list'] = list(filter(lambda x: x.comment_open == True and x.comment != None and len(x.comment) != 0, nanitozo_list))
        context['comment_open_negative_nanitozo_list'] = list(filter(lambda x: x.comment_open == True and x.comment_negative != None and len(x.comment_negative) != 0, nanitozo_list))

        my_nanitozo_list = list(filter(lambda x: x.user == self.request.user, nanitozo_list))
        if bool(my_nanitozo_list):
            context['my_nanitozo'] = my_nanitozo_list[0]

        return context


class ResultsView(generic.DetailView):
    model = Air
    template_name = 'airs/results.html'


@login_required
def nanitozo_create(request, air_id):
    air = get_object_or_404(Air, pk=air_id)
    try:
        user = request.user  # ログイン中のユーザー情報
        air.nanitozo_set.create(user=user)
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
