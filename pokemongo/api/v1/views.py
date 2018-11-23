# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger('django.trainerdex')
import requests

from allauth.socialaccount.models import SocialAccount
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.mail import mail_admins
from django.db.models import Max, Q, F, Window
from django.db.models.functions import Rank
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from pytz import utc
from rest_framework import authentication, permissions, status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from pokemongo.models import Trainer, Update
from pokemongo.api.v1.serializers import UserSerializer, BriefTrainerSerializer, DetailedTrainerSerializer, BriefUpdateSerializer, DetailedUpdateSerializer, LeaderboardSerializer, SocialAllAuthSerializer
from pokemongo.shortcuts import filter_leaderboard_qs

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
    """
    Limited to 5000
    """
    
    def get(self, request):
        query = filter_leaderboard_qs(Trainer.objects)
        if request.GET.get('users'):
            query = Trainer.objects.filter(id__in=request.GET.get('users').split(','))
        leaderboard = query.prefetch_related('faction').prefetch_related('update_set').prefetch_related('owner').annotate(Max('update__total_xp'), Max('update__update_time')).exclude(update__total_xp__max__isnull=True).annotate(rank=Window(expression=Rank(), order_by=F(f'update__total_xp__max').desc())).order_by('rank')
        serializer = LeaderboardSerializer(leaderboard[:5000], many=True)
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
        trainers = filter_leaderboard_qs(Trainer.objects.filter(owner__socialaccount__provider='discord', owner__socialaccount__uid__in=members))
        
        leaderboard = trainers.prefetch_related('faction').prefetch_related('update_set').prefetch_related('owner').annotate(Max('update__total_xp'), Max('update__update_time')).exclude(update__total_xp__max__isnull=True).filter(update__update_time__max__gte=datetime.now()-relativedelta(months=3, hour=0, minute=0, second=0, microsecond=0)).annotate(rank=Window(expression=Rank(), order_by=F(f'update__total_xp__max').desc())).order_by('rank')
        serializer = LeaderboardSerializer(leaderboard, many=True)
        output['leaderboard'] = serializer.data
        return Response(output)
