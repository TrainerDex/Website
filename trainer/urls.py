# -*- coding: utf-8 -*-
from rest_framework.routers import SimpleRouter

from trainer.views import *

router = SimpleRouter()
router.register("users", UserViewSet)
router.register("trainers", TrainerViewSet)
router.register("factions", FactionViewSet)
router.register("update", UpdateViewSet)
router.register("discord/users", DiscordUserViewSet)
router.register("discord/servers", DiscordServerViewSet)

urlpatterns = router.urls