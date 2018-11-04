# -*- coding: utf-8 -*-
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _
from trainer.models import Update, Trainer
from trainer.shortcuts import UPDATE_FIELDS_BADGES, UPDATE_FIELDS_TYPES, UPDATE_SORTABLE_FIELDS

class UpdateForm(ModelForm):
    
    class Meta:
        model = Update
        fields = (
            'trainer',
            'update_time',
            'total_xp',
            'data_source',
            'pokedex_caught',
            'pokedex_seen',
            'gymbadges_total',
            'gymbadges_gold',
            'pokemon_info_stardust',
            'double_check_confirmation',
        ) + UPDATE_FIELDS_BADGES + UPDATE_FIELDS_TYPES
    
    field_order = (
        'double_check_confirmation',
        ) + UPDATE_SORTABLE_FIELDS
    

class RegistrationFormTrainer(ModelForm):
    
    class Meta:
        model = Trainer
        fields = (
            'username',
            'start_date',
            'faction',
            'statistics',
            'daily_goal',
            'total_goal',
            'verification',
        )
    

class RegistrationFormUpdate(UpdateForm):
    
    class Meta:
        model = Update
        fields = (
            'trainer',
            'update_time',
            'total_xp',
            'data_source',
            'pokedex_caught',
            'pokedex_seen',
            'gymbadges_total',
            'gymbadges_gold',
            'pokemon_info_stardust',
            'screenshot',
            'double_check_confirmation',
        ) + UPDATE_FIELDS_BADGES + UPDATE_FIELDS_TYPES
    
    field_order = (
        'image_proof',
        'double_check_confirmation',
        ) + UPDATE_SORTABLE_FIELDS
