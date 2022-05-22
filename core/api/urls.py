from django.urls import path

from core.api.views import ServiceDetailView, ServiceListView

app_name = "core.api"

urlpatterns = [
    path("services/", ServiceListView.as_view(), name="service_list"),
    path("services/<int:pk>/", ServiceDetailView.as_view(), name="service_detail"),
]
