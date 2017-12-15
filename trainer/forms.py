from django.forms import ModelForm
from trainer.models import Update

class UpdateForm(ModelForm):
	class Meta:
		model = Update
		fields = ('__all__',)
		localized_fields = ('update_time',)
	
	def __init__(self, *args, **kwargs):
		super(UpdateForm, self).__init__(*args, **kwargs)
		
		self.fields['trainer'].queryset = Trainer.objects.filter(owner=self.instance.user_id)
