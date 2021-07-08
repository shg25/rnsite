from django.urls import path

from . import views

app_name = 'airs'
urlpatterns = [
    # 何卒一覧
    path('ns/', views.NsView.as_view(), name='ns'),
    # 何卒作成
    path('n/create/', views.NCreateView.as_view(), name='n_create'),
    # 何卒修正
    path('n/update/', views.NUpdateView.as_view(), name='n_update'),

    # リスナー一覧
    path('users/', views.UsersView.as_view(), name='users'),
    # 放送局一覧
    path('broadcasters/', views.BroadcastersView.as_view(), name='broadcasters'),
    # 番組一覧
    path('programs/', views.ProgramsView.as_view(), name='programs'),
    # 出演者一覧
    path('casts/', views.CastsView.as_view(), name='casts'),

    # リスナー詳細 TODO キーをユーザー名にする
    path('user/<int:pk>/', views.UserView.as_view(), name='user'),
    # 放送局詳細 TODO キーを放送局の略称にする
    path('broadcaster/<int:pk>/', views.BroadcasterView.as_view(), name='broadcaster'),
    # 番組詳細 TODO キーを番組名ハッシュタグにしたいな
    path('program/<int:pk>/', views.ProgramView.as_view(), name='program'),
    # 出演者詳細 TODO これはIDでいいかなって気もするし微妙な気もする…SNSのIDとか？
    path('cast/<int:pk>/', views.CastView.as_view(), name='cast'),
    
    # 放送一覧
    path('', views.IndexView.as_view(), name='index'),
    # 放送詳細 ex: '/1/'
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),


    # 削除予定 /airs/5/results/
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # 削除予定 /airs/5/vote/
    path('<int:air_id>/vote/', views.vote, name='vote'),
]
