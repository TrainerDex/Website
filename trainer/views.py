from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *

class Faction_List(APIView):
	
	def get(self, request):
		factions = Faction.objects.all()
		serializer = Faction_Serializer(factions, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = Faction_Serializer(data=request.data)
		if  serializer.is_valid():
			return Response(serializer.errors, status=status.HTTP_423_LOCKED) 
		return Response(serializer.errors, status=status.HTTP_423_LOCKED)

class Trainer_List(APIView):
	
	def get(self, request):
		trainers = Trainer.objects.all()
		serializer = Trainer_Serializer(trainers, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = Trainer_Serializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Level_List(APIView):
	
	def get(self, request):
		levels = Trainer_Level.objects.all()
		serializer = Trainer_Level_Serializer(levels, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = Trainer_Level_Serializer(data=request.data)
		if  serializer.is_valid():
			return Response(serializer.errors, status=status.HTTP_423_LOCKED) 
		return Response(serializer.errors, status=status.HTTP_423_LOCKED)

class Update_List(APIView):
	
	def get(self, request):
		experience = Update.objects.all()
		serializer = Update_Serializer(experience, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = Update_Serializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Discord_User_List(APIView):
	
	def get(self, request):
		discord = Discord_User.objects.all()
		serializer = Discord_User_Serializer(discord, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = Discord_User_Serializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Discord_Server_List(APIView):
	
	def get(self, request):
		server = Discord_Server.objects.all()
		serializer = Discord_Server_Serializer(server, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = Discord_Server_Serializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Discord_Relation_List(APIView):
	
	def get(self, request):
		donserver = Discord_Relation.objects.all()
		serializer = Discord_Relation_Serializer(donserver, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = Discord_Relations_Serializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)