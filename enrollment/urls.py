from enrollment.views import EnrollmentViewset
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', EnrollmentViewset)
urlpatterns = router.urls
