from __future__ import annotations

import logging
from datetime import timedelta
from math import ceil
from typing import TYPE_CHECKING

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Max, Sum, Window, Subquery, OuterRef
from django.db.models.functions import DenseRank
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from pokemongo.forms import TrainerForm, UpdateForm
from pokemongo.models import Community, Trainer, Update
from pokemongo.shortcuts import (
    BADGES,
    UPDATE_SORTABLE_FIELDS,
    chunks,
    filter_leaderboard_qs,
    get_country_info,
)

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
    if request.GET.get("nickname", nickname):
        trainer = get_object_or_404(
            Trainer,
            nickname__nickname__iexact=request.GET.get("nickname", nickname),
            owner__is_active=True,
        )
        if nickname == trainer.nickname:
            return profile_view(request, trainer)
    elif request.GET.get("id", id):
        trainer = get_object_or_404(
            Trainer, pk=int(str(request.GET.get("id", id)).replace("/", "")), owner__is_active=True
        )
    elif not request.user.is_authenticated:
        return redirect("account_login")
    else:
        trainer = request.user.trainer
        return redirect("trainerdex:profile", **{"nickname": trainer.nickname})

    return redirect("trainerdex:profile", permanent=True, **{"nickname": trainer.nickname})


def profile_view(request: HttpRequest, trainer: Trainer) -> HttpResponse:
    if request.user.is_authenticated and not _check_if_self_valid(request):
        messages.warning(request, _("Please complete your profile to continue using the website."))
        return redirect("profile_edit")

    context = {
        "trainer": trainer,
        "updates": trainer.update_set.all(),
        "stats": trainer.update_set.aggregate(**{x: Max(x) for x in UPDATE_SORTABLE_FIELDS}),
        "level": trainer.get_level(),
        "medal_data": {
            x.get("name"): {
                **x,
                **{
                    "verbose_name": Update._meta.get_field(x.get("name")).verbose_name,
                    "tooltip": Update._meta.get_field(x.get("name")).help_text,
                },
            }
            for x in BADGES
            if x.get("name") in (x.name for x in Update._meta.get_fields())
        },
    }

    context["bronze_medals"] = len(
        [
            True
            for x in context["medal_data"].values()
            if x.get("bronze")
            and context["stats"].get(x["name"])
            and (context["stats"].get(x["name"]) >= x["bronze"])
        ]
    )
    context["silver_medals"] = len(
        [
            True
            for x in context["medal_data"].values()
            if x.get("silver")
            and context["stats"].get(x["name"])
            and (context["stats"].get(x["name"]) >= x["silver"])
        ]
    )
    context["gold_medals"] = len(
        [
            True
            for x in context["medal_data"].values()
            if x.get("gold")
            and context["stats"].get(x["name"])
            and (context["stats"].get(x["name"]) >= x["gold"])
        ]
    )
    context["platinum_medals"] = len(
        [
            True
            for x in context["medal_data"].values()
            if x.get("platinum")
            and context["stats"].get(x["name"])
            and (context["stats"].get(x["name"]) >= x["platinum"])
        ]
    )
    context["medals_count"] = len(
        [
            True
            for x in context["medal_data"].values()
            if x.get("platinum") and context["stats"].get(x["name"])
        ]
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
            form.fields["double_check_confirmation"].widget = forms.HiddenInput()
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
            form.fields["double_check_confirmation"].widget = forms.HiddenInput()
    form.fields["update_time"].widget = forms.HiddenInput()
    form.fields["data_source"].widget = forms.HiddenInput()
    form.fields["data_source"].disabled = True
    form.fields["trainer"].widget = forms.HiddenInput()
    form.trainer = request.user.trainer

    if request.method == "POST":
        form.data_source = "web_detailed"
        if form.is_valid():
            form.save()
            messages.success(request, _("Statistics updated"))
            return redirect(
                "trainerdex:profile",
                **{"nickname": request.user.trainer.nickname},
            )
        else:
            form.fields["double_check_confirmation"].required = True

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
            country_info = get_country_info(country.upper())
        except IndexError:
            raise Http404(_("No country found for code {country}").format(country=country))
        context["title"] = country_info.get("name")
        queryset = Trainer.objects.filter(country_iso=country.upper())
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
        "evolved_total",
        "hatched_total",
        "pokestops_visited",
        "raid_battle_won",
        "legendary_battle_won",
        "hours_defended",
        "great_league",
        "ultra_league",
        "master_league",
        "update_time",
    }

    if order_by := request.GET.get("sort", "total_xp"):
        if order_by in UPDATE_SORTABLE_FIELDS:
            fields_to_calculate_max.add(order_by)
        else:
            order_by = "total_xp"
    context["sort_by"] = order_by

    context["grand_total_users"] = total_users = queryset.count()

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
            f"update__{field}__max": Subquery(
                Update.objects.filter(trainer=OuterRef("pk"), **{f"{order_by}__isnull": False})
                .values(field)
                .order_by("-update_time")[:1]
            )
            for field in fields_to_calculate_max
        },
    )

    Results = []
    GRAND_TOTAL = queryset.aggregate(Sum("update__total_xp__max"))
    context["grand_total_xp"] = GRAND_TOTAL["update__total_xp__max__sum"]

    queryset = (
        queryset.annotate(
            rank=Window(
                expression=DenseRank(),
                order_by=F(f"update__{order_by}__max").desc(),
            )
        )
        .order_by(
            "rank",
            "update__update_time__max",
            "faction",
        )
        .only(
            "id",
            "_nickname",
            "country_iso",
            "faction",
        )
    )

    for trainer in queryset:
        if not trainer.update__total_xp__max:
            continue
        trainer_stats = {
            "position": trainer.rank,
            "trainer": trainer,
            "total_xp": trainer.update__total_xp__max,
            "update_time": trainer.update__update_time__max,
            "level": trainer.level,
        }

        FIELDS = fields_to_calculate_max.copy()
        FIELDS.remove("update_time")
        FIELDS = [x for x in UPDATE_SORTABLE_FIELDS if x in FIELDS]
        FIELDS = [
            {
                "name": x,
                "readable_name": Update._meta.get_field(x).verbose_name,
                "tooltip": Update._meta.get_field(x).help_text,
                "value": getattr(trainer, "update__{field}__max".format(field=x)),
            }
            for x in FIELDS
        ]
        FIELDS.insert(0, FIELDS.pop([FIELDS.index(x) for x in FIELDS if x["name"] == order_by][0]))
        trainer_stats["columns"] = FIELDS
        Results.append(trainer_stats)

    try:
        page = int(request.GET.get("page") or 1)
    except ValueError:
        page = 1
    context["page"] = page
    context["pages"] = ceil(total_users / 100)
    pages = chunks(Results, 100)

    x = 0
    for y in pages:
        x += 1
        if x == context["page"]:
            context["leaderboard"] = y
            break

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
