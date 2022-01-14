from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.decorators import method_decorator

from common.util.datetime_extensions import this_week_started, last_week_started, new_datetime, new_date, timedelta_days
from common.util.url_extensions import scraping_title
from common.util.string_extensions import find_urls, share_text_to_search_index

from ..models import Broadcaster, Program, Air
from ..forms import AirCreateByShareTextForm


# 要ログイン & superuser不可（=一般メンバー限定）
def login_required_only_general_member():
    def wrapper(wrapped):
        class WrappedClass(UserPassesTestMixin, wrapped):
            def test_func(self):
                return self.request.user.is_authenticated and not self.request.user.is_superuser
        return WrappedClass
    return wrapper


class AirListView(generic.ListView):
    model = Air
    # queryset = Air.objects.filter(started__gte=this_week_started()).order_by('-started') # これを使えばviewではair_listで取得できるがなぜかキャッシュらしきものが残るので一旦使わない

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        this_week_list = Air.objects.filter(started__gte=this_week_started()).order_by('-started')
        context['this_week_list'] = this_week_list
        last_week_list = Air.objects.filter(started__range=(last_week_started(), this_week_started())).order_by('-started')
        context['last_week_list'] = last_week_list

        # TODO オススメ放送取得（1/3）
        # context['recommend_list'] = Air.objects.filter(started__range=(last_week_started(), timezone.now())).order_by('-started')

        return context
        # TODO  全面的に filter(started__lte=timezone.now()) の値を調整する、実際は事前登録も可とするので、現在時刻との比較は不要


