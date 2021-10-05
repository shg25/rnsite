from django.urls import path

from . import views

app_name = 'airs'
urlpatterns = [
    # 何卒一覧
    path('ns/', views.NsView.as_view(), name='ns'),
    # 何卒修正
    path('n/update/<int:pk>', views.NUpdateView.as_view(), name='n_update'),
    # 何卒削除
    path('n/delete/<int:pk>', views.NDeleteView.as_view(), name='n_delete'),

    # リスナー一覧
    path('users/', views.UsersView.as_view(), name='users'),
    # 放送局一覧
    path('broadcasters/', views.BroadcastersView.as_view(), name='broadcasters'),
    # 番組一覧
    path('programs/', views.ProgramsView.as_view(), name='programs'),

    # リスナー詳細 TODO キーをユーザー名にする
    path('user/<int:pk>/', views.UserView.as_view(), name='user'),
    # 放送局詳細 TODO キーを放送局の略称にする
    path('broadcaster/<int:pk>/', views.BroadcasterView.as_view(), name='broadcaster'),
    # 番組詳細 TODO キーを番組名ハッシュタグにしたいな
    path('program/<int:pk>/', views.ProgramView.as_view(), name='program'),

    # 放送作成 & 何卒作成
    path('air/create/', views.AirCreateByShareTextView.as_view(), name='air_create'),
    # 放送更新
    path('air/update/<int:pk>', views.AirUpdateView.as_view(), name='air_update'),
    # 放送一覧
    path('', views.IndexView.as_view(), name='index'),
    # 放送詳細 ex: '/1/'
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),


    # 削除予定 /airs/5/results/
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # 削除予定 /airs/5/vote/
    path('<int:air_id>/vote/', views.vote, name='vote'),
]
