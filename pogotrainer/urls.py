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
from django.conf.urls import url, include
from django.contrib import admin
from api.resources import *

levels_resource = Trainer_Levels_Resource()
trainers_resource = Trainers_Resource()
xp_resource = Experience_Resource()
discordUsers_resource = Discordian_Resource()
discordMembers_resource = Discordian_On_Servers_Resource()
discordServers_resource = Servers_Resource()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
	url(r'api/', include(trainers_resource.urls)),
]
