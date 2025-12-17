from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization, Subscription

User = get_user_model()


@extend_schema(
    summary="API Health Check",
    description="Returns basic API information and health status",
    responses={200: dict},
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """
    Dummy listing endpoint that provides basic API information
    and serves as a health check endpoint.
    """
    data = {
        'status': 'healthy',
        'message': 'Timber BE API is running',
        'version': '1.0.0',
        'endpoints': {
            'auth': {
                'register': '/api/v1/auth/register/',
                'login': '/api/v1/auth/login/',
                'logout': '/api/v1/auth/logout/',
                'profile': '/api/v1/auth/profile/',
                'verify_email': '/api/v1/auth/verify-email/<token>/',
                'password_reset': '/api/v1/auth/password-reset/request/',
                'password_change': '/api/v1/auth/password/change/',
            },
            'organizations': {
                'list': '/api/v1/organizations/',
                'create': '/api/v1/organizations/create/',
                'detail': '/api/v1/organizations/<id>/',
                'subscriptions': '/api/v1/organizations/subscriptions/',
            },
            'docs': {
                'swagger': '/api/docs/',
                'redoc': '/api/redoc/',
                'schema': '/api/schema/',
            }
        },
        'statistics': {
            'total_users': User.objects.count(),
            'total_organizations': Organization.objects.count(),
            'total_subscriptions': Subscription.objects.count(),
        }
    }
    
    return Response(data, status=status.HTTP_200_OK)


@extend_schema(
    summary="API Statistics",
    description="Returns detailed statistics about the API usage and data",
    responses={200: dict},
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_statistics(request):
    """
    Returns detailed statistics about the API.
    Requires authentication.
    """
    user = request.user
    
    # User-specific stats
    user_organizations = Organization.objects.filter(
        members__user=user, 
        members__is_active=True
    ).count()
    
    user_subscriptions = Subscription.objects.filter(
        organization__members__user=user,
        organization__members__is_active=True
    ).count()
    
    data = {
        'user_info': {
            'id': user.id,
            'email': user.email,
            'is_email_verified': user.is_email_verified,
            'created_at': user.created_at,
        },
        'user_statistics': {
            'organizations_count': user_organizations,
            'subscriptions_count': user_subscriptions,
        },
        'global_statistics': {
            'total_users': User.objects.count(),
            'total_organizations': Organization.objects.count(),
            'total_subscriptions': Subscription.objects.count(),
            'active_subscriptions': Subscription.objects.filter(has_expired=False).count(),
            'expired_subscriptions': Subscription.objects.filter(has_expired=True).count(),
        }
    }
    
    return Response(data, status=status.HTTP_200_OK)
