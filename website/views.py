from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from website.models import Discord, FacebookGroup, WhatsApp
from itertools import chain

def index(request):
	return render(request, 'index.html')

def communities(request):
	discord_list = Discord.objects.all()
	facebookgroup_list = FacebookGroup.objects.all()
	whatsapp_list = WhatsApp.objects.all()
	community_list = list(chain(discord_list, facebookgroup_list, whatsapp_list))
	community_list.sort(key=lambda x: x.name)
	context = {
		'community_list' : community_list,
	}
	return render(request, 'communities.html', context)
