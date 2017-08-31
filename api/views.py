from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *

class Factions_List(APIView):
	
	def get(self, request):
		factions = Factions.objects.all()
		serializer = Factions_Serializer(factions, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = Factions_Serializer(data=request.data)
		if  serializer.is_valid():
			return Response(serializer.errors, status=status.HTTP_423_LOCKED) 
		return Response(serializer.errors, status=status.HTTP_423_LOCKED)

class Trainers_List(APIView):
	
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
		levels = Trainer_Levels.objects.all()
		serializer = Trainer_Levels_Serializer(levels, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = Trainer_Levels_Serializer(data=request.data)
		if  serializer.is_valid():
			return Response(serializer.errors, status=status.HTTP_423_LOCKED) 
		return Response(serializer.errors, status=status.HTTP_423_LOCKED)

class Experience_List(APIView):
	
	def get(self, request):
		experience = Experience.objects.all()
		serializer = Experience_Serializer(experience, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = Experience_Serializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Discord_Users_List(APIView):
	
	def get(self, request):
		discord = Discord_Users.objects.all()
		serializer = Discord_Users_Serializer(discord, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = Discord_Users_Serializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Discord_Servers_List(APIView):
	
	def get(self, request):
		server = Discord_Servers.objects.all()
		serializer = Discord_Servers_Serializer(server, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = Discord_Servers_Serializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Discord_Relations_List(APIView):
	
	def get(self, request):
		donserver = Discord_Relations.objects.all()
		serializer = Discord_Relations_Serializer(donserver, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = Discord_Relations_Serializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)