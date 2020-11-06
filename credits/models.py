import logging
import typing

from django.conf import settings
from django.contrib.auth import get_user_model, Group
from django.db import models

from pokemongo.models import Community

logger = logging.getLogger("django.trainerdex")
AuthUser = get_user_model()

FREE, GIFT, PERSONAL, SHARED = "FREE", "GIFT", "PERSONAL", "SHARED"
CREDIT_ACCOUNT_TYPES = [
    (FREE, _("Free")),
    (GIFT, _("Free")),
    (PERSONAL, _("Free")),
    (SHARED, _("Shared")),
]


OPEN, EXPIRED, CLOSED = "OPEN", "EXPIRED", "CLOSED"
CREDIT_ACCOUNT_STATES = [
    (OPEN, _("Open")),
    (EXPIRED, _("Expired")),
    (CLOSED, _("Closed")),
]


class Account(models.Model):
    display_name = models.CharField(max_length=128, unique=False, null=True, blank=True)
    account_type = models.TextField(
        max_length=max(len(x) for x, y in CREDIT_ACCOUNT_TYPES),
        choices=CREDIT_ACCOUNT_TYPES,
        default=PERSONAL,
    )

    # Account access can be granted to multiple people, or just one person.  I've enabled a wide
    # range of options for selecting who has access to an account. This should give me the freedom
    # to create large scoping temporary accounts (usually of type GIFT) with a large quota during
    # events to encourage extra usage. Use Account.get_all_authorized_users() or
    # Account.user_has_permission(user: AuthUser) to check if a user can access and account.
    primary_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, models.SET_NULL, related_name="accounts"
    )
    secondary_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    groups = models.ManyToManyField(Group, blank=True)
    communities = models.ManyToManyField(Community, blank=True)

    status = models.TextField(
        max_length=max(len(x) for x, y in CREDIT_ACCOUNT_STATES),
        choices=CREDIT_ACCOUNT_STATES,
        default=OPEN,
    )

    # This is the amount of credits (units) an account can go into debt by. The default is 0,
    # but accounts with post-pay billing enabled will have a credit limit other than 0.
    # It's possible to grant an unlimited credit limit, but I don't think I will unless I trust
    # the user.
    credit_limit = models.IntegerField(default=0, null=True, blank=True)

    # For performance, we keep a cached balance. This can always be recalculated from the transactions.
    balance = models.IntegerField(default=0, null=True)

    # Accounts can have an date range to indicate when they are 'active'.
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return "{} by {} ({}-{})".format(
            self.display_name or "Account", self.get_primary_user(), self.account_type, self.status
        )

    def is_active(self):
        if self.start_date is None and self.end_date is None:
            return True
        now = timezone.now()
        if self.start_date and self.end_date is None:
            return now >= self.start_date
        if self.start_date is None and self.end_date:
            return now < self.end_date
        return self.start_date <= now < self.end_date

    def get_primary_user(self) -> AuthUser:
        return self.primary_user

    def get_all_authorized_users(self) -> typing.Iterable[AuthUser]:
        queryset = AuthUser.objects.none()
        queryset |= AuthUser.objects.filter(pk=self.get_primary_user().pk)
        queryset |= self.secondary_users
        for group in self.groups.all():
            queryset |= groups.user_set.all()
        for community in self.communities.all():
            queryset |= AuthUser.objects.filter(trainer__in=community.get_members())
        return queryset

    def user_has_permission(self, user: AuthUser) -> bool:
        return self.get_all_authorized_users().filter(pk=user.pk).exists()

    def save(self, *args, **kwargs):
        # Ensure the balance is always correct when saving
        self.balance = self._balance()
        return super().save(*args, **kwargs)

    def _balance(self):
        aggregates = self.transactions.aggregate(sum=Sum("amount"))
        sum = aggregates["sum"]
        return 0 if sum is None else sum

    def num_transactions(self):
        return self.transactions.all().count()

    @property
    def has_credit_limit(self):
        return self.credit_limit is not None

    def is_debit_permitted(self, amount):
        """
        Test if the a debit for the passed amount is permitted
        """
        if self.amount_available is None:
            return True
        return amount <= self.amount_available

    @property
    def amount_available(self):
        if self.credit_limit is None:
            return None
        return self.balance + self.credit_limit

    def is_open(self):
        return self.status == OPEN

    def is_closed(self):
        return self.status == CLOSED

    def is_frozen(self):
        return self.status == FROZEN


# TODO: Add Transfer model, see django-oscar-accounts for inspo
# https://github.com/django-oscar/django-oscar-accounts/blob/master/src/oscar_accounts/abstract_models.py#L323

# TODO: Add Transaction model, see django-oscar-accounts for inspo
# https://github.com/django-oscar/django-oscar-accounts/blob/master/src/oscar_accounts/abstract_models.py#L426
