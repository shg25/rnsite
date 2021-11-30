from django.views import generic
from django.contrib.auth.models import User


class UserListView(generic.ListView):
    model = User
    # NOTE ページネーションなしで問題ない範囲しかユーザーを登録しない想定
    # TODO ユーザー名昇順で表示
    # TODO 何卒した日時を保存して降順で表示（DjangoのAuthで可能であれば）


class UserDetailView(generic.DetailView):
    model = User
