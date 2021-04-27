from django.urls import path

from . import views

app_name = 'airs'
urlpatterns = [
    # ex: /airs/
    path('', views.index, name='index'),
    # ex: /airs/5/
    path('<int:air_id>/', views.detail, name='detail'),
    # ex: /airs/5/results/
    path('<int:air_id>/results/', views.results, name='results'),
    # ex: /airs/5/vote/
    path('<int:air_id>/vote/', views.vote, name='vote'),
]
