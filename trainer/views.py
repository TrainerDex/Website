# -*- coding: utf-8 -*-
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import detail_route
from rest_framework import permissions
from django.contrib.auth.models import User
from .models import *
from .serializers import *
from .permissions import IsOwnerOrReadOnly

class UserViewSet(ModelViewSet):
	serializer_class = UserSerializer
	queryset = User.objects.all()
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class TrainerViewSet(ModelViewSet):
	serializer_class = TrainerSerializer
	queryset = Trainer.objects.all()
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class FactionViewSet(ModelViewSet):
	serializer_class = FactionSerializer
	queryset = Faction.objects.all()
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class UpdateViewSet(ModelViewSet):
	serializer_class = UpdateSerializer
	queryset = Update.objects.order_by('-datetime').all()
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
#	permission_classes = (permissions.IsAuthenticatedOrReadOnly,
#						 IsOwnerOrReadOnly,)
	
#	def perform_create(self, serializer):
#		serializer.save(owner=self.request.user)
	
class DiscordUserViewSet(ModelViewSet):
	serializer_class = DiscordUserSerializer
	queryset = DiscordUser.objects.all()
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
	
class DiscordServerViewSet(ModelViewSet):
	serializer_class = DiscordServerSerializer
	queryset = DiscordServer.objects.all()
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class DiscordMemberViewSet(ModelViewSet):
	serializer_class = DiscordMemberSerializer
	queryset = DiscordMember.objects.all()
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class NetworkViewSet(ModelViewSet):
	serializer_class = NetworkSerializer
	queryset = Network.objects.all()
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class NetworkMemberViewSet(ModelViewSet):
	serializer_class = NetworkMemberSerializer
	queryset = NetworkMember.objects.all()
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class BanViewSet(ModelViewSet):
	serializer_class = BanSerializer
	queryset = Ban.objects.all()
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class ReportViewSet(ModelViewSet):
	serializer_class = ReportSerializer
	queryset = Report.objects.all()
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)