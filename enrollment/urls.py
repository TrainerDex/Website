from rest_framework.routers import SimpleRouter
from enrollment.views import *

router = SimpleRouter()
router.register("raids", RaidViewset)
urlpatterns = router.urls