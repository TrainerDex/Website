import datetime
import logging

from allauth.socialaccount.models import SocialAccount
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.core.mail import mail_admins
from django.db.models.functions import DenseRank as Rank
from django.db.models import F, Max, Q, Window
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework import authentication, permissions, status

# from core.models import DiscordGuild, get_guild_info
from trainerdex.api.v1.serializers import BriefUpdateSerializer, DetailedUpdateSerializer, LeaderboardSerializer, SocialAllAuthSerializer, TrainerSerializer, UserSerializer
from trainerdex.models import Trainer, Update
from trainerdex.shortcuts import filter_leaderboard_qs

log = logging.getLogger('django.trainerdex')
User = get_user_model()

def recent(value):
    if timezone.now()-datetime.timedelta(hours=1) <= value <= timezone.now():
        return True
    return False

class UserViewSet(ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.exclude(is_active=False, gdpr=False)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class TrainerListView(APIView):
    """
    get:
    Accepts paramaters for Team (t) and Nickname (q)
    """
    
    authentication_classes = (authentication.TokenAuthentication,)
    
    def get(self, request):
        queryset = Trainer.objects.exclude(user__is_active=False)
        if request.GET.get('q') or request.GET.get('t'):
            if request.GET.get('q'):
                queryset = queryset.filter(nickname__nickname__iexact=request.GET.get('q'))
            if request.GET.get('t'):
                queryset = queryset.filter(faction=request.GET.get('t'))
        
        serializer = TrainerSerializer(queryset, many=True)
        return Response(serializer.data)
    

class TrainerDetailView(APIView):
    """
    get:
    Trainer detail
    """
    
    authentication_classes = (authentication.TokenAuthentication,)
    
    def get_object(self, pk):
        return get_object_or_404(Trainer, id=pk, user__is_active=True, user__gdpr=True)
    
    def get(self, request, pk):
        trainer = self.get_object(pk)
        
        if trainer.user.gdpr and trainer.user.is_active:
            serializer = TrainerSerializer(trainer)
            return Response(serializer.data)
        return Response(None, status=status.HTTP_403_FORBIDDEN)

class UpdateListView(APIView):
    """
    get:
    Takes Trainer ID as part of URL, optional param: detail, shows all detail, otherwise, returns a list of objects with fields 'time_updated' (datetime.datetime), 'xp'(int) and 'fields_updated' (list)
    """
    
    authentication_classes = (authentication.TokenAuthentication,)
    
    def get(self, request, pk):
        updates = Update.objects.filter(trainer=pk, trainer__user__is_active=True)
        serializer = BriefUpdateSerializer(updates, many=True) if request.GET.get('detail') != "1" else DetailedUpdateSerializer(updates, many=True)
        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)
    

class LatestUpdateView(APIView):
    """
    get:
    Gets detailed view of the latest update
    """
    
    authentication_classes = (authentication.TokenAuthentication,)
    
    def get(self, request, pk):
        try:
            update = Update.objects.filter(trainer=pk, trainer__user__is_active=True).latest('update_time')
        except Update.DoesNotExist:
            return Response(None, status=404)
        serializer = DetailedUpdateSerializer(update)
        return Response(serializer.data)
    

class UpdateDetailView(APIView):
    """
    get:
    Gets detailed view
    """
    
    authentication_classes = (authentication.TokenAuthentication,)
    
    def get(self, request, uuid, pk):
        update = get_object_or_404(Update, trainer=pk, uuid=uuid, trainer__user__is_active=True)
        serializer = DetailedUpdateSerializer(update)
        if update.trainer.id != int(pk):
            return Response(status=400)
        return Response(serializer.data)
    

class LeaderboardView(APIView):
    """
    Limited to 5000
    """
    
    def get(self, request):
        query = filter_leaderboard_qs(Trainer.objects)
        if request.GET.get('users'):
            query = filter_leaderboard_qs(Trainer.objects.filter(id__in=request.GET.get('users').split(',')))
        leaderboard = query.prefetch_related('update_set') \
            .prefetch_related('user') \
            .annotate(Max('update__total_xp'), Max('update__update_time')) \
            .exclude(update__total_xp__max__isnull=True)
        if datetime.datetime(2019,3,31,23,00) < datetime.datetime.now() < datetime.datetime(2019,4,1,23,00):
            leaderboard = leaderboard.annotate(rank=Window(expression=Rank(), order_by=F('update__total_xp__max').asc())) \
                .order_by('rank')
        else:
            leaderboard = leaderboard.annotate(rank=Window(expression=Rank(), order_by=F('update__total_xp__max').desc())) \
                .order_by('rank')
        serializer = LeaderboardSerializer(leaderboard[:5000], many=True)
        return Response(serializer.data)
    

