from django.urls import path

from .views import air_views

app_name = 'airs'
urlpatterns = [
    # 何卒一覧
    path('ns/', air_views.NsView.as_view(), name='ns'),
    # 何卒修正（ログイン必須）
    path('nanitozo/update/<int:pk>', air_views.NanitozoUpdateView.as_view(), name='nanitozo_update'),

    # リスナー一覧
    path('users/', air_views.UsersView.as_view(), name='users'),
    # 放送局一覧
    path('broadcasters/', air_views.BroadcastersView.as_view(), name='broadcasters'),
    # 番組一覧
    path('programs/', air_views.ProgramsView.as_view(), name='programs'),

    # リスナー詳細 TODO キーをユーザー名にする
    path('user/<int:pk>/', air_views.UserView.as_view(), name='user'),
    # 放送局詳細 TODO キーを放送局の略称にする
    path('broadcaster/<int:pk>/', air_views.BroadcasterView.as_view(), name='broadcaster'),
    # 番組詳細 TODO キーを番組名ハッシュタグにしたいな
    path('program/<int:pk>/', air_views.ProgramView.as_view(), name='program'),

    # 放送作成 & 何卒作成（ログイン必須）
    path('air/create/', air_views.AirCreateByShareTextView.as_view(), name='air_create'),
    # 放送更新（ログイン必須）
    path('air/update/<int:pk>', air_views.AirUpdateView.as_view(), name='air_update'),
    # 放送一覧
    path('', air_views.IndexView.as_view(), name='index'),
    # 放送詳細 ex: '/1/'
    path('<int:pk>/', air_views.DetailView.as_view(), name='detail'),

    # 既存の放送に何卒作成（ログイン必須）
    path('<int:air_id>/nanitozo/create/', air_views.nanitozo_create, name='nanitozo_create'),
    # 何卒取消（ログイン必須）
    path('<int:air_id>/nanitozo/delete/<int:pk>', air_views.nanitozo_delete, name='nanitozo_delete'),

    # 削除予定 /airs/5/results/
    path('<int:pk>/results/', air_views.ResultsView.as_view(), name='results'),
    # 削除予定 /airs/5/vote/
    path('<int:air_id>/vote/', air_views.vote, name='vote'),
]
