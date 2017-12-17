from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from ajax_select.admin import AjaxSelectAdmin
from ajax_select import make_ajax_form
from trainer.models import *

class XUserForm(forms.ModelForm):
	class Meta:
		model = ExtendedProfile
		fields = ['dob','prefered_profile']
	
	def __init__(self, *args, **kwargs):
		super(XUserForm, self).__init__(*args, **kwargs)
		
		self.fields['prefered_profile'].queryset = Trainer.objects.filter(owner=self.instance.user_id)

class XUserInline(admin.StackedInline):
	model = ExtendedProfile
	can_delete = False
	form = XUserForm

class UserAdmin(BaseUserAdmin):
	inlines = (XUserInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Faction)

@admin.register(Update)
class UpdateAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(Update, {
		'trainer' : 'trainer'
	})
	list_display = ('trainer', 'xp', 'update_time')
	search_fields = ('trainer__username', 'trainer__owner__username')
	ordering = ('-update_time',)
	date_hierarchy = 'update_time'

@admin.register(Trainer)
class TrainerAdmin(AjaxSelectAdmin):
	
	form = make_ajax_form(Trainer, {
		'username' : 'user'
	})
	list_display = ('username', 'faction', 'currently_cheats', 'statistics')
	list_filter = ('faction', 'has_cheated', 'currently_cheats', 'statistics')
	search_fields = ('username', 'owner__username', 'owner__first_name')
	ordering = ('username',)
	date_hierarchy = 'start_date'
