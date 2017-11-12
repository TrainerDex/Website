from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from enrollment.serializers import EnrollmentSerializer, CreateEnrollmentSerializer
from enrollment.models import Enrollment as EnrollmentModel
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework import status

class EnrollmentViewset(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    queryset = EnrollmentModel.objects.all()

    @detail_route(methods=['POST'])
    def done(self, request, pk=None):
        self.queryset.objects.filter(gym_id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['GET'])
    def gym(self, request, pk=None):
        queryset = self.queryset.filter(gym_id=pk)
        gyms = self.serializer_class(queryset, many=True)
        return Response(gyms.data)

    def get_serializer_class(self): 
        serializer_class = self.serializer_class 
        if self.request.method == 'POST': 
            serializer_class = CreateEnrollmentSerializer
        return serializer_class

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
        else:
            serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(None, status=status.HTTP_201_CREATED, headers=headers)
        

"""
Enrollment:
POST: Add yourself as going
PUT: Update, add yourself as arrived
GET: Members going anywhere
DETAIL: Where is member going?

Gym:
GET: Gyms with members going
DETAIL: Who is going to this GYM?
POST: Gym is done
"""
