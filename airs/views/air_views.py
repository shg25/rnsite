from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.decorators import method_decorator

from common.util.datetime_extensions import new_datetime, new_date, timedelta_days
from common.util.url_extensions import scraping_title
from common.util.log_extensions import logger_share_text
from common.util.string_extensions import find_urls, share_text_to_formatted_name
from common.util.enum.nanitozo_icon_type_extensions import NanitozoIconType

from ..models import Air, FormattedName
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
    # queryset = Air.objects.filter(started_at__gte=this_week_started()).order_by('-started_at') # これを使えばviewではair_listで取得できるがなぜかキャッシュらしきものが残るので一旦使わない

    def get_context_data(self, *args, **kwargs):
        # TODO 2週間分を別々に取得しないで、一気に2週間分取得してそれぞれのリストに振り分ける → TODO オススメも書き出す
        context = super().get_context_data(*args, **kwargs)
        context['this_week_list'] = Air.objects_this_week.all()
        context['last_week_list'] = Air.objects_last_week.all()

        # TODO オススメ放送取得（1/3）
        # context['recommend_list'] = Air.objects.filter(started_at__range=(last_week_started(), timezone.now())).order_by('-started_at')

        return context
        # TODO  全面的に filter(started_at__lte=timezone.now()) の値を調整する、実際は事前登録も可とするので、現在時刻との比較は不要


