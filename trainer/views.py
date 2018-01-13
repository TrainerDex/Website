from allauth.socialaccount.models import SocialAccount
from datetime import datetime, timedelta
from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import mail_admins
from django.db.models import Max
from django.http import HttpResponseRedirect, QueryDict, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from pycent import percentage
from pytz import utc
from rest_framework import authentication, permissions, status
from rest_framework.decorators import detail_route
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from trainer.forms import QuickUpdateForm, UpdateForm
from trainer.models import Trainer, Update
from trainer.serializers import UserSerializer, BriefTrainerSerializer, DetailedTrainerSerializer, BriefUpdateSerializer, DetailedUpdateSerializer, LeaderboardSerializer, SocialAllAuthSerializer
from trainer.shortcuts import nullbool, cleanleaderboardqueryset, level_parser

# RESTful API Views

class UserViewSet(ModelViewSet):
	serializer_class = UserSerializer
	queryset = User.objects.all()
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class TrainerListJSONView(APIView):
	"""
	GET - Accepts paramaters for Team (t) and Username (q)
	POST - Register a Trainer, needs PK for User
	"""
	
	authentication_classes = (authentication.TokenAuthentication,)
	
	def get(self, request):
		queryset = Trainer.objects.exclude(active=False)
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
		serializer = DetailedTrainerSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	

class TrainerDetailJSONView(APIView):
	"""
	GET - Trainer detail
	PATCH - Update a trainer
	DELETE - Archives a trainer (hidden from APIs until trainer tries to join again)
	"""
	
	authentication_classes = (authentication.TokenAuthentication,)
	
	def get_object(self, pk):
		return get_object_or_404(Trainer, pk=pk)
	
	def get(self, request, pk):
		print(status.HTTP_423_LOCKED)
		trainer = self.get_object(pk)
		if trainer.active is True:
			if trainer.statistics is True or (trainer.statistics is False and request.GET.get('statistics') == 'force'):
				serializer = DetailedTrainerSerializer(trainer)
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
				'reason': _('Profile deactivated'),
				'profile': {
					'id': trainer.pk,
					'faction': trainer.faction.id,
				},
			}
			return Response(response, status=status.HTTP_204_NO_CONTENT)
		return Response(status=status.HTTP_400_BAD_REQUEST)
	

class UpdateListJSONView(APIView):
	"""
	GET - Takes Trainer ID as part of URL, optional param: detail, shows all detail, otherwise, returns a list of objects with fields 'time_updated' (datetime), 'xp'(int) and 'fields_updated' (list)
	POST/PATCH - Create a update
	"""
	
	authentication_classes = (authentication.TokenAuthentication,)
	
	def get(self, request, pk):
		updates = Update.objects.filter(trainer=pk)
		serializer = BriefUpdateSerializer(updates, many=True)
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
	GET - Gets detailed view of the latest update
	PATCH - Allows editting of update within first half hour of creation, after that time, all updates are denied. Trainer, UUID and PK are locked.
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
	GET - Gets detailed view
	PATCH - Allows editting of update within first half hour of creation, after that time, all updates are denied. Trainer, UUID and PK are locked.
	DELETE - Delete an update, works within first 48 hours of creation, otherwise, an email request for deletion is sent to admin
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
			SUBJECT = _('Late Update Deletion Request')
			MESSAGE = _('There has been a request to delete {update} by {requester} at {ip}').format(update=request.build_absolute_uri(), requester=request.user, ip=request.get_host())
			mail_admins(SUBJECT, MESSAGE)
			return Response({'request_made': True, 'subject': SUBJECT, 'message': MESSAGE}, status=status.HTTP_202_ACCEPTED)
		return Response(status=status.HTTP_400_BAD_REQUEST)
	

class LeaderboardJSONView(APIView):
	
	def get(self, request):
		query = Trainer.objects
		if request.GET.get('users'):
			query = query.filter(id__in=request.GET.get('users').split(','))
		leaderboard = query.exclude(statistics=False, currently_cheats=True).annotate(Max('update__xp'), Max('update__update_time'))
		leaderboard = cleanleaderboardqueryset(leaderboard, key=lambda x: x.update__xp__max, reverse=True)
		serializer = LeaderboardSerializer(enumerate(leaderboard, 1), many=True)
		return Response(serializer.data)
	

