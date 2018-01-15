from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, EmailField
from trainer.models import Update, Trainer

class QuickUpdateForm(ModelForm):
	
	class Meta:
		model = Update
		fields = ('trainer', 'xp', 'update_time', 'meta_source')
	

class UpdateForm(ModelForm):
	
	class Meta:
		model = Update
		fields = '__all__'
	

class RegistrationFormUser(UserCreationForm):
	email = EmailField(required=True)
	
	class Meta:
		model = User
		fields = ('username', 'email','password1','password2',)
	
	def save(self, commit=True):
		user = super(RegistrationFormUser, self).save(commit=False)
		user.email = self.cleaned_data["email"]
		if commit:
			user.save()
		return user

class RegistrationFormTrainer(ModelForm):
	
	class Meta:
		model = Trainer
		fields = ('username', 'start_date', 'faction', 'statistics',)

class RegistrationFormUpdate(ModelForm):
	
	class Meta:
		model = Update
		fields = ('xp',)
