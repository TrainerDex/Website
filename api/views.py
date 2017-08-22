from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *

class TrainersList(APIView):
	
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
	
class LevelList(APIView):
	
	def get(self, request):
		levels = Trainer_Levels.objects.all()
		serializer = Trainer_Levels_Serializer(levels, many=True)
		return Response(serializer.data)
	
	def post(self, request, format=None):
		serializer = Trainer_Levels_Serializer(data=request.data)
		if  serializer.is_valid():
			return Response(serializer.errors, status=status.HTTP_423_LOCKED) 
		return Response(serializer.errors, status=status.HTTP_423_LOCKED)
	
class ExperienceList(APIView):
	
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