@login_required_only_general_member()
class AirCreateByShareTextView(generic.FormView):
    template_name = 'airs/air_create.html'
    form_class = AirCreateByShareTextForm
    success_url = '/'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # 投稿したシェアテキストを取得 TODO 一時的にoverview_beforeから取得しているので修正する
        share_text = form.cleaned_data['overview_before']
        # share_text = 'アルコ＆ピース D.C.GARAGE | TBSラジオ | 2021/10/05/火  24:00-25:00 https://radiko.jp/share/?sid=TBS&t=20211006000000' # 例1

        # 投稿したシェアテキストはそのままログに記録する
        print('printの挙動確認用：' + share_text)  # テスト
        logger_share_text('loggerの挙動確認用：' + share_text)

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # [share_text]からradikoのURLを抜き出す
        urls = find_urls(share_text)
        if len(urls) == 0:
            messages.error(self.request, 'radikoのURLが見つかりません')  # TODO share_textをどこかに記録したい
            return super().form_invalid(form)

        has_radiko = False
        for url in urls:
            has_radiko = 'radiko.jp' in url
            if has_radiko:
                radiko_url = url
                break

        # radiko_url = "https://radiko.jp/share/?sid=TBS&t=20211006000000"

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # radikoのサイトからサイトタイトルを取得
        title = scraping_title(radiko_url)
        # title = '2021年10月5日（火）24:00～25:00 | アルコ＆ピース D.C.GARAGE | TBSラジオ | radiko'
        # print(title)

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # タイトルに「|」が3つ以上含まれていることを確認
        # ※タイトルにも含まれる可能性があるので3以上は許可
        if title.count('|') < 3:
            # print('「|」が3つない')
            if 'この番組の配信は終了しました' in title:
                messages.error(self.request, '配信が終了した放送\nどうにか登録したいならサイト管理者に相談を')
            else:
                messages.error(self.request, 'なぜかエラー！\n送信内容をサイト管理者に伝えてください')  # TODO share_textをどこかに記録したい
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
            started_at = timedelta_days(title_date, 1)
            started_hour = started_hour - 24
        else:
            started_at = title_date

        started_at = new_datetime(started_at.year, started_at.month, started_at.day, started_hour, started_minute)

        if ended_hour > 23:
            ended_at = timedelta_days(title_date, 1)
            ended_hour = ended_hour - 24
        else:
            ended_at = title_date

        ended_at = new_datetime(ended_at.year, ended_at.month, ended_at.day, ended_hour, ended_minute)

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # Airに保存する放送局情報を取得（検索がヒットしない場合は[None]が入ってDBには[null]で保存されるはず）
        broadcaster_formatted_name = share_text_to_formatted_name(broadcaster_name)
        try:
            broadcaster_formatted_name_object = FormattedName.objects.get(name=broadcaster_formatted_name)
            broadcaster = broadcaster_formatted_name_object.broadcaster_set.first()
        except FormattedName.DoesNotExist:
            # broadcasterはFormattedNameがヒットしなくてもエラーにならないのでここを通らないはず
            broadcaster = None

        # Airに保存する番組情報を取得（検索がヒットしない場合は[None]が入ってDBには[null]で保存されるはず）
        program_formatted_name = share_text_to_formatted_name(program_name)
        try:
            program_formatted_name_object = FormattedName.objects.get(name=program_formatted_name)
            programs = program_formatted_name_object.program_set.all()
            if programs.count() == 0:
                program = None
            elif programs.count() == 1:
                program = programs.first()
            else:
                program = programs.filter(day_of_week=title_date.weekday()).first()
        except FormattedName.DoesNotExist:  # programはcatchしないとエラーになる（broadcasterはFormattedNameがヒットしなくてもなぜかエラーにならない）
            program = None

        # - - - - - - - - - - - - - - - - - - - - - - - -
        if program_name == None or program_name == '' or started_at > ended_at:
            messages.error(self.request, 'パースエラー！\n送信内容をサイト管理者に伝えてください')  # TODO share_textをどこかに記録したい
            return super().form_invalid(form)

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # [overview_before]と[overview_after]以外をinstanceにセット
        form.instance.name = program_name
        form.instance.program = program
        form.instance.broadcaster = broadcaster
        form.instance.started_at = started_at  # 日本時刻として扱われる模様 例：datetimeで[2021-10-06 00:00:00]を登録 → DBは[2021-10-05T15:00:00Z]
        form.instance.ended_at = ended_at  # 日本時刻として扱われる模様 例：datetimeで[2021-10-06 01:00:00]を登録 → DBは[2021-10-05T16:00:00Z]
        form.instance.overview_before = ''  # TODO 一時的に share_text がセットされているので空にしている

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # 放送登録
        try:
            saved_air = form.save()
        except IntegrityError:
            messages.warning(self.request, '登録済みの放送')
            if broadcaster == None:
                messages.error(self.request, '放送局情報なし\n送信内容をサイト管理者に伝えてください')
                return super().form_invalid(form)
            else:
                saved_air = Air.objects_identification.get(broadcaster=broadcaster, started_at=started_at).first()
        except Exception as err:
            messages.error(self.request, '放送登録エラー：' + str(type(err)))
            return super().form_invalid(form)
        else:
            messages.success(self.request, '放送登録完了！')

        # 何卒登録
        try:
            saved_air.nanitozo_set.create(user=self.request.user)
        except IntegrityError:
            messages.warning(self.request, '何卒済みの放送')
            return HttpResponseRedirect(reverse('airs:detail', args=(saved_air.id,)))
        except Exception as err:
            messages.error(self.request, '何卒登録エラー：' + str(type(err)))
            return HttpResponseRedirect(reverse('airs:detail', args=(saved_air.id,)))
        else:
            messages.success(self.request, '何卒！')

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

        # 対象の放送の何卒リスト
        nanitozo_list = air.nanitozo_set.all()
        context['nanitozo_list'] = nanitozo_list

        # 下書き含む
        context['good_nanitozo_list'] = list(filter(lambda x: x.good == True, nanitozo_list))

        # 下書きは含まない
        context['comment_open_recommend_nanitozo_list'] = list(filter(lambda x: x.comment_open == True and x.comment_recommend != None and len(x.comment_recommend) != 0, nanitozo_list))
        context['comment_open_nanitozo_list'] = list(filter(lambda x: x.comment_open == True and x.comment != None and len(x.comment) != 0, nanitozo_list))
        context['comment_open_negative_nanitozo_list'] = list(filter(lambda x: x.comment_open == True and x.comment_negative != None and len(x.comment_negative) != 0, nanitozo_list))

        nanitozo_icon_list = []
        for nanitozo in context['comment_open_recommend_nanitozo_list']:
            nanitozo_icon_list.append((NanitozoIconType.comment_recommend, nanitozo.user == self.request.user))
        for nanitozo in context['good_nanitozo_list']:
            nanitozo_icon_list.append((NanitozoIconType.good, nanitozo.user == self.request.user))
        for nanitozo in context['comment_open_nanitozo_list']:
            nanitozo_icon_list.append((NanitozoIconType.comment, nanitozo.user == self.request.user))
        for nanitozo in context['comment_open_negative_nanitozo_list']:
            nanitozo_icon_list.append((NanitozoIconType.comment_negative, nanitozo.user == self.request.user))
        for nanitozo in nanitozo_list:
            nanitozo_icon_list.append((NanitozoIconType.nanitozo, nanitozo.user == self.request.user))
        context['nanitozo_icon_list'] = nanitozo_icon_list

        my_nanitozo_list = list(filter(lambda x: x.user == self.request.user, nanitozo_list))
        if bool(my_nanitozo_list):
            context['my_nanitozo'] = my_nanitozo_list[0]

        context['other_nanitozo_list'] = list(filter(lambda x: x.user != self.request.user, nanitozo_list))

        return context
