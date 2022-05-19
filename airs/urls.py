from django.urls import path

from .views import air_views, user_views, broadcaster_views, program_views, nanitozo_views

app_name = 'airs'
urlpatterns = [
    # リスナー一覧
    path('users/', user_views.UserListView.as_view(), name='users'),
    # リスナー詳細 TODO キーをユーザー名にする
    path('user/<int:pk>/', user_views.UserDetailView.as_view(), name='user'),

    # 放送局一覧
    path('broadcasters/', broadcaster_views.BroadcasterListView.as_view(), name='broadcasters'),
    # 放送局詳細 TODO キーを放送局の略称にする
    path('broadcaster/<int:pk>/', broadcaster_views.BroadcasterDetailView.as_view(), name='broadcaster'),

    # 番組一覧
    path('programs/', program_views.ProgramsListView.as_view(), name='programs'),
    # 番組詳細 TODO キーを番組名ハッシュタグにしたいな
    path('program/<int:pk>/', program_views.ProgramDetailView.as_view(), name='program'),

    # 何卒一覧
    path('ns/', nanitozo_views.NanitozoListView.as_view(), name='ns'),
    # 既存の放送に何卒作成（ログイン必須）
    path('<int:air_id>/nanitozo/create/', nanitozo_views.nanitozo_create, name='nanitozo_create'),
    # 何卒修正（ログイン必須）
    path('<int:air_id>/nanitozo/update/<int:pk>', nanitozo_views.nanitozo_update, name='nanitozo_update'),
    # 何卒満足（ログイン必須）
    path('<int:air_id>/nanitozo/apply_good/<int:pk>', nanitozo_views.nanitozo_apply_good, name='nanitozo_apply_good'),
    # 何卒満足キャンセル（ログイン必須）
    path('<int:air_id>/nanitozo/cancel_good/<int:pk>', nanitozo_views.nanitozo_cancel_good, name='nanitozo_cancel_good'),
    # 何卒取消（ログイン必須）
    path('<int:air_id>/nanitozo/delete/<int:pk>', nanitozo_views.nanitozo_delete, name='nanitozo_delete'),

    # 放送作成 & 何卒作成（ログイン必須）
    path('air/create/', air_views.AirCreateByShareTextView.as_view(), name='air_create'),
    # 放送更新（ログイン必須）
    path('air/update/<int:pk>', air_views.air_update, name='air_update'),
    # 放送一覧
    path('', air_views.AirListView.as_view(), name='index'),
    # 放送詳細 ex: '/1/'
    path('<int:pk>/', air_views.AirDetailView.as_view(), name='detail'),
]
