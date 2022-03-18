from typing import Literal

from allauth.account.adapter import DefaultAccountAdapter
from django.http import HttpRequest


class NoNewUsersAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest) -> Literal[False]:
        return False
