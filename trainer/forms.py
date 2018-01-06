from django.forms import ModelForm
from trainer.models import Update, Trainer

class QuickUpdateForm(ModelForm):
	
	class Meta:
		model = Update
		fields = ('trainer', 'xp', 'update_time', 'meta_source')
	

class UpdateForm(ModelForm):
	
	class Meta:
		model = Update
		fields = '__all__'
	