class SocialLookupView(APIView):
    """
    get:
        kwargs:
            provider (requiered) - platform, options are 'facebook', 'twitter', 'discord', 'google', 'patreon'
        
            uid - Social ID, supports a comma seperated list. Could be useful for passing a list of users in a server to retrieve a list of UserIDs, which could then be passed to api/v1/leaderboard/
            user - TrainerDex User ID, supports a comma seperated list
            trainer - TrainerDex Trainer ID
    """
    
    def get(self, request):
        query = SocialAccount.objects.exclude(user__is_active=False).filter(provider=request.GET.get('provider'))
        if request.GET.get('uid'):
            query = query.filter(uid__in=request.GET.get('uid').split(','))
        elif request.GET.get('user'):
            query = query.filter(user__in=request.GET.get('user').split(','))
        elif request.GET.get('trainer'):
            query = query.filter(user__trainer=request.GET.get('trainer'))
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = SocialAllAuthSerializer(query, many=True)
        return Response(serializer.data)

class DiscordLeaderboardAPIView(APIView):
    pass
#     def get(self, request, guild):
#         output = {'generated':datetime.datetime.utcnow()}
#
#         try:
#             server = DiscordGuild.objects.get(id=int(guild))
#         except DiscordGuild.DoesNotExist:
#             logger.warn(f"Guild with id {guild} not found")
#             try:
#                 i = get_guild_info(int(guild))
#             except:
#                 return Response({'error': 'Access Denied', 'cause': "The bot doesn't have access to this guild.", 'solution': "Add the bot account to the guild."}, status=404)
#             else:
#                 logger.info(f"{i['name']} found. Creating.")
#                 server, created = DiscordGuild.objects.get_or_create(id=int(guild), defaults={'data': i, 'cached_date': timezone.now()})
#
#         if not server.data or server.outdated:
#             try:
#                 server.refresh_from_api()
#             except:
#                 return Response(status=424)
#             else:
#                 server.save()
#
#             if not server.has_access:
#                 return Response({'error': 'Access Denied', 'cause': "The bot doesn't have access to this guild.", 'solution': "Add the bot account to the guild."}, status=424)
#             else:
#                 server.sync_members()
#
#         output['title'] = '{title} Leaderboard'.format(title=server.data['name'])
#         opt_out_roles = server.roles.filter(data__name='NoLB') | server.roles.filter(exclude_roles_community_membership_discord__discord=server)
#
#         sq = Q()
#         for x in opt_out_roles:
#             sq |= Q(discordguildmembership__data__roles__contains=[str(x.id)])
#
#         members = server.members.exclude(sq)
#         trainers = filter_leaderboard_qs(Trainer.objects.filter(user__socialaccount__in=members))
#
#         leaderboard = trainers.prefetch_related('update_set') \
#             .prefetch_related('user') \
#             .annotate(Max('update__total_xp'), Max('update__update_time')) \
#             .exclude(update__total_xp__max__isnull=True) \
#             .filter(update__update_time__max__gte=datetime.datetime.now()-relativedelta(months=3, hour=0, minute=0, second=0, microsecond=0))
#         if datetime.datetime(2019,3,31,23,00) < datetime.datetime.now() < datetime.datetime(2019,4,1,23,00):
#             leaderboard = leaderboard.annotate(rank=Window(expression=Rank(), order_by=F('update__total_xp__max').asc())) \
#                 .order_by('rank')
#         else:
#             leaderboard = leaderboard.annotate(rank=Window(expression=Rank(), order_by=F('update__total_xp__max').desc())) \
#                 .order_by('rank')
#         serializer = LeaderboardSerializer(leaderboard, many=True)
#         output['leaderboard'] = serializer.data
#         return Response(output)
