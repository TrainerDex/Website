from rest_framework.viewsets import ModelViewSet

from pokemongo.api.v2.serializers.trainers import NicknameSerializer
from pokemongo.models import Nickname


class NicknameViewSet(ModelViewSet):
    serializer_class = NicknameSerializer

    def get_queryset(self):
        return Nickname.objects.filter(trainer__uuid=self.kwargs["uuid"]).order_by(
            "-active", "nickname"
        )
