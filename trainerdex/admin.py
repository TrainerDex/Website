# from django.contrib import admin, messages
# from django.utils.translation import gettext_lazy as _, ngettext
#
# from community.models import Community, CommunityMembershipDiscord
# from core.models import Nickname
# from trainerdex.models import Trainer, Update
#
# def sync_members(modeladmin, request, queryset):
#     for x in queryset:
#         for y in x.memberships_discord.filter(communitymembershipdiscord__sync_members=True):
#             results = y.sync_members()
#             for message in results['success']:
#                 messages.success(request, message)
#             for message in results['warning']:
#                 messages.warning(request, message)
#
# sync_members.short_description = _('Sync Members for all eligible Discords')
#
#
# @admin.register(Community)
# class CommunityAdmin(admin.ModelAdmin):
#
#     search_fields = ('name','short_description', 'handle')
#     autocomplete_fields = ['memberships_personal', 'memberships_discord']
#     actions = [sync_members]
#
#
# @admin.register(CommunityMembershipDiscord)
# class CommunityMembershipDiscordAdmin(admin.ModelAdmin):
#
#     autocomplete_fields = ['community', 'discord']
#
#
# @admin.register(Update)
# class UpdateAdmin(admin.ModelAdmin):
#
#     autocomplete_fields = ['trainer']
#     list_display = ('trainer', 'total_xp', 'update_time', 'submission_date', 'has_modified_extra_fields')
#     search_fields = ('trainer__nickname__nickname', 'trainer__owner__username')
#     ordering = ('-update_time',)
#     date_hierarchy = 'update_time'
#
#
# @admin.register(Nickname)
# class NicknameAdmin(admin.ModelAdmin):
#
#     search_fields = (
#         'nickname',
#         'trainer__owner__first_name',
#         'trainer__owner__username',
#         )
#     list_display = (
#         'nickname',
#         'trainer',
#         'active',
#         )
#     list_filter = ('active',)
#     list_display_links = ('nickname',)
#     autocomplete_fields = ['trainer']
#
#
# @admin.register(Trainer)
# class TrainerAdmin(admin.ModelAdmin):
#
#     autocomplete_fields = [
#         'owner',
#         'leaderboard_country',
#         'leaderboard_region',
#         ]
#     list_display = (
#         'nickname',
#         'faction',
#         'currently_cheats',
#         'is_on_leaderboard',
#         'is_verified',
#         'awaiting_verification',
#         )
#     list_filter = (
#         'faction',
#         'last_cheated',
#         'statistics',
#         'verified',
#         )
#     search_fields = (
#         'nickname__nickname',
#         'owner__first_name',
#         'owner__username',
#         )
#     ordering = (
#         'nickname__nickname',
#         'pk'
#         )
#
#     fieldsets = (
#         (None, {
#             'fields': ('owner', 'faction', 'start_date', 'daily_goal', 'total_goal','trainer_code')
#         }),
#         (_('Reports'), {
#             'fields': ('last_cheated', 'verified', 'verification')
#         }),
#         (_('Leaderboard'), {
#             'fields': ('leaderboard_country', 'leaderboard_region', 'statistics')
#         }),
#     )
