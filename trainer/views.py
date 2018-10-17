# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger('django.trainerdex')
import requests

from allauth.socialaccount.models import SocialAccount
from cities.models import Continent, Country, Region
from datetime import datetime, timedelta, date
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist, PermissionDenied
from django.core.mail import mail_admins, EmailMessage
from django.db.models import Max, Q, Sum, F, Window
from django.db.models.functions import Rank
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect, QueryDict, HttpResponseBadRequest, Http404, HttpResponse
from django.shortcuts import get_object_or_404, get_list_or_404, render, redirect, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext_noop, pgettext_lazy, get_language_from_request
from django.urls import resolve
from math import ceil
from pytz import utc
from rest_framework import authentication, permissions, status
from rest_framework.decorators import detail_route
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from trainer.forms import UpdateForm, RegistrationFormTrainer, RegistrationFormUpdate
from trainer.models import Trainer, Update, Faction
from trainer.serializers import UserSerializer, BriefTrainerSerializer, DetailedTrainerSerializer, BriefUpdateSerializer, DetailedUpdateSerializer, LeaderboardSerializer, SocialAllAuthSerializer
from trainer.shortcuts import strtoboolornone, cleanleaderboardqueryset, level_parser, UPDATE_FIELDS_BADGES, UPDATE_FIELDS_TYPES, UPDATE_SORTABLE_FIELDS, BADGES, chunks


def _leaderboard_queryset_filter(queryset):
	return queryset.exclude(statistics=False).exclude(verified=False).exclude(last_cheated__lt=date(2018,9,1)-timedelta(weeks=26)).exclude(last_cheated__gt=date(2018,9,1)).exclude(last_cheated__gt=date.today()-timedelta(weeks=26)).select_related('faction')

# RESTful API Views

def recent(value):
	if timezone.now()-timedelta(hours=1) <= value <= timezone.now():
		return True
	return False

