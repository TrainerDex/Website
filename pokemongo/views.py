from __future__ import annotations

import logging
from datetime import timedelta
from math import ceil
from typing import TYPE_CHECKING, Callable

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Max, OuterRef, Q, QuerySet, Subquery, Sum, Window
from django.db.models.functions import DenseRank
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_countries import countries

from pokemongo.fields import BaseStatistic
from pokemongo.forms import TrainerForm, UpdateForm
from pokemongo.models import (
    BATTLE_HUB_STATS,
    STANDARD_MEDALS,
    UPDATE_FIELDS_TYPES,
    Community,
    Trainer,
    Update,
)
from pokemongo.shortcuts import filter_leaderboard_qs

logger = logging.getLogger("django.trainerdex")

if TYPE_CHECKING:
    from django.contrib.auth.models import User


def _check_if_trainer_valid(user: User) -> bool:
    verified = user.trainer.verified
    logger.debug(
        msg="Checking {nickname}: Completed profile: {status}".format(
            nickname=user.username, status=verified
        ),
    )
    return verified


def _check_if_self_valid(request: HttpRequest) -> bool:
    valid = _check_if_trainer_valid(request.user)
    if valid and request.user.trainer.start_date is None:
        messages.warning(
            request,
            _(
                "Please set your trainer start date. You can edit your profile in the settings section on the menu."
            ),
        )
    return valid


def profile_redirector(
    request: HttpRequest,
    nickname: str | None = None,
    id: int | None = None,
) -> HttpResponse:

    BASE_QUERYSET: QuerySet[Trainer] = (
        Trainer.objects.filter(owner__is_active=True)
        .prefetch_related(
            "update_set",
        )
        .annotate(
            level=Max(
                "update__trainer_level",
                filter=Q(**{"update__trainer_level__isnull": False}),
            )
        )
    )

    if nickname or (nickname := request.GET.get("nickname")):
        try:
            trainer = BASE_QUERYSET.get(nickname__nickname__iexact=nickname)
        except Trainer.DoesNotExist:
            raise Http404("Trainer not found")

        if nickname == trainer.nickname:
            return profile_view(request, trainer)
    elif id or (id := request.GET.get("id")):
        try:
            trainer = BASE_QUERYSET.get(pk=id)
        except Trainer.DoesNotExist:
            raise Http404("Trainer not found")
    elif not request.user.is_authenticated:
        return redirect("account_login")
    else:
        return redirect("trainerdex:profile", **{"nickname": request.user.username})

    return redirect("trainerdex:profile", permanent=True, **{"nickname": trainer.nickname})


def profile_view(request: HttpRequest, trainer: Trainer) -> HttpResponse:
    if request.user.is_authenticated and not _check_if_self_valid(request):
        messages.warning(request, _("Please complete your profile to continue using the website."))
        return redirect("profile_edit")

    updates = trainer.update_set.all()
    stats = trainer.update_set.aggregate(
        **{
            field.name: Max(
                field.name,
                filter=Q(**{f"{field.name}__isnull": False}),
            )
            for field in Update.get_stat_fields()
        }
    )
    level = trainer.get_level()
    medal_data = {field.name: field.medal_data for field in Update.get_stat_fields()}

    context = {
        "trainer": trainer,
        "updates": updates,
        "stats": stats,
        "level": level,
        "medal_data": medal_data,
    }

    context["bronze_medals"] = len(
        [
            True
            for name, medal in medal_data.items()
            if medal.bronze and stats.get(name) and medal.bronze >= stats.get(name)
        ]
    )
    context["silver_medals"] = len(
        [
            True
            for name, medal in medal_data.items()
            if medal.silver and stats.get(name) and medal.silver >= stats.get(name)
        ]
    )
    context["gold_medals"] = len(
        [
            True
            for name, medal in medal_data.items()
            if medal.gold and stats.get(name) and medal.gold >= stats.get(name)
        ]
    )
    context["platinum_medals"] = len(
        [
            True
            for name, medal in medal_data.items()
            if medal.platinum and stats.get(name) and medal.platinum >= stats.get(name)
        ]
    )
    context["medals_count"] = len(
        [True for name, medal in medal_data.items() if medal.platinum and stats.get(name)]
    )

    return render(request, "profile.html", context)


