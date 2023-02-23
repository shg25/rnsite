import json

from urllib.parse import unquote

from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect

from common.util.enum.status_type import StatusType
from common.util.datetime_extensions import new_datetime, new_date, timedelta_days, this_week_started, output_ymdhm
from common.util.url_extensions import scraping_title
from common.util.log_extensions import logger_share_text
from common.util.string_extensions import find_urls, share_text_to_formatted_name

from ..models import Air, FormattedName
from ..forms import AirCreateByShareTextForm, AirUpdateForm


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
        context = super().get_context_data(*args, **kwargs)

        two_week_list = Air.objects_two_week.all()
        context['this_week_list'] = list(filter(lambda x: x.started_at >= this_week_started(), two_week_list))
        context['last_week_list'] = list(filter(lambda x: x.started_at < this_week_started(), two_week_list))

        if self.request.user:
            my_this_week_list = []
            for item in context['this_week_list']:
                nanitozo_list = item.nanitozo_set.all()
                my_nanitozo_list = list(filter(lambda x: x.user == self.request.user, nanitozo_list))
                if bool(my_nanitozo_list):
                    my_this_week_list.append(item)
            context['my_this_week_list'] = my_this_week_list

            my_last_week_list = []
            for item in context['last_week_list']:
                nanitozo_list = item.nanitozo_set.all()
                my_nanitozo_list = list(filter(lambda x: x.user == self.request.user, nanitozo_list))
                if bool(my_nanitozo_list):
                    my_last_week_list.append(item)
            context['my_last_week_list'] = my_last_week_list

            un_nanitozo_list = []
            for item in context['my_last_week_list']:
                if item.un_nanitozo_this_week(context['my_this_week_list']):
                    un_nanitozo_list.append(item)
            context['un_nanitozo_list'] = un_nanitozo_list

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
        # print('printの挙動確認用：' + share_text)  # テスト
        logger_share_text(share_text)

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # [share_text]からradikoのURLを抜き出す
        result = pickRadikoUrlFromShareText(share_text)
        # share_textに問題があればエラーメッセージを表示
        if result['status'] == StatusType.fail.value:
            messages.error(self.request, result['data']['title'])
            return super().form_invalid(form)

        radiko_url = result['data']['radiko_url']
        # radiko_url = "https://radiko.jp/share/?sid=TBS&t=20211006000000"

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # radikoのサイトからサイトタイトルを取得
        title = scraping_title(radiko_url)
        # title = '2021年10月5日（火）24:00～25:00 | アルコ＆ピース D.C.GARAGE | TBSラジオ | radiko'
        # print(title)

        # - - - - - - - - - - - - - - - - - - - - - - - -
        result = pickAirFromRadikoPageTitle(title)

        # パース処理でエラーがあれば処理を中断してエラーメッセージを表示
        if result['status'] == StatusType.error.value:
            messages.error(self.request, result['message'])
            return super().form_invalid(form)

        dict = result['data']

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # [overview_before]と[overview_after]以外をinstanceにセット
        form.instance.name = dict['program_name']
        form.instance.program = dict['program']
        form.instance.broadcaster = dict['broadcaster']
        form.instance.started_at = dict['started_at']  # 日本時刻として扱われる模様 例：datetimeで[2021-10-06 00:00:00]を登録 → DBは[2021-10-05T15:00:00Z]
        form.instance.ended_at = dict['ended_at']  # 日本時刻として扱われる模様 例：datetimeで[2021-10-06 01:00:00]を登録 → DBは[2021-10-05T16:00:00Z]
        form.instance.overview_before = ''  # TODO 一時的に share_text がセットされているので空にしている

        # - - - - - - - - - - - - - - - - - - - - - - - -
        # 放送登録
        try:
            saved_air = form.save()
        except IntegrityError:
            messages.warning(self.request, '登録済みの放送')
            if form.instance.broadcaster == None:
                messages.error(self.request, '放送局情報なし\n送信内容をサイト管理者に伝えてください')
                return super().form_invalid(form)
            else:
                # 引き続き何卒登録のために登録済みの放送を取得する
                saved_air = Air.objects_identification.get(broadcaster=form.instance.broadcaster, started_at=form.instance.started_at).first()
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


