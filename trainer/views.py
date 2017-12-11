from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import detail_route
from rest_framework import permissions
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from trainer.models import Trainer, Faction, Update, DiscordGuild
from allauth.socialaccount.models import SocialAccount
from trainer.serializers import UserSerializer, TrainerSerializer, FactionSerializer, UpdateSerializer, DiscordGuildSerializer

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

def profile(request, username):
	try:
		trainer = Trainer.objects.get(username__iexact=username)
		updates = Update.objects.filter(trainer=trainer)
		xp = 0
		for i in updates:
			if i.xp > xp:
				xp = i.xp
		#user = Trainer.owner
	except Trainer.DoesNotExist:
		raise Http404("User not found")
	context = {
		'trainer' : trainer,
		'update_list' : updates,
		'xp': xp,
	}
	return render(request, 'profile.html', context)
