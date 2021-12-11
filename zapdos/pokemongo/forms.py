from django.forms import ModelForm

from pokemongo.models import MedalProgressPost


class MedalProgressForm(ModelForm):
    class Meta:
        model = MedalProgressPost
        fields = "__all__"