def pickRadikoUrlFromShareText(share_text):
    urls = find_urls(share_text)

    if len(urls) == 0:
        return {
            'status': StatusType.fail.value,
            'data': {
                'title': 'URLが見つかりません'
            }
        }

    has_radiko = False
    for url in urls:
        has_radiko = 'radiko.jp' in url
        if has_radiko:
            radiko_url = url
            break

    if not has_radiko:
        return {
            'status': StatusType.fail.value,
            'data': {
                'title': 'radikoのURLが見つかりません'
            }
        }

    return {
        'status': StatusType.success.value,
        'data': {
            'radiko_url': radiko_url
        }
    }


def pickAirFromRadikoPageTitle(title):
    # タイトルに「|」が3つ以上含まれていることを確認
    # ※タイトルにも含まれる可能性があるので3以上は許可
    if title.count('|') < 3:
        # print('「|」が3つない')
        if 'この番組の配信は終了しました' in title:
            message = '配信が終了した放送\nどうにか登録したいならサイト管理者に相談を'
        else:
            message = 'なぜかエラー！\n送信内容をサイト管理者に伝えてください'
        return {
            'status': StatusType.error.value,
            'message': message
        }

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

    # データとして破綻がないか確認
    if program_name == None or program_name == '' or started_at > ended_at:
        return {
            'status': StatusType.error.value,
            'message': 'パースエラー！\n送信内容をサイト管理者に伝えてください'
        }

    return {
        'status': StatusType.success.value,
        'data': {
            'program_name': program_name,
            'program': program,
            'broadcaster': broadcaster,
            'started_at': started_at,  # 日本時刻として扱われる模様 例：datetimeで[2021-10-06 00:00:00]を登録 → DBは[2021-10-05T15:00:00Z]
            'ended_at': ended_at,  # 日本時刻として扱われる模様 例：datetimeで[2021-10-06 01:00:00]を登録 → DBは[2021-10-05T16:00:00Z]
        }
    }


@login_required
def air_create_url_check(_, encoded_radiko_url):
    title = scraping_title(unquote(encoded_radiko_url))  # '2021年10月5日（火）24:00～25:00 | アルコ＆ピース D.C.GARAGE | TBSラジオ | radiko'
    result = pickAirFromRadikoPageTitleApi(title)
    json_str = json.dumps(result, ensure_ascii=False, indent=2)  # json形式に変換
    return HttpResponse(json_str)


def pickAirFromRadikoPageTitleApi(title):
    result = pickAirFromRadikoPageTitle(title)
    # 成功した場合はデータを整形（オブジェクトを全て文字列に置換） TODO ValueObject的なもの（data class?）を用意した方がいいかも
    if result['status'] == StatusType.success.value:
        if result['data']['program'] != None:
            result['data']['program'] = result['data']['program'].name
        if result['data']['broadcaster'] != None:
            result['data']['broadcaster'] = result['data']['broadcaster'].name
        result['data']['started_at'] = output_ymdhm(result['data']['started_at'])
        result['data']['ended_at'] = output_ymdhm(result['data']['ended_at'])
    return result


@login_required
def air_update(request, pk):
    if request.method != 'POST':
        return HttpResponseNotAllowed('POSTじゃないと')  # NOTE テストコードを実行するとなぜかここだけログが表示されるのが気になる、HttpResponseBadRequestとかに変えても同じ

    air = get_object_or_404(Air, pk=pk)
    form = AirUpdateForm(request.POST, instance=air)
    if form.is_valid():
        form.save()
        messages.success(request, '更新完了！')
    else:
        messages.error(request, '更新失敗！')
    return redirect('airs:detail', pk=pk)


class AirDetailView(generic.DetailView):
    model = Air

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
