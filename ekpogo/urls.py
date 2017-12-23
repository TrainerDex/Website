from django.contrib.auth.decorators import login_required
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views
from ajax_select import urls as ajex_select_urls
from website.views import *
from trainer.views import TrainerProfileView, LeaderboardView, LeaderboardAPIView, UpdateDialogView
from trainer.urls import TrainerURLs, UserURLs

api_v1_patterns = [
    url(r'^trainers/', include(TrainerURLs, namespace="trainer_profiles")),
    url(r'^users/', include(UserURLs, namespace="user_profiles")),
    url(r'^leaderboard/$', LeaderboardAPIView.as_view()),
#    url(r'^gyms/', include('raids.urls', namespace="raid_enrollment")),
]

def DisordRedirectView(request):
    return redirect('https://discord.gg/pFhMS3s')

urlpatterns = [
    url(r'^api/v1/', include(api_v1_patterns, namespace="api_v1")),
    url(r'^api/admin/', admin.site.urls),
    url(r'^api-token-auth/', views.obtain_auth_token),
    url(r'^ajax_select/', include(ajex_select_urls)),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^$', IndexView, name='home'),
    url(r'^_DISCORD/$', DisordRedirectView, name='discord'),
    url(r'^communities/$', CommunityListView, name='communities'),
    url(r'^leaderboard/$', LeaderboardView, name='leaderboard'),
    url(r'^help/faq$', FAQView, name='faq'),
    url(r'^profile/$', TrainerProfileView, name='profile'),
    url(r'^tools/update_stats/$', UpdateDialogView, name='update_stats'),
    url(r'^(?P<username>[a-zA-Z0-9]+)/$', TrainerProfileView, name='profile_short'),
]

admin.site.site_title = "TrainerDex Admin"
