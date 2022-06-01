from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from rest_framework.request import Request


class BaseHandler:
    def __init__(self, request: Request, *args, **kwargs) -> None:
        ...

    def get_queryset(self) -> QuerySet:
        ...

    def format_data(self, queryset: QuerySet) -> Any:
        ...

    @classmethod
    def get_data(cls, request: Request, *args, **kwargs) -> Any:
        obj = cls(request, *args, **kwargs)
        queryset = obj.get_queryset()
        data = obj.format_data(queryset)
        return data
