from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from trainerdex.models import Trainer, Update, Evidence, EvidenceImage


@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):

    autocomplete_fields = ['trainer']
    list_display = ('trainer', 'total_xp', 'update_time', 'submission_date', 'has_modified_extra_fields')
    search_fields = ('trainer__user__nickname__nickname', 'trainer__user__username')
    ordering = ('-update_time',)
    date_hierarchy = 'update_time'


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):

    autocomplete_fields = [
        'user',
        ]
    list_display = (
        'nickname',
        'faction',
        'banned',
        'leaderboard_eligibility',
        'profile_complete',
        'awaiting_verification',
        )
    list_filter = (
        'faction',
        'banned',
        'user__gdpr',
        'verified',
        )
    search_fields = (
        'user__nickname__nickname',
        'user__first_name',
        'user__username',
        )

    fieldsets = (
        (None, {
            'fields': ('user', 'faction', 'start_date', 'trainer_code')
        }),
        (_('Reports'), {
            'fields': ('banned', 'verified',)
        }),
        (_('Leaderboard'), {
            'fields': ('country',)
        }),
    )
    
    def queryset(self, request):
        qs = super(TrainerAdmin, self).queryset(request)
        qs = qs.order_by('user__username', 'pk').distinct('pk')
        return qs


class EvidenceImageInline(admin.TabularInline):
    model = EvidenceImage
    min_num = 0


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    
    list_display = [
        'trainer',
        'content_field',
    ]
    list_filter = [
        'content_type',
        'content_field',
    ]
    inlines = [
        EvidenceImageInline,
    ]
    
