from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.conf import settings
from django.urls import reverse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import User
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    PasswordChangeSerializer
)
from .utils import send_verification_email, send_password_reset_email


@extend_schema(
    summary="Register a new user",
    request=UserRegistrationSerializer,
    responses={201: UserProfileSerializer},
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Generate email verification token
        token = user.generate_email_verification_token()
        
        # Send verification email
        email_sent = send_verification_email(user, token)
        
        # Create auth token
        token_obj, created = Token.objects.get_or_create(user=user)
        
        response_data = {
            'user': UserProfileSerializer(user).data,
            'token': token_obj.key,
            'message': 'Registration successful. Please check your email for verification.',
            'email_sent': email_sent
        }
        
        if not email_sent:
            response_data['warning'] = 'Email could not be sent. Please check your email configuration.'
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Login user",
    request=UserLoginSerializer,
    responses={200: UserProfileSerializer},
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        
        # Create or get auth token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'token': token.key,
            'message': 'Login successful'
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Logout user",
    responses={200: dict},
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    try:
        # Delete the user's token
        request.user.auth_token.delete()
    except:
        pass
    
    logout(request)
    return Response({'message': 'Logout successful'})


@extend_schema(
    summary="Get user profile",
    responses={200: UserProfileSerializer},
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def profile(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)


@extend_schema(
    summary="Update user profile",
    request=UserProfileSerializer,
    responses={200: UserProfileSerializer},
)
@api_view(['PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_profile(request):
    serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Verify email address",
    parameters=[
        OpenApiParameter(
            name='token',
            type=OpenApiTypes.UUID,
            location=OpenApiParameter.PATH,
            description='Email verification token'
        )
    ],
    responses={200: dict},
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_email(request, token):
    try:
        user = User.objects.get(email_verification_token=token)
        user.is_email_verified = True
        user.email_verification_token = None
        user.save()
        
        return Response({
            'message': 'Email verified successfully'
        })
    except User.DoesNotExist:
        return Response(
            {'error': 'Invalid or expired verification token'},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    summary="Request password reset",
    request=PasswordResetRequestSerializer,
    responses={200: dict},
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def request_password_reset(request):
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Generate password reset token
        token = user.generate_password_reset_token()
        
        # Send password reset email
        email_sent = send_password_reset_email(user, token)
        
        response_data = {
            'message': 'Password reset link sent to your email',
            'email_sent': email_sent
        }
        
        if not email_sent:
            response_data['warning'] = 'Email could not be sent. Please check your email configuration.'
        
        return Response(response_data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Confirm password reset",
    request=PasswordResetConfirmSerializer,
    responses={200: dict},
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def confirm_password_reset(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            user = User.objects.get(password_reset_token=token)
            if user.is_password_reset_token_valid():
                user.set_password(new_password)
                user.clear_password_reset_token()
                
                return Response({
                    'message': 'Password reset successful'
                })
            else:
                return Response(
                    {'error': 'Invalid or expired reset token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid reset token'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Change password",
    request=PasswordChangeSerializer,
    responses={200: dict},
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Password changed successfully'
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
