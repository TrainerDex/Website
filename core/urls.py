from django.urls import path

from core.views import terms

app_name = "core"

urlpatterns = [
    path('terms', terms, name='terms')
]
