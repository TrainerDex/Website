# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger('django.trainerdex')
import requests

from cities.models import Continent, Country, Region
from datetime import datetime, date, timedelta
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db.models import Max, Q, Sum, F, Window
from django.db.models.functions import Rank
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect, Http404, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language_from_request
from math import ceil
from trainer.forms import UpdateForm, RegistrationFormTrainer, RegistrationFormUpdate
from trainer.models import Trainer, Update, Faction
from trainer.shortcuts import strtoboolornone, filter_leaderboard_qs, level_parser, UPDATE_FIELDS_BADGES, UPDATE_FIELDS_TYPES, UPDATE_SORTABLE_FIELDS, BADGES, chunks

def _check_if_trainer_valid(trainer):
    if settings.DEBUG:
        logger.log(level=30 if trainer.profile_complete else 20, msg='Checking {username}: Completed profile: {status}'.format(username=trainer.username, status=trainer.profile_complete))
        logger.log(level=30 if trainer.update_set.exclude(total_xp__isnull=True).count() else 20, msg='Checking {username}: Update count: {count}'.format(username=trainer.username, count=trainer.update_set.count()))
    if not trainer.profile_complete or not trainer.update_set.exclude(total_xp__isnull=True).exists():
        raise Http404(_('{0} has not completed their profile.').format(trainer.owner.username))
    return trainer

def _check_if_self_valid(request):
    try:
        _check_if_trainer_valid(request.user.trainer)
        return True
    except Http404:
        return False

def TrainerRedirectorView(request, username=None, id=None):
    if username:
        trainer = get_object_or_404(Trainer, username__iexact=username)
    elif id:
        trainer = get_object_or_404(Trainer, pk=id)
    elif request.GET.get('username'):
        trainer = get_object_or_404(Trainer, username__iexact=request.GET.get('username'))
    elif request.GET.get('id'):
        trainer = get_object_or_404(Trainer, pk=request.GET.get('id'))
    elif not request.user.is_authenticated:
        return redirect('home')
    else:
        trainer = request.user.trainer
    
    return HttpResponsePermanentRedirect(reverse('trainerdex:profile_username', kwargs={'username':trainer.username}))

def TrainerProfileHTMLView(request, username):
    if request.user.is_authenticated and not _check_if_self_valid(request):
        messages.warning(request, _("Please complete your profile to continue using the website."))
        return HttpResponseRedirect(reverse('profile_set_up'))
    
    trainer = Trainer.objects.prefetch_related().get(username__iexact=username)
    context = {
        'trainer' : trainer,
        'updates' : trainer.update_set.all(),
        'sponsorships' : trainer.sponsorships.all(),
    }
    _badges = context['updates'].aggregate(*[Max(x) for x in UPDATE_FIELDS_BADGES + UPDATE_FIELDS_TYPES])
    badges = []
    for badge in _badges:
        if not bool(_badges[badge]):
            continue
        badge_dict = {
            'name':badge,
            'readable_name':Update._meta.get_field(badge[:-5]).verbose_name,
            'tooltip':Update._meta.get_field(badge[:-5]).help_text,
            'value':_badges[badge]
        }
        badge_info = [x for x in BADGES if x['name'] == badge[:-5]][0]
        if badge_dict['value'] < badge_info['gold']:
            badge_dict['percent'] = int((badge_dict['value']/badge_info['gold'])*100)
        else:
            badge_dict['percent'] = 100
        badges.append(badge_dict)
    _values = context['updates'].aggregate(*[Max(x) for x in ('total_xp', 'pokedex_caught', 'pokedex_seen', 'gymbadges_total', 'gymbadges_gold', 'pokemon_info_stardust',)])
    for value in _values:
        context[value[:-5]] = _values[value]
    context['level'] = trainer.level()
    context['badges'] = badges
    context['update_history'] = []
    
    UPDATE_FIELDS = [x for x in Update._meta.get_fields() if x.name not in ['id', 'uuid', 'trainer','submission_date', 'data_source', 'screenshot', 'double_check_confirmation']]
    for update in trainer.update_set.all():
        update_obj = []
        for x in UPDATE_FIELDS:
            update_obj.append(
                {
                    'attname':x.attname,
                    'readable_name':x.verbose_name,
                    'tooltip':x.help_text,
                    'value':getattr(update, x.column),
                },
            )
        context['update_history'].append(update_obj)
    
    try:
        trainer.get_silph_card()
    except (ObjectDoesNotExist, PermissionDenied):
        context['silph_card'] = False
    else:
        context['silph_card'] = True
    
    return render(request, 'profile.html', context)