class SocialLookupJSONView(APIView):
	"""
	GET args:
		provider (requiered) - platform, options are 'facebook', 'twitter', 'discord', 'google', 'patreon'
		
		One of the below, they're checked in this order so if you provide more than one, only the first would be processed.
		uid - Social ID, supports a comma seperated list. Could be useful for passing a list of users in a server to retrieve a list of UserIDs, which could then be passed to api/v1/leaderboard/
		user - TrainerDex User ID, supports a comma seperated list
		trainer - TrainerDex Trainer ID
	PUT: Register a SocialAccount. Patch if exists, post if not.
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

# Web-based views

BADGES = [
	{'name':'walk_dist', 'bronze':10, 'silver':100, 'gold':1000, 'i18n_name':_('Distance Walked')},
	{'name':'gen_1_dex', 'bronze':5, 'silver':50, 'gold':100, 'i18n_name':_('Kanto Pokédex')},
	{'name':'pkmn_caught', 'bronze':30, 'silver':500, 'gold':2000, 'i18n_name':_('Pokémon Caught')},
	{'name':'pkmn_evolved', 'bronze':3, 'silver':20, 'gold':200, 'i18n_name':_('Pokémon Evolved')},
	{'name':'eggs_hatched', 'bronze':10, 'silver':100, 'gold':500, 'i18n_name':_('Eggs Hatched')},
	{'name':'pkstops_spun', 'bronze':100, 'silver':1000, 'gold':2000, 'i18n_name':_('Pokéstops Spun')},
	{'name':'big_magikarp', 'bronze':3, 'silver':50, 'gold':300, 'i18n_name':_('Big Magikarp')},
	{'name':'battles_won', 'bronze':10, 'silver':100, 'gold':1000, 'i18n_name':_('Battles Won')},
	{'name':'legacy_gym_trained', 'bronze':10, 'silver':100, 'gold':1000, 'i18n_name':_('Ace Trainer')},
	{'name':'tiny_rattata', 'bronze':3, 'silver':50, 'gold':300, 'i18n_name':_('Tiny Rattata')},
	{'name':'pikachu_caught', 'bronze':3, 'silver':50, 'gold':300, 'i18n_name':_('Pikachu Caught')},
	{'name':'gen_2_dex', 'bronze':5, 'silver':30, 'gold':70, 'i18n_name':_('Johto Pokédex')},
	{'name':'unown_alphabet', 'bronze':3, 'silver':10, 'gold':26, 'i18n_name':_('Unown')},
	{'name':'berry_fed', 'bronze':10, 'silver':100, 'gold':1000, 'i18n_name':_('Berries Fed')},
	{'name':'gym_defended', 'bronze':10, 'silver':100, 'gold':1000, 'i18n_name':_('Gyms Defended (Hours)')},
	{'name':'raids_completed', 'bronze':10, 'silver':100, 'gold':1000, 'i18n_name':_('Raids Completed (Levels 1-4)')},
	{'name':'leg_raids_completed', 'bronze':10, 'silver':100, 'gold':1000, 'i18n_name':_('Raids Completed (Level 5)')},
	{'name':'gen_3_dex', 'bronze':5, 'silver':40, 'gold':90, 'i18n_name':_('Hoenn Pokédex')},
]

TYPE_BADGES = [
	{'name':'pkmn_normal', 'bronze':10, 'silver':50, 'gold':200, 'i18n_name':_('Normal')},
	{'name':'pkmn_flying', 'bronze':10, 'silver':50, 'gold':200, 'i18n_name':_('Flying')},
	{'name':'pkmn_poison', 'bronze':10, 'silver':50, 'gold':200, 'i18n_name':_('Poison')},
	{'name':'pkmn_ground', 'bronze':10, 'silver':50, 'gold':200, 'i18n_name':_('Ground')},
	{'name':'pkmn_rock', 'bronze':10, 'silver':50, 'gold':200, 'i18n_name':_('Rock')},
	{'name':'pkmn_bug', 'bronze':10, 'silver':50, 'gold':200, 'i18n_name':_('Bug')},
	{'name':'pkmn_steel', 'bronze':10, 'silver':50, 'gold':200, 'i18n_name':_('Steel')},
	{'name':'pkmn_fire', 'bronze':10, 'silver':50, 'gold':200, 'i18n_name':_('Fire')},
	{'name':'pkmn_water', 'bronze':10, 'silver':50, 'gold':200, 'i18n_name':_('Water')},
	{'name':'pkmn_electric', 'bronze':10, 'silver':50, 'gold':200, 'i18n_name':_('Electric')},
	{'name':'pkmn_psychic', 'bronze':10, 'silver':50, 'gold':200, 'i18n_name':_('Psychic')},
	{'name':'pkmn_dark', 'bronze':10, 'silver':50, 'gold':200, 'i18n_name':_('Dark')},
	{'name':'pkmn_fairy', 'bronze':10, 'silver':50, 'gold':200, 'i18n_name':_('Fairy')},
	{'name':'pkmn_fighting', 'bronze':10, 'silver':50, 'gold':200, 'i18n_name':_('Fighting')},
	{'name':'pkmn_ghost', 'bronze':10, 'silver':50, 'gold':200, 'i18n_name':_('Ghost')},
	{'name':'pkmn_ice', 'bronze':10, 'silver':50, 'gold':200, 'i18n_name':_('Ice')},
	{'name':'pkmn_dragon', 'bronze':10, 'silver':50, 'gold':200, 'i18n_name':_('Dragon')},
]

STATS = [
	'dex_caught',
	'dex_seen',
	'gym_badges',
	'xp'
]

def TrainerProfileHTMLView(request, username=None):
	if username:
		trainer = get_object_or_404(Trainer, username__iexact=username)
	elif request.GET.get('username'):
		trainer = get_object_or_404(Trainer, username__iexact=request.GET.get('username'))
	elif request.GET.get('id'):
		trainer = get_object_or_404(Trainer, pk=request.GET.get('id'))
	elif not request.user.is_authenticated():
		return redirect('home')
	else:
		trainer = get_object_or_404(Trainer, owner=request.user, prefered=True)
	context = {
		'trainer' : trainer,
		'updates' : Update.objects.filter(trainer=trainer),
	}
	badges = []
	type_badges = []
	for badge in BADGES:
		badge_dict = {
			'name':badge['name'],
			'readable_name':badge['i18n_name'],
		}
		try:
			badge_dict['value'] = getattr(Update.objects.filter(trainer=trainer).exclude(**{badge['name'] : None}).order_by('-'+badge['name']).first(), badge['name'])
			if badge_dict['value'] < badge['bronze']:
				badge_dict['percent'] = int(percentage(badge_dict['value'],badge['bronze'],0))
			elif badge_dict['value'] < badge['silver']:
				badge_dict['percent'] = int(percentage(badge_dict['value'],badge['silver'],0))
			elif badge_dict['value'] < badge['gold']:
				badge_dict['percent'] = int(percentage(badge_dict['value'],badge['gold'],0))
			else:
				badge_dict['percent'] = 100
			badge_dict['time'] = getattr(Update.objects.filter(trainer=trainer).exclude(**{badge['name'] : None}).order_by('-'+badge['name']).first(), 'update_time')
		except AttributeError:
			continue
		badges.append(badge_dict)
	for badge in TYPE_BADGES:
		badge_dict = {
			'name':badge['name'],
			'readable_name':badge['i18n_name'],
		}
		try:
			badge_dict['value'] = getattr(Update.objects.filter(trainer=trainer).exclude(**{badge['name'] : None}).order_by('-'+badge['name']).first(), badge['name'])
			if badge_dict['value'] < badge['bronze']:
				badge_dict['percent'] = int(percentage(badge_dict['value'],badge['bronze'],0))
			elif badge_dict['value'] < badge['silver']:
				badge_dict['percent'] = int(percentage(badge_dict['value'],badge['silver'],0))
			elif badge_dict['value'] < badge['gold']:
				badge_dict['percent'] = int(percentage(badge_dict['value'],badge['gold'],0))
			else:
				badge_dict['percent'] = 100
			badge_dict['time'] = getattr(Update.objects.filter(trainer=trainer).exclude(**{badge['name'] : None}).order_by('-'+badge['name']).first(), 'update_time')
		except AttributeError:
			continue
		type_badges.append(badge_dict)
	for badge in STATS:
		try:
			context[badge] = getattr(Update.objects.filter(trainer=trainer).exclude(**{badge : None}).order_by('-'+badge).first(), badge)
			context[badge+'-time'] = getattr(Update.objects.filter(trainer=trainer).exclude(**{badge : None}).order_by('-'+badge).first(), 'update_time')
		except AttributeError:
			continue
	context['level'] = level_parser(xp=context['xp'])
	context['badges'] = badges
	context['type_badges'] = type_badges
	
	if request.user == trainer.owner:
		form_data = request.POST.copy()
		form_data['trainer'] = trainer.pk
		form_data['update_time'] = timezone.now()
		form_data['meta_source'] = 'web_quick'
		form = QuickUpdateForm(form_data or None)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('profile')+'?id={}#history-panel'.format(trainer.pk))
		form.fields['trainer'].queryset = Trainer.objects.filter(owner=request.user)
		if request.method == 'GET':
			form.fields['trainer'].initial = get_object_or_404(Trainer, owner=request.user, prefered=True)
		context['form'] = form
	
	return render(request, 'profile.html', context)

@login_required
def CreateUpdateHTMLView(request):
	if request.POST:
		form_data = request.POST.copy()
		form_data['meta_source'] = 'web_detailed'
	else:
		form_data = None
	form = UpdateForm(form_data or None)
	form.fields['update_time'].widget = forms.HiddenInput()
	if form.is_valid() and (int(request.POST['trainer']),) in Trainer.objects.filter(owner=request.user).values_list('pk'):
		print('valid')
		form.save()
		return HttpResponseRedirect(reverse('profile')+'?id={}#history-panel'.format(request.POST['trainer']))
	else:
		print(form.errors)
	form.fields['trainer'].queryset = Trainer.objects.filter(owner=request.user)
	if request.method == 'GET':
		form.fields['trainer'].initial = get_object_or_404(Trainer, owner=request.user, prefered=True)
	return render(request, 'create_update.html', {'form': form})

def LeaderboardHTMLView(request):
	#Defining Parameters
	showValor = {'param':'Valor', 'value':nullbool(request.GET.get('valor'), default=True)}
	showMystic = {'param':'Mystic', 'value':nullbool(request.GET.get('mystic'), default=True)}
	showInstinct = {'param':'Instinct', 'value':nullbool(request.GET.get('instinct'), default=True)}
	showSpoofers = {'param':'currently_cheats', 'value':nullbool(request.GET.get('spoofers'), default=False)}
	
	_trainers_query = Trainer.objects.exclude(statistics=False)
	for param in (showValor, showMystic, showInstinct):
		if param['value'] is False:
			_trainers_query = _trainers_query.exclude(faction__name=param['param'])
	_trainers_non_legit = _trainers_query.exclude(currently_cheats = False).annotate(Max('update__xp'), Max('update__update_time'), Max('update__pkmn_caught'), Max('update__gym_defended'), Max('update__eggs_hatched'), Max('update__walk_dist'), Max('update__pkstops_spun'))
	_trainers_non_legit = cleanleaderboardqueryset(_trainers_non_legit, key=lambda x: x.update__xp__max, reverse=True)
	_trainers_legit = _trainers_query.exclude(currently_cheats = True).annotate(Max('update__xp'), Max('update__update_time'), Max('update__pkmn_caught'), Max('update__gym_defended'), Max('update__eggs_hatched'), Max('update__walk_dist'), Max('update__pkstops_spun'))
	_trainers_legit = cleanleaderboardqueryset(_trainers_legit, key=lambda x: x.update__xp__max, reverse=True)
	
	_trainers = []
	grand_total_xp = 0
	for trainer in _trainers_legit:
		grand_total_xp += trainer.update__xp__max
		_trainers.append({
			'position' : _trainers_legit.index(trainer)+1,
			'trainer' : trainer,
			'xp' : trainer.update__xp__max,
			'pkmn_caught' : trainer.update__pkmn_caught__max,
			'gym_defended' : trainer.update__gym_defended__max,
			'eggs_hatched' : trainer.update__eggs_hatched__max,
			'walk_dist' : trainer.update__walk_dist__max,
			'pkstops_spun' : trainer.update__pkstops_spun__max,
			'time' : trainer.update__update_time__max,
			'level' : level_parser(xp=trainer.update__xp__max).level,
		})
	if showSpoofers['value']:
		for trainer in _trainers_non_legit:
			grand_total_xp += trainer.update__xp__max
			_trainers.append({
				'position' : None,
				'trainer' : trainer,
				'xp' : trainer.update__xp__max,
				'pkmn_caught' : trainer.update__pkmn_caught__max,
				'gym_defended' : trainer.update__gym_defended__max,
				'eggs_hatched' : trainer.update__eggs_hatched__max,
				'walk_dist' : trainer.update__walk_dist__max,
				'pkstops_spun' : trainer.update__pkstops_spun__max,
				'time' : trainer.update__update_time__max,
				'level' : level_parser(xp=trainer.update__xp__max).level,
			})
	_trainers.sort(key = lambda x: x['xp'], reverse=True)
	
	return render(request, 'leaderboard.html', {'leaderboard' : _trainers, 'valor' : showValor, 'mystic' : showMystic, 'instinct' : showInstinct, 'spoofers' : showSpoofers, 'grand_total_xp' : grand_total_xp})
