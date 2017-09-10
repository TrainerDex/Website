from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import detail_route
from rest_framework import permissions
from django.contrib.auth.models import User
from .models import *
from .serializers import *

class UserViewSet(ModelViewSet):
	serializer_class = UserSerializer
	queryset = User.objects.all()

class TrainerViewSet(ModelViewSet):
	serializer_class = TrainerSerializer
	queryset = Trainer.objects.all()

class FactionViewSet(ModelViewSet):
	serializer_class = FactionSerializer
	queryset = Faction.objects.all()

class UpdateViewSet(ModelViewSet):
	serializer_class = UpdateSerializer
	queryset = Update.objects.all()
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
	
class DiscordUserViewSet(ModelViewSet):
	serializer_class = DiscordUserSerializer
	queryset = DiscordUser.objects.all()
	
class DiscordServerViewSet(ModelViewSet):
	serializer_class = DiscordServerSerializer
	queryset = DiscordServer.objects.all()

class DiscordMemberViewSet(ModelViewSet):
	serializer_class = DiscordMemberSerializer
	queryset = DiscordMember.objects.all()

class NetworkViewSet(ModelViewSet):
	serializer_class = NetworkSerializer
	queryset = Network.objects.all()

class NetworkMemberViewSet(ModelViewSet):
	serializer_class = NetworkMemberSerializer
	queryset = NetworkMember.objects.all()

class BanViewSet(ModelViewSet):
	serializer_class = BanSerializer
	queryset = Ban.objects.all()

class ReportViewSet(ModelViewSet):
	serializer_class = ReportSerializer
	queryset = Report.objects.all()