@login_required
def CreateUpdateHTMLView(request):
    if request.user.is_authenticated and not _check_if_self_valid(request):
        messages.warning(request, _("Please complete your profile to continue using the website."))
        return HttpResponseRedirect(reverse('profile_set_up'))
    
    if request.user.trainer.update_set.filter(update_time__gte=datetime.now()-timedelta(hours=1)).exists():
        existing = request.user.trainer.update_set.filter(update_time__gte=datetime.now()-timedelta(hours=1)).latest('update_time')
    else:
        existing = None
        
    if existing:
        form = UpdateForm(instance=existing)
    else:
        form = UpdateForm(initial={'trainer':request.user.trainer, 'data_source': 'web_detailed'})
    form.fields['update_time'].widget = forms.HiddenInput()
    form.fields['data_source'].widget = forms.HiddenInput()
    form.fields['data_source'].disabled = True
    form.fields['trainer'].widget = forms.HiddenInput()
    form.fields['double_check_confirmation'].widget = forms.HiddenInput()
    form.trainer = request.user.trainer
    if request.method == 'POST':
        if existing:
            form = UpdateForm(request.POST, instance=existing)
        else:
            form = UpdateForm(request.POST, initial={'trainer':request.user.trainer, 'data_source': 'web_detailed'})
        form.fields['update_time'].widget = forms.HiddenInput()
        form.fields['data_source'].widget = forms.HiddenInput()
        form.fields['data_source'].disabled = True
        form.fields['trainer'].widget = forms.HiddenInput()
        form.fields['double_check_confirmation'].required = True
        form.data_source = 'web_detailed'
        form.trainer = request.user.trainer
        if form.is_valid():
            update = form.save()
            messages.success(request, _('Statistics updated'))
            return HttpResponseRedirect(reverse('trainerdex:profile_username', kwargs={'username':request.user.trainer.username}))
    
    if existing:
        messages.info(request, _('You have posted in the past hour - updating previous post.'))
    context = {
        'form': form
    }
    return render(request, 'create_update.html', context)

def LeaderboardHTMLView(request, continent=None, country=None, region=None):
    if request.user.is_authenticated and not _check_if_self_valid(request):
        messages.warning(request, _("Please complete your profile to continue using the website."))
        return HttpResponseRedirect(reverse('profile_set_up'))
    
    context = {}
    
    context['mystic'] = showMystic = {'param':'Mystic', 'value': strtoboolornone(request.GET.get('mystic'))}
    context['valor'] = showValor = {'param':'Valor', 'value': strtoboolornone(request.GET.get('valor'))}
    context['instinct'] = showInstinct = {'param':'Instinct', 'value': strtoboolornone(request.GET.get('instinct'))}
    context['factions'] = Faction.objects.all()
    
    if continent:
        try:
            continent = Continent.objects.get(code__iexact = continent)
        except Continent.DoesNotExist:
            raise Http404(_('No continent found for code {continent}').format(continent=continent))
        context['title'] = (continent.alt_names.filter(language_code=get_language_from_request(request)).first() or continent).name
        QuerySet = Trainer.objects.filter(leaderboard_country__continent__code__iexact=continent)
    elif country and region == None:
        try:
            country = Country.objects.prefetch_related('leaderboard_trainers_country').get(code__iexact = country)
        except Country.DoesNotExist:
            raise Http404(_('No country found for code {country}').format(country=country))
        context['title'] = (country.alt_names.filter(language_code=get_language_from_request(request)).first() or country).name
        QuerySet = country.leaderboard_trainers_country
    elif region:
        try:
            region = Region.objects.filter(country__code__iexact = country).get(code__iexact = region)
        except Country.DoesNotExist:
            raise Http404(_('No country found for code {country}').format(country = country))
        except Region.DoesNotExist:
            raise Http404(_('No region found for code {country}/{region}').format(country = country, region = region))
            
        context['title'] = _('{region_str}, {country_str}').format(
            region_str=(region.alt_names.filter(language_code=get_language_from_request(request)).first() or region).name,
            country_str=(region.country.alt_names.filter(language_code=get_language_from_request(request)).first() or region.country).name
        )
        QuerySet = region.leaderboard_trainers_region
    else:
        context['title'] = None
        QuerySet = Trainer.objects
    
    QuerySet = filter_leaderboard_qs(QuerySet)
    
    SORTABLE_FIELDS = ['update__'+x for x in UPDATE_SORTABLE_FIELDS]
    fields_to_calculate_max = {'total_xp', 'badge_capture_total', 'badge_travel_km', 'badge_evolved_total', 'badge_hatched_total', 'badge_pokestops_visited', 'badge_raid_battle_won', 'badge_legendary_battle_won',
'badge_hours_defended','badge_challenge_quests', 'badge_pokedex_entries_gen4', 'update_time'} # Gen 4 in there temp.
    if request.GET.get('sort'):
        if request.GET.get('sort') in UPDATE_SORTABLE_FIELDS:
            fields_to_calculate_max.add(request.GET.get('sort'))
            sort_by = request.GET.get('sort')
        else:
            sort_by = 'total_xp'
    else:
        sort_by = 'total_xp'
    context['sort_by'] = sort_by
    
    
    QuerySet = QuerySet.exclude(faction__slug__in=[x['param'] for x in (showValor, showMystic, showInstinct) if x['value'] is False])
    context['grand_total_users'] = total_users = QuerySet.count()
    
    if total_users == 0:
        context['page'] = 0
        context['pages'] = 0
        context['leaderboard'] = None
        return render(request, 'leaderboard.html', context, status=404)
    
    QuerySet = QuerySet.annotate(*[Max('update__'+x) for x in fields_to_calculate_max]).exclude(**{f'update__{sort_by}__max__isnull': True}).order_by(f'-update__{sort_by}__max', '-update__total_xp__max', '-update__update_time__max', 'faction',)
    
    Results = []
    GRAND_TOTAL = QuerySet.aggregate(Sum('update__total_xp__max'))
    context['grand_total_xp'] = GRAND_TOTAL['update__total_xp__max__sum']
    
    for trainer in QuerySet.annotate(rank=Window(expression=Rank(), order_by=F(f'update__{sort_by}__max').desc())).prefetch_related('leaderboard_country'):
        if not trainer.update__total_xp__max:
            continue
        trainer_stats = {
            'position' : trainer.rank,
            'trainer' : trainer,
            'level' : level_parser(xp=trainer.update__total_xp__max).level,
            'xp' : trainer.update__total_xp__max,
            'update_time' : trainer.update__update_time__max,
        }
        
        FIELDS = []
        FIELDS_TO_SORT = fields_to_calculate_max.copy()
        FIELDS_TO_SORT.remove('update_time')
        FIELDS_TO_SORT = [x for x in UPDATE_SORTABLE_FIELDS if x in FIELDS_TO_SORT]
        for x in FIELDS_TO_SORT:
            FIELDS.append(
                {
                    'name':x,
                    'readable_name':Update._meta.get_field(x).verbose_name,
                    'tooltip':Update._meta.get_field(x).help_text,
                    'value':getattr(trainer, 'update__{field}__max'.format(field=x)),
                },
            )
        trainer_stats['columns'] = FIELDS
        Results.append(trainer_stats)
    
    try:
        page = int(request.GET.get('page') or 1)
    except ValueError:
        page = 1
    context['page'] = page
    context['pages'] = ceil(total_users/100)
    pages = chunks(Results, 100)
    
    x = 0
    for y in pages:
        x += 1
        if x == context['page']:
            context['leaderboard'] = y
            break
    
    
    return render(request, 'leaderboard.html', context)

