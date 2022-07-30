from django.urls import path

from ocr.views import ActivityViewOCR

app_name = "ocr"

urlpatterns = [
    path(
        "activity-view/",
        ActivityViewOCR.as_view(),
    ),
]
