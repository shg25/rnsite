from django.urls import path

from . import views

app_name = 'airs'
urlpatterns = [
    # 放送一覧
    path('', views.IndexView.as_view(), name='index'),
    # 何卒一覧
    path('nanitozo/', views.NanitozoView.as_view(), name='nanitozo'),
    # リスナー一覧
    path('users/', views.UsersView.as_view(), name='users'),
    # 放送局一覧
    path('broadcasters/', views.BroadcastersView.as_view(), name='broadcasters'),
    # 番組一覧
    path('programs/', views.ProgramsView.as_view(), name='programs'),
    # 出演者一覧
    path('casts/', views.CastsView.as_view(), name='casts'),

    # 放送詳細 ex: '/1/'
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),

    # 削除予定 /airs/5/results/
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # 削除予定 /airs/5/vote/
    path('<int:air_id>/vote/', views.vote, name='vote'),
]
