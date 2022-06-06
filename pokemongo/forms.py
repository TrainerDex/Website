from django.forms import ModelForm

from pokemongo.models import Trainer, Update
from pokemongo.shortcuts import BATTLE_HUB_STATS, STANDARD_MEDALS, UPDATE_FIELDS_TYPES


class UpdateForm(ModelForm):
    class Meta:
        model = Update
        fields = (
            [
                "trainer",
                "update_time",
                "data_source",
                "double_check_confirmation",
                "gym_gold",
                "mini_collection",
            ]
            + STANDARD_MEDALS
            + BATTLE_HUB_STATS
            + UPDATE_FIELDS_TYPES
        )


class TrainerForm(ModelForm):
    class Meta:
        model = Trainer
        fields = (
            "start_date",
            "faction",
            "statistics",
            "trainer_code",
            "country_iso",
            "verification",
        )
