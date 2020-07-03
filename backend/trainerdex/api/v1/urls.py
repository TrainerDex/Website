from django.urls import path

from trainerdex.api.v1.views import LatestUpdateView, SocialLookupView, TrainerDetailView, TrainerListView, UpdateDetailView, UpdateListView, UserViewSet

app_name = "trainerdex.api.1"

urlpatterns = [
    # /trainers/
    path('trainers/', TrainerListView.as_view()),
    path('trainers/<int:pk>/', TrainerDetailView.as_view()),
    path('trainers/<int:pk>/updates/', UpdateListView.as_view()),
    path('trainers/<int:pk>/updates/latest/', LatestUpdateView.as_view(), name='latest_update'),
    path('trainers/<int:pk>/updates/<uuid:uuid>/', UpdateDetailView.as_view()),
    # /users/
    path('users/', UserViewSet.as_view({'get': 'list'})),
    path('users/<int:pk>/', UserViewSet.as_view({'get': 'retrieve'})),
    path('users/social/', SocialLookupView.as_view()),
]
