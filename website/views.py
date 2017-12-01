from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from website.models import Discord

def index(request):
	return render(request, 'index.html')

def communities(request):
	discord_list = Discord.objects.all()
	context = {
		'discord_list' : discord_list,
	}
	return render(request, 'communities.html', context)
