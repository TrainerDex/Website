from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.models import User
from django.db.models import PositiveIntegerField
from django.shortcuts import get_object_or_404, render
from rest_framework import permissions
from rest_framework.decorators import detail_route
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from trainer.models import Trainer, Faction, Update, DiscordGuild
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
		user = Trainer.owner
	except Trainer.DoesNotExist:
		raise Http404("Trainer not found")
	context = {
		'trainer' : trainer,
	}
	
	for field in Update._meta.get_fields():
		if type(field) == PositiveIntegerField or field.name == 'walk_dist':
			try:
				context[field.name] = getattr(Update.objects.filter(trainer=trainer).exclude(**{field.name : None}).order_by('-'+field.name).first(), field.name)
			except AttributeError:
				context[field.name] = None
	
	return render(request, 'profile.html', context)
