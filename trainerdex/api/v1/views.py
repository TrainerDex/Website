import datetime
import logging

from allauth.socialaccount.models import SocialAccount
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.mail import mail_admins
from django.db.models.functions import DenseRank as Rank
from django.db.models import F, Max, Q, Window
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework import authentication, permissions, status

# from core.models import DiscordGuild, get_guild_info
from trainerdex.api.v1.serializers import BriefUpdateSerializer, DetailedUpdateSerializer, SocialAllAuthSerializer, TrainerSerializer, UserSerializer
from trainerdex.models import Trainer, Update

log = logging.getLogger('django.trainerdex')
User = get_user_model()

def recent(value):
    if timezone.now()-datetime.timedelta(hours=1) <= value <= timezone.now():
        return True
    return False

class UserViewSet(ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.exclude(is_active=False, gdpr=False, is_service_user=True)

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
    
    def get_object(self, pk: int) -> Trainer:
        try:
            obj = Trainer.objects.get(id=pk)
        except Trainer.DoesNotExist:
            raise Http404
        
        if not obj.user.gdpr:
            raise PermissionDenied
        
        if not obj.user.is_active:
            raise Http404
        
        return obj
    
    def get(self, request, pk: int) -> Response:
        trainer = self.get_object(pk)
        serializer = TrainerSerializer(trainer)
        return Response(serializer.data)

class UpdateListView(APIView):
    """
    get:
        parameters
        ---------
        detail:
            bool
    """
    
    authentication_classes = (authentication.TokenAuthentication,)
    
    def get_trainer(self, pk: int) -> Trainer:
        try:
            obj = Trainer.objects.get(id=pk)
        except Trainer.DoesNotExist:
            raise Http404
        
        if not obj.user.gdpr:
            raise PermissionDenied
        
        if not obj.user.is_active:
            raise Http404
        
        return obj
    
    def get(self, request, pk: int) -> Response:
        updates = Update.objects.filter(trainer=self.get_trainer(pk))
        serializer = BriefUpdateSerializer(updates, many=True) if request.GET.get('detail') != "1" else DetailedUpdateSerializer(updates, many=True)
        return Response(serializer.data, status=status.HTTP_206_PARTIAL_CONTENT)
    

class LatestUpdateView(APIView):
    """
    get:
        Returns the latest update of the user
    """
    
    authentication_classes = (authentication.TokenAuthentication,)
    
    def get_trainer(self, pk: int) -> Trainer:
        try:
            obj = Trainer.objects.get(id=pk)
        except Trainer.DoesNotExist:
            raise Http404
        
        if not obj.user.gdpr:
            raise PermissionDenied
        
        if not obj.user.is_active:
            raise Http404
        
        return obj
    
    def get_object(self, pk: int) -> Update:
        try:
            obj = Update.objects.filter(trainer=self.get_trainer(pk)).latest('update_time')
        except Update.DoesNotExist:
            raise Http404
        
        return obj
    
    def get(self, request, pk: int) -> Response:
        update = self.get_object(pk)
        serializer = DetailedUpdateSerializer(update)
        return Response(serializer.data)
    

class UpdateDetailView(APIView):
    """
    get:
        Returns an update object
    """
    
    authentication_classes = (authentication.TokenAuthentication,)
    
    def get_trainer(self, pk: int) -> Trainer:
        try:
            obj = Trainer.objects.get(id=pk)
        except Trainer.DoesNotExist:
            raise Http404
        
        if not obj.user.gdpr:
            raise PermissionDenied
        
        if not obj.user.is_active:
            raise Http404
        
        return obj
    
    def get_object(self, pk: int, uuid) -> Update:
        try:
            obj = Update.objects.get(trainer=self.get_trainer(pk), uuid=uuid)
        except Update.DoesNotExist:
            raise Http404
        
        return obj
    
    def get(self, request, pk: int, uuid) -> Response:
        update = self.get_object(trainer=pk, uuid=uuid)
        serializer = DetailedUpdateSerializer(update)
        return Response(serializer.data)


class SocialLookupView(APIView):
    """
    get:
        parameters
        ---------
        provider:
            str, required
            options are 'discord', 'facebook', 'google', 'twitter'
        uid:
            int
            Social ID, supports a comma seperated list
        user:
            int
            New TrainerDex User IDs (all users have this)
        trainer:
            int
            Old TrainerDex Trainer IDs (not all users have this)
    """
    
    def get(self, request) -> Response:
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