@login_required
def new_update(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated and not _check_if_self_valid(request):
        messages.warning(request, _("Please complete your profile to continue using the website."))
        return redirect("profile_edit")

    try:
        existing = request.user.trainer.update_set.filter(
            update_time__gte=timezone.now() - timedelta(hours=6)
        ).latest("update_time")
    except Update.DoesNotExist:
        existing = None

    if existing:
        if request.method == "POST":
            form = UpdateForm(request.POST, instance=existing)
        else:
            form = UpdateForm(
                instance=existing,
                initial={
                    "trainer": request.user.trainer,
                    "data_source": "web_detailed",
                },
            )
    else:
        if request.method == "POST":
            form = UpdateForm(
                request.POST,
                initial={
                    "trainer": request.user.trainer,
                    "data_source": "web_detailed",
                },
            )
        else:
            form = UpdateForm(
                initial={"trainer": request.user.trainer, "data_source": "web_detailed"}
            )
    form.fields["update_time"].widget = forms.HiddenInput()
    form.fields["data_source"].widget = forms.HiddenInput()
    form.fields["data_source"].disabled = True
    form.fields["trainer"].widget = forms.HiddenInput()
    form.trainer = request.user.trainer

    def sort_by_medal(queryset: QuerySet[Trainer]) -> Callable[[BaseStatistic], float]:
        def _sort_by_medal(stat: BaseStatistic) -> float:
            value = queryset.get(stat.name, None)
            medal = stat.medal_data
            print(medal, value)
            if value is None:
                return (5, medal.stat_id)
            elif medal.platinum and medal.platinum <= value:
                return (1, medal.stat_id)
            elif medal.gold and medal.gold <= value:
                return (2, medal.stat_id)
            elif medal.silver and medal.silver <= value:
                return (3, medal.stat_id)
            else:
                return (4, medal.stat_id)

        return _sort_by_medal

    latest_stats = Trainer.objects.filter(pk=request.user.trainer.pk).aggregate(
        **{
            field.name: Max(
                f"update__{field.name}",
                filter=Q(**{f"update__{field.name}__isnull": False}),
            )
            for field in STANDARD_MEDALS + BATTLE_HUB_STATS + UPDATE_FIELDS_TYPES
        },
    )

    try:

        form.order_fields(
            [
                "trainer",
                "update_time",
                "data_source",
                "trainer_level",
                "total_xp",
                "gym_gold",
                "mini_collection",
            ]
            + [field.name for field in sorted(STANDARD_MEDALS, key=sort_by_medal(latest_stats))]
            + [field.name for field in BATTLE_HUB_STATS]
            + [
                field.name
                for field in sorted(UPDATE_FIELDS_TYPES, key=sort_by_medal(latest_stats))
            ]
        )
    except Exception:
        pass

    if request.method == "POST":
        form.data_source = "web_detailed"
        if form.is_valid():
            form.save()
            messages.success(request, _("Statistics updated"))
            return redirect(
                "trainerdex:profile",
                **{"nickname": request.user.trainer.nickname},
            )

    if existing:
        messages.info(
            request,
            _(
                "Since you have posted in the past hour, you are currently updating your previous post."
            ),
        )

    context = {
        "form": form,
    }
    return render(request, "create_update.html", context)


def leaderboard(
    request: HttpRequest,
    country: str | None = None,
    community: str | None = None,
) -> HttpResponse:
    context = {}

    if country:
        try:
            context["title"] = dict(countries)[country.upper()]
        except KeyError:
            raise Http404(_("No country found for code {country}").format(country=country))
        queryset = Trainer.objects.filter(country=country.upper())
    elif community:
        try:
            community = Community.objects.get(handle__iexact=community)
        except Community.DoesNotExist:
            if not request.user.is_authenticated:
                return redirect(
                    "{0}?next={1}".format(
                        reverse("account_login"),
                        reverse("trainerdex:leaderboard", **{"community": community}),
                    )
                )
            raise Http404(
                _("No community found for handle {community}").format(community=community)
            )

        if not community.privacy_public and not request.user.is_superuser:
            if (not request.user.is_authenticated) or (
                not community.get_members().filter(id=request.user.trainer.id).exists()
            ):
                raise Http404(_("Access denied"))

        context["title"] = community.name
        queryset = community.get_members()
    else:
        context["title"] = None
        queryset = Trainer.objects

    queryset = filter_leaderboard_qs(queryset)

    fields_to_calculate_max = {
        "total_xp",
        "capture_total",
        "travel_km",
        "pokestops_visited",
        "gym_gold",
        "update_time",
    }

    if order_by := request.GET.get("sort", "total_xp"):
        if (
            isinstance((order_by_field := Update._meta.get_field(order_by)), BaseStatistic)
            and order_by_field.sortable
        ):
            fields_to_calculate_max.add(order_by)
        else:
            order_by = "total_xp"
    context["sort_by"] = order_by
    context["stat_name"] = Update._meta.get_field(order_by).verbose_name

    totals = queryset.annotate(order_by=Max(f"update__{order_by}")).aggregate(
        grand_stat=Sum("order_by"),
        grand_total_users=Count("id"),
    )
    context["grand_total_users"] = total_users = totals["grand_total_users"]
    context["grand_stat"] = totals["grand_stat"]

    if total_users == 0:
        context["page"] = 0
        context["pages"] = 0
        context["leaderboard"] = None
        return render(request, "leaderboard.html", context, status=404)

    queryset = queryset.annotate(
        level=Subquery(
            Update.objects.filter(trainer=OuterRef("pk"), **{f"{order_by}__isnull": False})
            .values("trainer_level")
            .order_by("-update_time")[:1]
        ),
        **{
            f"max_{field}": Subquery(
                Update.objects.filter(trainer=OuterRef("pk"), **{f"{order_by}__isnull": False})
                .values(field)
                .order_by("-update_time")[:1]
            )
            for field in fields_to_calculate_max
        },
    )

    try:
        page = int(request.GET.get("page") or 1)
    except ValueError:
        page = 1
    context["page"] = page
    PAGE_SIZE = 100
    context["pages"] = ceil(total_users / PAGE_SIZE)

    results = []

    queryset = (
        queryset.annotate(
            rank=Window(
                expression=DenseRank(),
                order_by=F(f"max_{order_by}").desc(),
            )
        )
        .order_by(
            "rank",
            "max_update_time",
            "faction",
        )
        .only(
            "id",
            "_nickname",
            "country",
            "faction",
        )
    )

    queryset_chunk = queryset[(page - 1) * PAGE_SIZE : page * PAGE_SIZE]
    for trainer in queryset_chunk:
        print(trainer)
        trainer_stats = {
            "position": trainer.rank,
            "trainer": trainer,
            "total_xp": trainer.max_total_xp,
            "update_time": trainer.max_update_time,
            "level": trainer.level,
        }

        FIELDS = fields_to_calculate_max.copy()
        FIELDS = [
            {
                "name": field.name,
                "readable_name": field.verbose_name,
                "tooltip": field.help_text,
                "value": getattr(trainer, f"max_{field.name}"),
            }
            for field in Update.get_sortable_fields()
            if field.name in FIELDS
        ]
        FIELDS = sorted(FIELDS, key=lambda x: 0 if x["name"] == order_by else 1)
        trainer_stats["columns"] = FIELDS
        results.append(trainer_stats)

    context["leaderboard"] = results

    return render(request, "leaderboard.html", context)


@login_required
def edit_profile(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated and _check_if_self_valid(request):
        if request.user.trainer.update_set.count() == 0:
            messages.warning(request, "You have not posted your stats yet.")

    form = TrainerForm(instance=request.user.trainer)

    if request.method == "POST":
        form = TrainerForm(request.POST, request.FILES, instance=request.user.trainer)
        if form.is_valid():
            if form.has_changed():
                form.save()
                if not request.user.trainer.verified:
                    messages.success(
                        request,
                        _(
                            "Thank you for filling out your profile."
                            " Your screenshots have been sent for verification."
                            " Join our Discord. https://discord.gg/Anz3UpM"
                        ),
                    )
                    return redirect("trainerdex:update_stats")
                else:
                    messages.success(request, _("Profile edited successfully."))
                    return redirect("account_settings")
    return render(request, "edit_profile.html", {"form": form})
