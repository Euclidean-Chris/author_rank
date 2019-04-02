from django.conf.urls import url
from django.urls import path

from . import views

app_name = 'Author Ranking'
urlpatterns = [
    path('', views.index, name='index'),
    url(r'^$', views.index, name="index"),
    url(r'^search-author/', views.search_author),
]