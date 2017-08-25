from . import views
from django.conf.urls import url

urlpatterns = [
    url(
        regex=r'^$',
        view=views.GymView.as_view(),
        name='gym-list',
    ),
]
