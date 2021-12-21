import logging
from datetime import timedelta
from math import ceil
from typing import Optional

from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import F, Max, Sum, Window
from django.db.models.functions import DenseRank as Rank
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls.base import reverse
from django.utils import timezone
from django.utils.translation import get_language_from_request
from django.utils.translation import gettext_lazy as _

from community.models import Community
from pokemongo.constants import (
    BADGES,
    UPDATE_FIELDS_BADGES,
    UPDATE_FIELDS_TYPES,
    UPDATE_SORTABLE_FIELDS,
)
from pokemongo.forms import MedalProgressForm
from pokemongo.models import MedalProgressPost
from pokemongo.utils import chunks, filter_leaderboard_qs, get_possible_levels_from_total_xp

logger = logging.getLogger("django.trainerdex")
User = get_user_model()


def UserRedirectorView(
    request: HttpRequest, nickname: Optional[str] = None, id: Optional[int] = None
) -> HttpResponse:
    if request.GET.get("nickname", nickname):
        user = get_object_or_404(
            User,
            username_history__username__iexact=request.GET.get("nickname", nickname),
            is_active=True,
        )
        if nickname == user.username:
            return UserProfileView(request, user)
    elif request.GET.get("id", id):
        user = get_object_or_404(
            User, pk=int(str(request.GET.get("id", id)).replace("/", "")), is_active=True
        )
    elif not request.user.is_authenticated:
        return redirect("account_login")
    else:
        user = request.user
        return redirect("trainerdex:profile", **{"nickname": user.username})

    return redirect("trainerdex:profile", permanent=True, **{"nickname": user.username})


def UserProfileView(request: HttpRequest, user: User) -> HttpResponse:
    context = {
        "user": user,
        "posts": user.posts.all().select_subclasses(),
        "stats": user.posts.select_subclasses(MedalProgressPost).aggregate(
            **{x: Max(x) for x in UPDATE_FIELDS_BADGES + UPDATE_FIELDS_TYPES}
        ),
        "level": 40,  # TODO: New level system,
        "medal_data": {
            x.get("name"): {
                **x,
                **{
                    "verbose_name": MedalProgressPost._meta.get_field(x.get("name")).verbose_name,
                    "tooltip": MedalProgressPost._meta.get_field(x.get("name")).help_text,
                },
            }
            for x in BADGES
            if x.get("name") in (x.name for x in MedalProgressPost._meta.get_fields())
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
def CreateUpdateView(request: HttpRequest) -> HttpResponse:

    try:
        existing = (
            request.user.posts.select_subclass(MedalProgressPost)
            .filter(post_dt__gte=timezone.now() - timedelta(hours=6))
            .latest("post_dt")
        )
    except MedalProgressPost.DoesNotExist:
        existing = None

    if existing:
        if request.method == "POST":
            form = MedalProgressForm(request.POST, instance=existing)
        else:
            form = MedalProgressForm(
                instance=existing,
                initial={
                    "trainer": request.user.trainer,
                    "data_source": "web_detailed",
                },
            )
            form.fields["double_check_confirmation"].widget = forms.HiddenInput()
    else:
        if request.method == "POST":
            form = MedalProgressForm(
                request.POST,
                initial={
                    "trainer": request.user.trainer,
                    "data_source": "web_detailed",
                },
            )
        else:
            form = MedalProgressForm(
                initial={"trainer": request.user.trainer, "data_source": "web_detailed"}
            )
            form.fields["double_check_confirmation"].widget = forms.HiddenInput()
    form.fields["post_dt"].widget = forms.HiddenInput()
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


def LeaderboardView(
    request: HttpRequest,
    country: Optional[str] = None,
    community: Optional[str] = None,
) -> HttpResponse:
    context = {}

    if country:
        from django_countries import countries

        countries[country]
        country = dict(countries)[country]
        context["title"] = (
            country.alt_names.filter(language_code=get_language_from_request(request)).first()
            or country
        ).name
        queryset = country.leaderboard_trainers_country
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
        "badge_capture_total",
        "badge_travel_km",
        "badge_evolved_total",
        "badge_hatched_total",
        "badge_pokestops_visited",
        "badge_raid_battle_won",
        "badge_legendary_battle_won",
        "badge_hours_defended",
        "badge_pokedex_entries_gen4",
        "badge_great_league",
        "badge_ultra_league",
        "badge_master_league",
        "post_dt",
    }
    if request.GET.get("sort"):
        if request.GET.get("sort") in UPDATE_SORTABLE_FIELDS:
            fields_to_calculate_max.add(request.GET.get("sort"))
            sort_by = request.GET.get("sort")
        else:
            sort_by = "total_xp"
    else:
        sort_by = "total_xp"
    context["sort_by"] = sort_by

    context["grand_total_users"] = total_users = queryset.count()

    if total_users == 0:
        context["page"] = 0
        context["pages"] = 0
        context["leaderboard"] = None
        return render(request, "leaderboard.html", context, status=404)

    queryset = queryset.annotate(*[Max("update__" + x) for x in fields_to_calculate_max]).exclude(
        **{f"update__{sort_by}__max__isnull": True}
    )

    Results = []
    GRAND_TOTAL = queryset.aggregate(Sum("update__total_xp__max"))
    context["grand_total_xp"] = GRAND_TOTAL["update__total_xp__max__sum"]

    queryset = (
        queryset.annotate(
            rank=Window(expression=Rank(), order_by=F(f"update__{sort_by}__max").desc())
        )
        .prefetch_related("leaderboard_country")
        .order_by("rank", "update__post_dt__max", "faction")
    )

    for trainer in queryset:
        if not trainer.update__total_xp__max:
            continue
        trainer_stats = {
            "position": trainer.rank,
            "trainer": trainer,
            "xp": trainer.update__total_xp__max,
            "update_time": trainer.update__update_time__max,
        }

        possible_levels = [
            x.level for x in get_possible_levels_from_total_xp(xp=trainer.update__total_xp__max)
        ]
        if min(possible_levels) == max(possible_levels):
            trainer_stats["level"] = str(min(possible_levels))
        else:
            trainer_stats["level"] = f"{min(possible_levels)}-{max(possible_levels)}"

        FIELDS = fields_to_calculate_max.copy()
        FIELDS.remove("update_time")
        FIELDS = [x for x in UPDATE_SORTABLE_FIELDS if x in FIELDS]
        FIELDS = [
            {
                "name": x,
                "readable_name": MedalProgressPost._meta.get_field(x).verbose_name,
                "tooltip": MedalProgressPost._meta.get_field(x).help_text,
                "value": getattr(trainer, "update__{field}__max".format(field=x)),
            }
            for x in FIELDS
        ]
        FIELDS.insert(0, FIELDS.pop([FIELDS.index(x) for x in FIELDS if x["name"] == sort_by][0]))
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
