from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from trainerdex.models import DataSource, Trainer, TrainerCode, Update, Evidence, EvidenceImage, Target, PresetTarget, PresetTargetGroup

admin.site.register(PresetTargetGroup)
admin.site.register(DataSource)


@admin.register(PresetTarget)
class PresetTargetAdmin(admin.ModelAdmin):

    list_display = ('name', 'stat', 'target')
    list_filter = ('stat',)
    search_fields = ('name', 'stat')


@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):

    autocomplete_fields = ['trainer']
    list_display = ('trainer', 'total_xp', 'update_time', 'submission_date', 'has_modified_extra_fields')
    search_fields = ('trainer__user__nickname__nickname', 'trainer__user__username')
    ordering = ('-update_time',)
    date_hierarchy = 'update_time'


class TrainerCodeInline(admin.TabularInline):
    model = TrainerCode
    min_num = 1
    max_num = 1
    can_delete = False
    verbose_name_plural = TrainerCode._meta.verbose_name


class TargetInline(admin.TabularInline):
    model = Target
    min_num = 0


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):

    autocomplete_fields = [
        'user',
        ]
    list_display = [
        'nickname',
        'faction',
        'banned',
        'leaderboard_eligibility',
        'awaiting_verification',
        ]
    list_filter = [
        'faction',
        'banned',
        'user__gdpr',
        'verified',
        ]
    search_fields = [
        'user__nickname__nickname',
        'user__first_name',
        'user__username',
        ]
    readonly_fields = [
        'id',
        ]
    fieldsets = [
        (None, {
            'fields': (
                'user',
                'id',
                'faction',
                'start_date',
                'country',
                ),
        }),
        (_('Reports'), {
            'fields': (
                'banned',
                'verified',
                ),
        }),
    ]
    inlines = [
        TargetInline,
        TrainerCodeInline,
    ]
    
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
        'approval',
        'content_type',
        'content_field',
    ]
    list_filter = [
        'approval',
        'content_type',
        'content_field',
    ]
    readonly_fields = [
        'content_object',
    ]
    fieldsets = [
        (_('Object'), {
            'fields': [
                'content_type',
                'object_pk',
                'content_object',
                'content_field',
            ],
        }),
        (None, {
            'fields': [
                'approval',
            ],
        }),
    ]
    inlines = [
        EvidenceImageInline,
    ]
