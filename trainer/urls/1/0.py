from rest_framework.routers import SimpleRouter
from trainer.views import UserViewSet, TrainerViewSet, FactionViewSet, UpdateViewSet, DiscordGuildViewSet
#from trainer.views import UserViewSet, TrainerViewSet, FactionViewSet, UpdateViewSet, DiscordGuildViewSet, ConnectedSocialViewSet

router = SimpleRouter()
router.register("users", UserViewSet)
router.register("trainers", TrainerViewSet)
router.register("factions", FactionViewSet)
router.register("update", UpdateViewSet)
#ConnectedSocialViewSet needs to be built
router.register("guilds", DiscordGuildViewSet)

urlpatterns = router.urls