class UserViewSet(ModelViewSet):
	serializer_class = UserSerializer
	queryset = User.objects.all()
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class TrainerListJSONView(APIView):
	"""
	get:
	Accepts paramaters for Team (t) and Username (q)
	
	post:
	Register a Trainer, needs the Primary Key of the Owner, the User object which owns the Trainer
	"""
	
	authentication_classes = (authentication.TokenAuthentication,)
	
	def get(self, request):
		queryset = Trainer.objects.exclude(owner__is_active=False)
		if request.GET.get('q') or request.GET.get('t'):
			if request.GET.get('q'):
				queryset = queryset.filter(username__iexact=request.GET.get('q'))
			if request.GET.get('t'):
				queryset = queryset.filter(faction=request.GET.get('t'))
		
		if request.GET.get('detail') == '1':
			serializer = DetailedTrainerSerializer(queryset, many=True)
			return Response(serializer.data)
		else:
			serializer = BriefTrainerSerializer(queryset, many=True)
			return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)
	
	def post(self, request):
		"""
		This used to work as a simple post, but since the beginning of transitioning to API v2 it would have always given Validation Errors if left the same.
		Now it has a 60 minute open slot to work after the auth.User (owner) instance is created. After which, a PATCH request must be given. This is due to the nature of a Trainer being created automatically for all new auth.User
		"""
		
		trainer = Trainer.objects.get(owner__pk=request.data['owner'])
		if not recent(trainer.owner.date_joined):
			return Response({"_error": "profile already exists, please use patch on trainer uri instead or check the owner pk is correct", "_profile_id": trainer.pk}, status=status.HTTP_400_BAD_REQUEST)
		serializer = DetailedTrainerSerializer(trainer, data=request.data, partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	

class TrainerDetailJSONView(APIView):
	"""
	get:
	Trainer detail
	
	patch:
	Update a trainer
	
	delete:
	Archives a trainer
	"""
	
	authentication_classes = (authentication.TokenAuthentication,)
	
	def get_object(self, pk):
		return get_object_or_404(Trainer, pk=pk)
	
	def get(self, request, pk):
		trainer = self.get_object(pk)
		if trainer.active is True:
			if request.GET.get('detail') == 'low':
				serializer = BriefTrainerSerializer(trainer)
			else:
				serializer = DetailedTrainerSerializer(trainer)
			if trainer.statistics is True or (trainer.statistics is False and request.GET.get('statistics') == 'force'):
				return Response(serializer.data)
			elif trainer.statistics is False:
				return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
		elif trainer.active is False:
			response = {
				'code': 1,
				'reason': 'Profile deactivated',
				'profile': {
					'id': trainer.pk,
					'faction': trainer.faction.id,
				},
			}
			return Response(response, status=status.HTTP_423_LOCKED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	
	def patch(self, request, pk):
		trainer = self.get_object(pk)
		serializer = DetailedTrainerSerializer(trainer, data=request.data, partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	
	def delete(self, request, pk):
		trainer = self.get_object(pk)
		if trainer.active:
			trainer.active = False
			trainer.save()
			response = {
				'code': 1,
				'reason': 'Profile deactivated',
				'profile': {
					'id': trainer.pk,
					'faction': trainer.faction.id,
				},
			}
			return Response(response, status=status.HTTP_204_NO_CONTENT)
		return Response(status=status.HTTP_400_BAD_REQUEST)
	

class UpdateListJSONView(APIView):
	"""
	get:
	Takes Trainer ID as part of URL, optional param: detail, shows all detail, otherwise, returns a list of objects with fields 'time_updated' (datetime), 'xp'(int) and 'fields_updated' (list)
	
	post:
	Create a update
	"""
	
	authentication_classes = (authentication.TokenAuthentication,)
	
	def get(self, request, pk):
		updates = Update.objects.filter(trainer=pk)
		serializer = BriefUpdateSerializer(updates, many=True) if request.GET.get('detail') != "1" else DetailedUpdateSerializer(updates, many=True)
		return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)
	
	def post(self, request, pk):
		serializer = DetailedUpdateSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save(trainer=get_object_or_404(Trainer, pk=pk))
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	
	def patch(self, request, pk):
		return self.post(self, request, pk)
	

class LatestUpdateJSONView(APIView):
	"""
	get:
	Gets detailed view of the latest update
	
	patch:
	Allows editting of update within first half hour of creation, after that time, all updates are denied. Trainer, UUID and PK are locked.
	"""
	
	authentication_classes = (authentication.TokenAuthentication,)
	
	def get(self, request, pk):
		update = Update.objects.filter(trainer=pk).latest('update_time')
		serializer = DetailedUpdateSerializer(update)
		return Response(serializer.data)
	
	def patch(self, request, pk):
		update = Update.objects.filter(trainer=pk).latest('update_time')
		if update.meta_time_created > datetime.now(utc)-timedelta(minutes=32):
			serializer = DetailedUpdateSerializer(update, data=request.data)
			if serializer.is_valid():
				serializer.clean()
				serializer.save(trainer=update.trainer,uuid=update.uuid,pk=update.pk)
				return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	

class UpdateDetailJSONView(APIView):
	"""
	get:
	Gets detailed view
	
	patch:
	Allows editting of update within first half hour of creation, after that time, all updates are denied. Trainer, UUID and PK are locked
	
	delete:
	Delete an update, works within first 48 hours of creation, otherwise, an email request for deletion is sent to admin
	"""
	
	authentication_classes = (authentication.TokenAuthentication,)
	
	def get(self, request, uuid, pk):
		update = get_object_or_404(Update, trainer=pk, uuid=uuid)
		serializer = DetailedUpdateSerializer(update)
		if update.trainer.id != int(pk):
			return Response(serializer.errors, status=400)
		return Response(serializer.data)
	
	def patch(self, request, uuid, pk):
		update = get_object_or_404(Update, trainer=pk, uuid=uuid)
		if update.meta_time_created > datetime.now(utc)-timedelta(minutes=32):
			serializer = DetailedUpdateSerializer(update, data=request.data)
			if serializer.is_valid():
				serializer.clean()
				serializer.save(trainer=update.trainer,uuid=update.uuid,pk=update.pk)
				return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	
	def delete(self, request, uuid, pk):
		update = get_object_or_404(Update, trainer=pk, uuid=uuid)
		if update.meta_time_created > datetime.now(utc)-timedelta(days=2):
			update.delete()
			return Response(status=status.HTTP_204_NO_CONTENT)
		else:
			SUBJECT = 'Late Update Deletion Request'
			MESSAGE = 'There has been a request to delete {update} by {requester} at {ip}'.format(update=request.build_absolute_uri(), requester=request.user, ip=request.get_host())
			mail_admins(SUBJECT, MESSAGE)
			return Response({'request_made': True, 'subject': SUBJECT, 'message': MESSAGE}, status=status.HTTP_202_ACCEPTED)
		return Response(status=status.HTTP_400_BAD_REQUEST)
	

class LeaderboardJSONView(APIView):
	
	def get(self, request):
		query = _leaderboard_queryset_filter(Trainer.objects)
		if request.GET.get('users'):
			query = Trainer.objects.filter(id__in=request.GET.get('users').split(','))
		leaderboard = query.annotate(Max('update__total_xp'), Max('update__update_time')).exclude(update__total_xp__max__isnull=True).order_by('-update__total_xp__max')
		serializer = LeaderboardSerializer(enumerate(leaderboard, 1), many=True)
		return Response(serializer.data)
	

class SocialLookupJSONView(APIView):
	"""
	get:
		kwargs:
			provider (requiered) - platform, options are 'facebook', 'twitter', 'discord', 'google', 'patreon'
		
			uid - Social ID, supports a comma seperated list. Could be useful for passing a list of users in a server to retrieve a list of UserIDs, which could then be passed to api/v1/leaderboard/
			user - TrainerDex User ID, supports a comma seperated list
			trainer - TrainerDex Trainer ID
	
	patch:
	Register a SocialAccount. Patch if exists, post if not.
	"""
	
	def get(self, request):
		query = SocialAccount.objects.filter(provider=request.GET.get('provider'))
		if request.GET.get('uid'):
			query = query.filter(uid__in=request.GET.get('uid').split(','))
		elif request.GET.get('user'):
			query = query.filter(user__in=request.GET.get('user').split(','))
		elif request.GET.get('trainer'):
			query = query.filter(user=get_object_or_404(Trainer, pk=request.GET.get('trainer')).owner)
		else:
			return Response(status=status.HTTP_400_BAD_REQUEST)
		serializer = SocialAllAuthSerializer(query, many=True)
		return Response(serializer.data)
		
	def put(self, request):
		try:
			query = SocialAccount.objects.get(provider=request.data['provider'], uid=request.data['uid'])
		except:
			serializer = SocialAllAuthSerializer(data=request.data)
		else:
			serializer = SocialAllAuthSerializer(query, data=request.data, partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DiscordLeaderboardAPIView(APIView):
	def get(self, request, guild):
		discord_base_url = 'https://discordapp.com/api'
		headers = {}
		output = {'generated':datetime.utcnow()}
		
		if request.GET.get('DiscordAuthorization'):
			headers['Authorization'] = request.GET.get('DiscordAuthorization')
		else:
			headers['Authorization'] = 'Bot Mzc3NTU5OTAyNTEzNzkwOTc3.DYhWdw.tBGXI2g8RqH3EbDDdypSaQLXYLU'
		
		_guild = requests.get('{base_url}/guilds/{param}'.format(base_url=discord_base_url, param=guild), headers=headers)
		if not status.is_success(_guild.status_code):
			return Response({'error': '003 - Bad Guild ID', 'cause': "Most likely, the bot parameter provided doesn't have access to that guild", 'solution': "If I have to lay this out to you, you shouldn't be here"}, status=status.HTTP_400_BAD_REQUEST)
		_guild = _guild.json()
		
		output['title'] = '{guild_name} Leaderboard'.format(guild_name=_guild['name'])
		opt_out_role_id = [x['id'] for x in _guild['roles'] if x['name'] in ('NoLB,')]
		
		members = requests.get('{base_url}/guilds/{param}/members'.format(base_url=discord_base_url, param=guild), headers=headers, params={'limit':1000})
		if not status.is_success(members.status_code):
			return Response({'error': '000 - Unknown', 'cause': 'unknown', 'solution':'forward this output to apisupport@trainerdex.co.uk', 'Discord API Responce': members.content}, status=members.status_code)
		members = [x['user']['id'] for x in members.json() if not any([i in x['roles'] for i in opt_out_role_id])]
		trainers = _leaderboard_queryset_filter(Trainer.objects.filter(owner__socialaccount__provider='discord', owner__socialaccount__uid__in=members))
		
		leaderboard = trainers.annotate(Max('update__total_xp'), Max('update__update_time')).exclude(update__total_xp__max__isnull=True).order_by('-update__total_xp__max')
		serializer = LeaderboardSerializer(enumerate(leaderboard, 1), many=True)
		output['leaderboard'] = serializer.data
		return Response(output)
	
# Web-based views

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
	
	return HttpResponsePermanentRedirect(reverse('trainerdex_web:profile_username', kwargs={'username':trainer.username}))

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
	_values = context['updates'].aggregate(*[Max(x) for x in ('total_xp', 'pokedex_caught', 'pokedex_seen', 'gymbadges_total', 'gymbadges_gold',)])
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
	
	form = UpdateForm(initial={'trainer':request.user.trainer, 'data_source': 'web_detailed'})
	form.fields['update_time'].widget = forms.HiddenInput()
	form.fields['data_source'].widget = forms.HiddenInput()
	form.fields['data_source'].disabled = True
	form.fields['trainer'].widget = forms.HiddenInput()
	form.fields['double_check_confirmation'].widget = forms.HiddenInput()
	form.trainer = request.user.trainer
	if request.method == 'POST':
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
			messages.success(request, 'Statistics updated')
			return HttpResponseRedirect(reverse('trainerdex_web:profile_username', kwargs={'username':request.user.trainer.username}))
	
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
	
	QuerySet = _leaderboard_queryset_filter(QuerySet)
	
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
		return HttpResponseRedirect(reverse('trainerdex_web:profile'))
	
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
		return HttpResponseRedirect(reverse('trainerdex_web:update_stats'))
	
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
			return HttpResponseRedirect(reverse('trainerdex_web:profile_username', kwargs={'username':request.user.trainer.username}))
		logger.info(form.cleaned_data)
		logger.error(form.errors)
	form.fields['update_time'].widget = forms.HiddenInput()
	form.fields['data_source'].widget = forms.HiddenInput()
	form.fields['trainer'].widget = forms.HiddenInput()
	return render(request, 'create_update.html', {'form': form})
