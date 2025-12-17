from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404

from .models import Organization, Subscription, OrganizationMember
from .serializers import OrganizationSerializer, SubscriptionSerializer, OrganizationMemberSerializer


@extend_schema(
    summary="List organizations",
    responses={200: OrganizationSerializer(many=True)},
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def organization_list(request):
    organizations = Organization.objects.filter(
        members__user=request.user, 
        members__is_active=True
    ).distinct()
    serializer = OrganizationSerializer(organizations, many=True)
    return Response(serializer.data)


@extend_schema(
    summary="Create organization",
    request=OrganizationSerializer,
    responses={201: OrganizationSerializer},
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def organization_create(request):
    serializer = OrganizationSerializer(data=request.data)
    if serializer.is_valid():
        organization = serializer.save(created_by=request.user)
        
        # Add creator as owner
        OrganizationMember.objects.create(
            organization=organization,
            user=request.user,
            role='owner'
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Get organization details",
    responses={200: OrganizationSerializer},
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def organization_detail(request, pk):
    organization = get_object_or_404(Organization, pk=pk, members__user=request.user)
    serializer = OrganizationSerializer(organization)
    return Response(serializer.data)


@extend_schema(
    summary="Update organization",
    request=OrganizationSerializer,
    responses={200: OrganizationSerializer},
)
@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def organization_update(request, pk):
    organization = get_object_or_404(
        Organization, 
        pk=pk, 
        members__user=request.user,
        members__role__in=['owner', 'admin']
    )
    serializer = OrganizationSerializer(organization, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="List subscriptions",
    responses={200: SubscriptionSerializer(many=True)},
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def subscription_list(request):
    subscriptions = Subscription.objects.filter(
        organization__members__user=request.user,
        organization__members__is_active=True
    ).select_related('organization')
    serializer = SubscriptionSerializer(subscriptions, many=True)
    return Response(serializer.data)


@extend_schema(
    summary="Create subscription",
    request=SubscriptionSerializer,
    responses={201: SubscriptionSerializer},
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def subscription_create(request):
    serializer = SubscriptionSerializer(data=request.data)
    if serializer.is_valid():
        # Check if user has permission to create subscription for this organization
        organization = serializer.validated_data['organization']
        if not OrganizationMember.objects.filter(
            organization=organization,
            user=request.user,
            role__in=['owner', 'admin'],
            is_active=True
        ).exists():
            return Response(
                {'error': 'You do not have permission to create subscriptions for this organization'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        subscription = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="List organization members",
    responses={200: OrganizationMemberSerializer(many=True)},
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def organization_members_list(request, pk):
    organization = get_object_or_404(Organization, pk=pk, members__user=request.user)
    members = OrganizationMember.objects.filter(organization=organization, is_active=True)
    serializer = OrganizationMemberSerializer(members, many=True)
    return Response(serializer.data)
