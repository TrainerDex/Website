from rest_framework.routers import SimpleRouter
from raids.views import *

router = SimpleRouter()
router.register("raids", RaidViewset)
urlpatterns = router.urls

# /gyms/
# GET - Search for a gym using GET parameters
# 	{ 'coordinates' : vector, 'range': int in km, defaults to 1 }
# /gyms/<str:uuid>/
# GET - Shows what's in our database
# PUT/PATCH - Pulls latest information from GymHuntr
# /gyms/<str:uuid>/raids/
# POST - Submit information about a raid
# /gyms/<str:uuid>/raids/current/
# /gyms/<str:uuid>/raids/<int:uuid>/
# GET - Information about raid and gym, anonymous list of trainers, unless access granted
# PATCH - update a users enrollment status (when used from a bot)
# 	{'trainer' : <int:id>, 'status' : str mapped states}
# /gyms/<str:uuid>/raids/<int:uuid>/<str:state>/
# PUT - updates user to that status when standard credentials are handed over via http auth headers
