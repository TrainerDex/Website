from rest_framework.routers import SimpleRouter
from trainer.views import *

router = SimpleRouter()
router.register("users", UserViewSet)
router.register("trainers", TrainerViewSet)
router.register("factions", FactionViewSet)
router.register("update", UpdateViewSet)
router.register("guilds", DiscordGuildViewSet)

urlpatterns = router.urls
