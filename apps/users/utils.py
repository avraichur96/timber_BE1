import logging
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def send_email_with_fallback(subject, message, recipient_list, html_message=None, from_email=None):
    """
    Send email with fallback to console backend if SMTP fails
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email or settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Email sent successfully to {recipient_list}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_list}: {str(e)}")
        
        # Fallback to console backend for development
        if settings.DEBUG:
            print(f"\n{'='*50}")
            print(f"EMAIL FALLBACK - Could not send via SMTP")
            print(f"{'='*50}")
            print(f"To: {', '.join(recipient_list)}")
            print(f"Subject: {subject}")
            print(f"Message: {message}")
            if html_message:
                print(f"HTML: {html_message}")
            print(f"{'='*50}\n")
            return True
        
        return False


def send_verification_email(user, token):
    """
    Send email verification email
    """
    verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}/"
    
    subject = "Verify your email address - Timber"
    
    # HTML message template
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px;">
            <h2 style="color: #333; text-align: center;">Welcome to Timber!</h2>
            <p style="color: #666; line-height: 1.6;">
                Hi {user.first_name or user.username},<br><br>
                Thank you for registering with Timber. Please click the button below to verify your email address:
            </p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_url}" 
                   style="background-color: #007bff; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Verify Email Address
                </a>
            </div>
            <p style="color: #666; line-height: 1.6;">
                Or copy and paste this link into your browser:<br>
                <a href="{verification_url}" style="color: #007bff;">{verification_url}</a>
            </p>
            <p style="color: #999; font-size: 12px; margin-top: 30px;">
                This link will expire in 24 hours. If you didn't create an account with Timber, 
                please ignore this email.
            </p>
        </div>
    </body>
    </html>
    """
    
    # Plain text message
    message = f"""
    Welcome to Timber!
    
    Hi {user.first_name or user.username},
    
    Thank you for registering with Timber. Please visit the following link to verify your email address:
    
    {verification_url}
    
    This link will expire in 24 hours. If you didn't create an account with Timber, please ignore this email.
    """
    
    return send_email_with_fallback(
        subject=subject,
        message=message,
        recipient_list=[user.email],
        html_message=html_message
    )


def send_password_reset_email(user, token):
    """
    Send password reset email
    """
    reset_url = f"{settings.FRONTEND_URL}/reset-password/{token}/"
    
    subject = "Reset your password - Timber"
    
    # HTML message template
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px;">
            <h2 style="color: #333; text-align: center;">Password Reset Request</h2>
            <p style="color: #666; line-height: 1.6;">
                Hi {user.first_name or user.username},<br><br>
                We received a request to reset your password for your Timber account. 
                Click the button below to reset your password:
            </p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" 
                   style="background-color: #dc3545; color: white; padding: 12px 30px; 
                          text-decoration: none; border-radius: 5px; display: inline-block;">
                    Reset Password
                </a>
            </div>
            <p style="color: #666; line-height: 1.6;">
                Or copy and paste this link into your browser:<br>
                <a href="{reset_url}" style="color: #dc3545;">{reset_url}</a>
            </p>
            <p style="color: #999; font-size: 12px; margin-top: 30px;">
                This link will expire in 24 hours. If you didn't request a password reset, 
                please ignore this email or contact support if you have concerns.
            </p>
        </div>
    </body>
    </html>
    """
    
    # Plain text message
    message = f"""
    Password Reset Request
    
    Hi {user.first_name or user.username},
    
    We received a request to reset your password for your Timber account. 
    Please visit the following link to reset your password:
    
    {reset_url}
    
    This link will expire in 24 hours. If you didn't request a password reset, 
    please ignore this email or contact support if you have concerns.
    """
    
    return send_email_with_fallback(
        subject=subject,
        message=message,
        recipient_list=[user.email],
        html_message=html_message
    )
