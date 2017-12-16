from django.forms import ModelForm
from trainer.models import Update, Trainer

class UpdateForm(ModelForm):
	class Meta:
		model = Update
		fields = '__all__'
		localized_fields = ('update_time',)
	
	def __init__(self, trainers, *args, **kwargs):
		super(UpdateForm, self).__init__(*args, **kwargs)
		
		self.fields['trainer'].queryset = trainers
