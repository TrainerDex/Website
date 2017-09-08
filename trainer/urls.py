from rest_framework.routers import SimpleRouter

from .views import *

router = SimpleRouter()
router.register("users", UserViewSet)
router.register("trainers", TrainerViewSet)
router.register("teams", FactionViewSet)
router.register("factions", FactionViewSet)
router.register("update", UpdateViewSet)
router.register("xp", UpdateViewSet)
router.register("stats", UpdateViewSet)
router.register("discord/users", DiscordUserViewSet)
router.register("discord/servers", DiscordServerViewSet)
router.register("networks", NetworkViewSet)
router.register("bans", BanViewSet)
router.register("reports", ReportViewSet)

urlpatterns = router.urls