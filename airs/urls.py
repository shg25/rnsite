from django.urls import path

from . import views

app_name = 'airs'
urlpatterns = [
    # ex: /airs/
    path('', views.IndexView.as_view(), name='index'),
    # ex: /airs/
    path('nanitozo/', views.NanitozoView.as_view(), name='nanitozo'),
    # ex: /airs/5/
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # ex: /airs/5/results/
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # ex: /airs/5/vote/
    path('<int:air_id>/vote/', views.vote, name='vote'),
]
