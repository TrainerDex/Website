from django import forms

class UserForm(forms.ModelForm):
    class Meta:
        model = Directory_Users
        widgets = {
        'password': forms.PasswordInput(),
    }