@login_required
def SetUpProfileViewStep2(request):
    if request.user.is_authenticated and _check_if_self_valid(request):
        if len(request.user.trainer.update_set.all()) == 0:
            return HttpResponseRedirect(reverse('profile_first_post'))
        return HttpResponseRedirect(reverse('trainerdex:profile'))
    
    form = RegistrationFormTrainer(instance=request.user.trainer)
    form.fields['verification'].required = True
    
    if request.method == 'POST':
        form = RegistrationFormTrainer(request.POST, request.FILES, instance=request.user.trainer)
        form.fields['verification'].required = True
        if form.is_valid() and form.has_changed():
            request.user.username = form.cleaned_data['username']
            request.user.save()
            form.save()
            messages.success(request, _("Thank you for filling out your profile. Your screenshots have been sent for verification. An admin will verify you within the next couple of days. Until then, you will not appear in the Global Leaderboard but you can still use Guild Leaderboards and and update your stats!"))
            return HttpResponseRedirect(reverse('profile_first_post'))
    return render(request, 'account/signup2.html', {'form': form})

@login_required
def SetUpProfileViewStep3(request):
    if request.user.is_authenticated and _check_if_self_valid(request) and len(request.user.trainer.update_set.all()) > 0:
        return HttpResponseRedirect(reverse('trainerdex:update_stats'))
    
    form = RegistrationFormUpdate(initial={'trainer':request.user.trainer})
    form.fields['screenshot'].required = True
    
    if request.method == 'POST':
        logger.info(request.FILES)
        form_data = request.POST.copy()
        form_data['data_source'] = 'ss_registration'
        form = RegistrationFormUpdate(form_data, request.FILES)
        form.fields['screenshot'].required = True
        form.trainer = request.user.trainer
        logger.info(form.is_valid())
        if form.is_valid():
            form.save()
            messages.success(request, _("Stats updated. Screenshot included."))
            return HttpResponseRedirect(reverse('trainerdex:profile_username', kwargs={'username':request.user.trainer.username}))
        logger.info(form.cleaned_data)
        logger.error(form.errors)
    form.fields['update_time'].widget = forms.HiddenInput()
    form.fields['data_source'].widget = forms.HiddenInput()
    form.fields['trainer'].widget = forms.HiddenInput()
    return render(request, 'create_update.html', {'form': form})
