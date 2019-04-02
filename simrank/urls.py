"""simrank URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

from simranking import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('author-ranking/', include(('simranking.urls','author-ranking'), namespace="simranking")),
    path('author-ranking/<author>/', views.get_single_author, name='author-detail'),
    # url(r'^(?P<author-ranking>[0-9]+)$', views.get_single_author, name='author_detail')
]
admin.site.site_header = 'Simrank'