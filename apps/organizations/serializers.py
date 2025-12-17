from rest_framework import serializers
from .models import Organization, Subscription, OrganizationMember


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "description",
            "created_by",
            "created_at",
            "updated_at",
            "is_active",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at")


class SubscriptionSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )

    class Meta:
        model = Subscription
        fields = (
            "id",
            "organization",
            "organization_name",
            "plan_name",
            "has_expired",
            "started_at",
            "updated_at",
        )
        read_only_fields = ("id", "started_at", "updated_at")


class OrganizationMemberSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)
    user_name = serializers.CharField(
        source="user.get_full_name", read_only=True
    )
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )

    class Meta:
        model = OrganizationMember
        fields = (
            "id",
            "organization",
            "organization_name",
            "user",
            "user_email",
            "user_name",
            "role",
            "joined_at",
            "is_active",
        )
        read_only_fields = ("id", "joined_at")
