from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import detail_route
from rest_framework import permissions
from django.contrib.auth.models import User
from trainer.models import *
from allauth.socialaccount.models import SocialAccount
from trainer.serializers import *

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

class DiscordGuildViewSet(ModelViewSet):
	serializer_class = DiscordGuildSerializer
	queryset = DiscordGuild.objects.all()
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
