from gyms.views import GymView
from django.conf.urls import url

urlpatterns = [
    url(
        regex=r'^$',
        view=GymView.as_view(),
        name='gym-list',
    ),
]
