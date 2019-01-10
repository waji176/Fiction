"""Fiction URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from app01 import views as app01
import xadmin

xadmin.autodiscover()
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', app01.index),
    url(r'^fiction/$', app01.fiction),
    url(r'^chapter_content/$', app01.chapter_content),
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^itunes-store-web-service-search/', app01.itunes_store_web_service_search),
    url(r'^hentai/', app01.hentaiindex),
    url(r'^hentai_doujinshi_manga/', app01.hentai_doujinshi_manga),
    url(r'^hentai_statistics/', app01.hentai_statistics),
    url(r'^images/', app01.images),
    url(r'^comics/', app01.comics),
    url(r'^hentai2read/', app01.hentai2read),
    url(r'^anti_theft_chain_img/', app01.anti_theft_chain_img),
    url(r'^exec_script/(\d+)/(.+)/', app01.exec_script),
]
