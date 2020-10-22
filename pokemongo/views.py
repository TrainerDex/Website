import logging
from typing import Optional

from cities.models import Country
from datetime import datetime, timedelta
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Max, Sum, F, Window, Prefetch
from django.db.models.functions import DenseRank as Rank
from django.http import (
    HttpRequest,
    HttpResponse,
    Http404,
)
from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _, get_language_from_request
from math import ceil
from pokemongo.forms import UpdateForm, TrainerForm
from pokemongo.models import Trainer, Update, Community, Nickname
from pokemongo.shortcuts import (
    filter_leaderboard_qs,
    level_parser,
    UPDATE_FIELDS_BADGES,
    UPDATE_FIELDS_TYPES,
    UPDATE_SORTABLE_FIELDS,
    BADGES,
    chunks,
)

logger = logging.getLogger("django.trainerdex")


def _check_if_trainer_valid(user) -> bool:
    profile_complete = user.trainer.profile_complete
    logger.debug(
        msg="Checking {nickname}: Completed profile: {status}".format(
            nickname=user.username, status=profile_complete
        ),
    )
    return profile_complete


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


def TrainerRedirectorView(
    request: HttpRequest, nickname: Optional[str] = None, id: Optional[int] = None
) -> HttpResponse:
    if request.GET.get("nickname", nickname):
        trainer = get_object_or_404(
            Trainer, nickname__nickname__iexact=nickname, owner__is_active=True
        )
        if nickname == trainer.nickname:
            return TrainerProfileView(request, trainer)
    elif request.GET.get("id", id):
        trainer = get_object_or_404(Trainer, pk=id, owner__is_active=True)
    elif not request.user.is_authenticated:
        return redirect("account_login")
    else:
        trainer = request.user.trainer
        return redirect("trainerdex:profile", **{"nickname": trainer.nickname})

    return redirect("trainerdex:profile", permanent=True, **{"nickname": trainer.nickname})


def TrainerProfileView(request: HttpRequest, trainer: Trainer) -> HttpResponse:
    if request.user.is_authenticated and not _check_if_self_valid(request):
        messages.warning(request, _("Please complete your profile to continue using the website."))
        return redirect("profile_edit")

    context = {
        "trainer": trainer,
        "updates": trainer.update_set.all(),
        "badges": trainer.profilebadge_set.all(),
    }
    _badges = context["updates"].aggregate(
        *[Max(x) for x in UPDATE_FIELDS_BADGES + UPDATE_FIELDS_TYPES]
    )
    badges = []
    for badge in _badges:
        if not bool(_badges[badge]):
            continue
        badge_dict = {
            "name": badge,
            "readable_name": Update._meta.get_field(badge[:-5]).verbose_name,
            "tooltip": Update._meta.get_field(badge[:-5]).help_text,
            "value": _badges[badge],
        }
        badge_info = [x for x in BADGES if x["name"] == badge[:-5]][0]
        if badge_dict["value"] < badge_info["gold"]:
            badge_dict["percent"] = int((badge_dict["value"] / badge_info["gold"]) * 100)
        else:
            badge_dict["percent"] = 100
        badges.append(badge_dict)
    _values = context["updates"].aggregate(
        *[
            Max(x)
            for x in (
                "badge_travel_km",
                "badge_capture_total",
                "badge_pokestops_visited",
                "total_xp",
            )
        ]
    )
    for value in _values:
        context[value[:-5]] = _values[value]
    context["level"] = trainer.level()
    context["badges"] = badges
    context["update_history"] = []

    UPDATE_FIELDS = [
        x
        for x in Update._meta.get_fields()
        if x.name
        not in [
            "id",
            "uuid",
            "trainer",
            "submission_date",
            "data_source",
            "screenshot",
            "double_check_confirmation",
        ]
    ]
    for update in trainer.update_set.all():
        update_obj = []
        for x in UPDATE_FIELDS:
            update_obj.append(
                {
                    "attname": x.attname,
                    "readable_name": x.verbose_name,
                    "tooltip": x.help_text,
                    "value": getattr(update, x.column),
                },
            )
        context["update_history"].append(update_obj)

    return render(request, "profile.html", context)


@login_required
def CreateUpdateView(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated and not _check_if_self_valid(request):
        messages.warning(request, _("Please complete your profile to continue using the website."))
        return redirect("profile_edit")

    if request.user.trainer.update_set.filter(
        update_time__gte=datetime.now() - timedelta(hours=1)
    ).exists():
        existing = request.user.trainer.update_set.filter(
            update_time__gte=datetime.now() - timedelta(hours=1)
        ).latest("update_time")
    else:
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
    error_fields = None

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
            error_fields = [Update._meta.get_field(x) for x in form.errors.as_data().keys()]

    if existing:
        messages.info(
            request,
            _(
                "Since you have posted in the past hour, you are currently updating your previous post."
            ),
        )

    context = {
        "form": form,
        "error_fields": error_fields,
    }
    return render(request, "create_update.html", context)


def LeaderboardView(
    request: HttpRequest,
    country: Optional[str] = None,
    community: Optional[str] = None,
) -> HttpResponse:
    context = {}

    if country:
        try:
            country = Country.objects.prefetch_related("leaderboard_trainers_country").get(
                code__iexact=country
            )
        except Country.DoesNotExist:
            raise Http404(_("No country found for code {country}").format(country=country))
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
        "update_time",
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
        .prefetch_related(
            "leaderboard_country",
            Prefetch(
                "nickname_set",
                Nickname.objects.filter(active=True),
                to_attr="_nickname",
            ),
        )
        .order_by("rank", "update__update_time__max", "faction")
    )

    for trainer in queryset:
        if not trainer.update__total_xp__max:
            continue
        trainer_stats = {
            "position": trainer.rank,
            "trainer": trainer,
            "level": level_parser(xp=trainer.update__total_xp__max).level,
            "xp": trainer.update__total_xp__max,
            "update_time": trainer.update__update_time__max,
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


@login_required
def EditProfileView(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated and _check_if_self_valid(request):
        if request.user.trainer.update_set.count() == 0:
            messages.warning(request, "You have not posted your stats yet.")

    form = TrainerForm(instance=request.user.trainer)
    form.fields["verification"].required = not request.user.trainer.verified

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
