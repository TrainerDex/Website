from typing import Callable, Sequence, Union
from django.contrib import admin


class UUIDAdmin(admin.ModelAdmin):
    """
    This is the abstract admin class for all models that have a UUID field.
    """

    def get_fields(self, request, obj=None) -> Sequence[Union[Callable, str]]:
        """
        Return a list of all the fields for the model.
        """
        if obj:
            return tuple(super().get_fields(request, obj)) + ("uuid",)
        return super().get_fields(request, obj)

    def get_readonly_fields(self, request, obj=None) -> Sequence[Union[Callable, str]]:
        """
        Return a list of all the readonly fields for the model.
        """
        if obj:
            return tuple(super().get_readonly_fields(request, obj)) + ("uuid",)
        return super().get_readonly_fields(request, obj)


class DatedAdmin(admin.ModelAdmin):
    def get_fields(self, request, obj=None) -> Sequence[Union[Callable, str]]:
        """
        Return a list of all the fields for the model.
        """
        if obj:
            return tuple(super().get_fields(request, obj)) + ("created_at", "updated_at")
        return super().get_fields(request, obj)
