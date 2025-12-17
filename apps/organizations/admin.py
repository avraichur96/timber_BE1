from django.contrib import admin
from .models import Organization, Subscription, OrganizationMember


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description', 'created_by__email')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('organization', 'plan_name', 'has_expired', 'started_at')
    list_filter = ('has_expired', 'plan_name', 'started_at')
    search_fields = ('organization__name', 'plan_name')
    ordering = ('-started_at',)
    readonly_fields = ('id', 'started_at', 'updated_at')


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'is_active', 'joined_at')
    list_filter = ('role', 'is_active', 'joined_at')
    search_fields = ('user__email', 'organization__name')
    ordering = ('organization', 'role', 'joined_at')
    readonly_fields = ('id', 'joined_at')
