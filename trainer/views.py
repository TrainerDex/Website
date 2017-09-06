from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route, list_route
from .models import *
from .serializers import *

class UserList(APIView):
	
	def get(self, request, *args, **kwargs):
		users = User.objects.all()
		serializer = UserSerializer(users, many=True)
		filter_fields = ('username', 'id')
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = TrainerSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TrainerList(APIView):
	
	def get(self, request, *args, **kwargs):
		trainers = Trainer.objects.all()
		serializer = TrainerSerializer(trainers, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = TrainerSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FactionList(APIView):
	
	def get(self, request):
		factions = Faction.objects.all()
		serializer = FactionSerializer(factions, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = FactionSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	
	

class UpdateList(APIView):
	
	def get(self, request):
		update = Update.objects.all()
		serializer = UpdateSerializer(update, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = UpdateSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	
class DiscordUserList(APIView):
	
	def get(self, request):
		discord = DiscordUser.objects.all()
		serializer = DiscordUserSerializer(discord, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = DiscordUserSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	
class DiscordServerList(APIView):
	
	def get(self, request):
		server = DiscordServer.objects.all()
		serializer = DiscordServerSerializer(server, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = DiscordServerSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DiscordMemberList(APIView):
	
	def get(self, request):
		member = DiscordMember.objects.all()
		serializer = DiscordMemberSerializer(member, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = DiscordMemberSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NetworkList(APIView):
	
	def get(self, request):
		network = Network.objects.all()
		serializer = NetworkSerializer(network, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = NetworkSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NetworkMemberList(APIView):
	
	def get(self, request):
		network = NetworkMember.objects.all()
		serializer = NetworkMemberSerializer(network, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = NetworkMemberSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BanList(APIView):
	
	def get(self, request):
		ban = Ban.objects.all()
		serializer = BanSerializer(ban, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = BanSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReportList(APIView):
	
	def get(self, request):
		report = Report.objects.all()
		serializer = ReportSerializer(report, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = ReportSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)