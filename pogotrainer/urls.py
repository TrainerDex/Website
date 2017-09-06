"""pogotrainer URL Configuration

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
from rest_framework.urlpatterns import format_suffix_patterns
from trainer.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/1.0/faction/', FactionList.as_view()),
    url(r'^api/1.0/trainer/', TrainerList.as_view()),
    url(r'^api/1.0/user/', UserList.as_view()),
    url(r'^api/1.0/update/', UpdateList.as_view()),
    url(r'^api/1.0/discord/user/', DiscordUserList.as_view()),
    url(r'^api/1.0/discord/server/', DiscordServerList.as_view()),
    url(r'^api/1.0/discord/member/', DiscordMemberList.as_view()),
    url(r'^api/1.0/network/member/', NetworkMemberList.as_view()),
    url(r'^api/1.0/network/group/', NetworkList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)