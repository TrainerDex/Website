from enrollment.serializers import *
from enrollment.models import *
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
    
    #ToDo
    # [ ] GET: Take GymID in url rather than pk
    # [ ] POST, PATCH, PUT, DELETE: Take GymID but relate to the pk via a lookup. Never give old raids, only the latest. Ended raids only remain for 45 minutes after end time. After 45 minutes, any ARRIVED reports change to COMPLETE and any going reports change to ABORTED. Can still be changed on web interface.
