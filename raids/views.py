from raids.serializers import *
from raids.models import *
from rest_framework import viewsets
from rest_framework import permissions

class EnrollmentViewset(viewsets.ModelViewSet):
	serializer_class = EnrollmentSerializer
	queryset = Enrollment.objects.all()
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

class RaidViewset(viewsets.ModelViewSet):
	serializer_class = RaidSerializer
	queryset = Raid.objects.all()
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
	

