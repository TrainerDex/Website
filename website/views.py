from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from website.models import Discord, FacebookGroup, WhatsApp, MessengerGroup
from trainer.models import ExtendedProfile, Faction
from itertools import chain

def IndexView(request):
	return render(request, 'index.html')

def CommunityListView(request):
	discord_list = Discord.objects.all()
	facebookgroup_list = FacebookGroup.objects.all()
	messengergroup_list = MessengerGroup.objects.all()
	whatsapp_list = WhatsApp.objects.all()
	community_list = list(chain(discord_list, facebookgroup_list, whatsapp_list, messengergroup_list))
	if request.user.is_authenticated():
		community_list = list(filter(lambda x: x.team in (ExtendedProfile.objects.get(user=request.user).prefered_profile.faction, Faction.objects.get(pk=0)), community_list))
	community_list.sort(key=lambda x: x.name)
	context = {
		'community_list' : community_list,
	}
	return render(request, 'communities.html', context)