@login_required_only_general_member()
class AirCreateByShareTextView(generic.FormView):
    template_name = 'airs/air_create.html'
    form_class = AirCreateByShareTextForm
    success_url = '/'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # 投稿したシェアテキストを取得
        share_text = form.cleaned_data['share_text']
        # share_text = 'アルコ＆ピース D.C.GARAGE | TBSラジオ | 2021/10/05/火  24:00-25:00 https://radiko.jp/share/?sid=TBS&t=20211006000000' # 例1

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # [share_text]からラジコのURLを抜き出す
        urls = find_urls(share_text)
        if len(urls) == 0:
            messages.error(self.request, 'ラジコのURLがなさそう！ 投稿した「' + share_text + '」を管理人に教えて！！')  # TODO share_textをどこかに記録したい
            return super().form_invalid(form)

        has_radiko = False
        for url in urls:
            has_radiko = 'radiko.jp' in url
            if has_radiko:
                radiko_url = url
                break

        # radiko_url = "https://radiko.jp/share/?sid=TBS&t=20211006000000"

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # ラジコのサイトからサイトタイトルを取得
        title = scraping_title(radiko_url)
        # title = '2021年10月5日（火）24:00～25:00 | アルコ＆ピース D.C.GARAGE | TBSラジオ | radiko'
        # print(title)

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # タイトルに「|」が3つ以上含まれていることを確認
        # ※タイトルにも含まれる可能性があるので3以上は許可
        if title.count('|') < 3:
            # print('「|」が3つない')
            if 'この番組の配信は終了しました' in title:
                messages.error(self.request, '配信終了してるっぽい！　どうしても登録が必要なら管理人に相談を')
            else:
                messages.error(self.request, 'なんか違和感！ 投稿した「' + share_text + '」と「' + title + '」を管理人に教えて！！')  # TODO share_textをどこかに記録したい
            return super().form_invalid(form)

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # タイトル末尾の「| radiko」を除去
        # rfindで後ろから「|」を検索して、それより前だけ残す
        title = title[:title.rfind('|')]
        # print(title)

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # タイトルから放送局名を取得
        # rfindで後ろから「|」を検索して、それより後ろを取得 → 「| TBSラジオ 」
        # 「|」を削除して、前後のスペースを除去 → 「TBSラジオ」
        broadcaster_name = title[title.rfind('|'):].replace('|', '').strip()

        # Airに保存する放送局情報を取得（検索がヒットしない場合は[None]が入ってDBには[null]で保存されるはず）
        broadcaster_search_index = share_text_to_search_index(broadcaster_name)
        broadcaster = Broadcaster.objects.filter(search_index=broadcaster_search_index).first()

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # タイトルから放送局名を除去
        # rfindで後ろから「|」を検索して、それより前だけ残す
        title = title[:title.rfind('|')]
        # title = '2021年10月5日（火）24:00～25:00 | アルコ＆ピース D.C.GARAGE '
        # print(title)

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # タイトルから番組名を取得
        # findで前から「|」を検索して、それより後ろを取得 → 「| アルコ＆ピース D.C.GARAGE 」
        # 「|」を削除して、前後のスペースを除去 → 「アルコ＆ピース D.C.GARAGE」
        program_name = title[title.find('|'):].replace('|', '').strip()

        # Airに保存する番組情報を取得（検索がヒットしない場合は[None]が入ってDBには[null]で保存されるはず）
        program_search_index = share_text_to_search_index(program_name)
        program = Program.objects.filter(search_index=program_search_index).first()

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # 放送開始日時と放送終了日時を作成

        # findで前から「|」を検索して、それより前だけ残して、前後のスペースを除去 → 「2021年10月5日（火）24:00～25:00」
        title = title[:title.find('|')].strip()
        # print(title)

        # 曜日を除去 → 「2021年10月5日24:00～25:00」が残る
        title = title.replace('（月）', '').replace('（火）', '').replace('（水）', '').replace('（木）', '').replace('（金）', '').replace('（土）', '').replace('（日）', '')
        # print(title)

        # 「年」「月」「日」「:」「～」「:」を半角カンマに置換 → 「2021,10,5,24,00,25,00」
        title = title.replace('年', ',').replace('月', ',').replace('日', ',').replace(':', ',').replace('～', ',')
        # print(title)

        # 半角カンマで分割して日付を作成
        split_title = title.split(',')  # ['2021', '10', '5', '24', '00', '25', '00']
        title_date = new_date(int(split_title[0]), int(split_title[1]), int(split_title[2]))

        # 開始時間と終了時間を取得
        started_hour = int(split_title[3])
        started_minute = int(split_title[4])
        ended_hour = int(split_title[5])
        ended_minute = int(split_title[6])

        # 開始日時と終了日時どちらも24時以降は次の日にして24時間マイナスする
        if started_hour > 23:
            started = timedelta_days(title_date, 1)
            started_hour = started_hour - 24
        else:
            started = title_date

        started = new_datetime(started.year, started.month, started.day, started_hour, started_minute)

        if ended_hour > 23:
            ended = timedelta_days(title_date, 1)
            ended_hour = ended_hour - 24
        else:
            ended = title_date

        ended = new_datetime(ended.year, ended.month, ended.day, ended_hour, ended_minute)

        # - - - - - - - - - - - - - - - - - - - - - - - -
        if program_name == None or program_name == '' or started > ended:
            messages.error(self.request, 'パースエラー！ [' + share_text + ']を管理人に教えて！')  # TODO share_textをどこかに記録したい
            return super().form_invalid(form)

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # [overview_before]と[overview_after]以外をinstanceにセット
        form.instance.name = program_name
        form.instance.program = program
        form.instance.broadcaster = broadcaster
        form.instance.started = started  # 日本時刻として扱われる模様 例：datetimeで[2021-10-06 00:00:00]を登録 → DBは[2021-10-05T15:00:00Z]
        form.instance.ended = ended  # 日本時刻として扱われる模様 例：datetimeで[2021-10-06 01:00:00]を登録 → DBは[2021-10-05T16:00:00Z]

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # 放送を保存 → 続けてログイン中のユーザー情報 & デフォルト値で何卒を登録
        try:
            saved_air = form.save()
        except Exception as err:
            messages.warning(self.request, '放送登録エラー：' + str(type(err)))  # TODO とりあえずエラータイプだけ表示しているがエラー内容によって調整したい
            if broadcaster != None:
                air = Air.objects.filter(broadcaster=broadcaster, started=started).first()
                try:
                    air.nanitozo_set.create(user=self.request.user)
                except Exception as err:
                    messages.error(self.request, '何卒登録エラー：' + str(type(err)))
                    return HttpResponseRedirect(reverse('airs:detail', args=(air.id,)))
                else:
                    messages.success(self.request, '何卒！')
                    return HttpResponseRedirect(reverse('airs:detail', args=(air.id,)))
            else:
                messages.error(self.request, '登録済みの放送です')
                return super().form_invalid(form)

        saved_air.nanitozo_set.create(user=self.request.user)
        # return super().form_valid(form)
        return HttpResponseRedirect(reverse('airs:detail', args=(saved_air.id,)))


@method_decorator(login_required, name='dispatch')
class AirUpdateView(generic.UpdateView):
    model = Air
    fields = ['overview_before', 'overview_after']
    template_name = 'airs/air_update.html'

    def get_success_url(self):
        return reverse('airs:detail', kwargs={'pk': self.kwargs['pk']})


class AirDetailView(generic.DetailView):
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
