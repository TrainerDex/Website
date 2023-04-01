from django.forms import ModelForm

from pokemongo.models import (
    BATTLE_HUB_STATS,
    STANDARD_MEDALS,
    UPDATE_FIELDS_TYPES,
    Trainer,
    Update,
)


class UpdateForm(ModelForm):
    class Meta:
        model = Update
        fields = (
            [
                "trainer",
                "update_time",
                "data_source",
                "trainer_level",
                "total_xp",
                "gym_gold",
                "mini_collection",
                "butterfly_collector",
            ]
            + [field.name for field in STANDARD_MEDALS]
            + [field.name for field in BATTLE_HUB_STATS]
            + [field.name for field in UPDATE_FIELDS_TYPES]
        )


class TrainerForm(ModelForm):
    class Meta:
        model = Trainer
        fields = (
            "start_date",
            "faction",
            "statistics",
            "trainer_code",
            "country",
        )
