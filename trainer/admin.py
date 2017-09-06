from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from trainer.models import *

admin.site.register(Trainer)
admin.site.register(Faction)
admin.site.register(Update)
admin.site.register(DiscordUser)
admin.site.register(DiscordServer)
admin.site.register(DiscordMember)
admin.site.register(Network)
admin.site.register(NetworkMember)
admin.site.register(Ban)
admin.site.register(Report)

class XUserInline(admin.StackedInline):
	model = ExtendedProfile
	can_delete = False
	
class UserAdmin(BaseUserAdmin):
	inlines = (XUserInline,)
	
admin.site.unregister(User)
admin.site.register(User, UserAdmin)