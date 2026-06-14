from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_verification_email(email, token, username='User'):
    """
    Email verification link jo'natish
    """
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Email Verification</h2>
            <p>Hi {username},</p>
            <p>Please verify your email by clicking the link below:</p>
            <a href="{verification_url}" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                Verify Email
            </a>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't create an account, please ignore this email.</p>
        </body>
    </html>
    """
    
    send_mail(
        subject='Verify Your Email - Gaming Challenge Platform',
        message=strip_tags(html_message),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        html_message=html_message,
        fail_silently=False,
    )


def send_welcome_email(email, username, role):
    """
    Welcome email
    """
    if role == 'CHALLENGER':
        role_text = "Challenge Creator"
    else:
        role_text = "Streamer"
    
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Welcome to Gaming Challenge Platform!</h2>
            <p>Hi {username},</p>
            <p>Your account has been created as a {role_text}.</p>
            <p>Start creating challenges and earning points!</p>
        </body>
    </html>
    """
    
    send_mail(
        subject='Welcome to Gaming Challenge Platform',
        message=strip_tags(html_message),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        html_message=html_message,
        fail_silently=False,
    )


def send_payment_verification_email(email, username, amount, status):
    """
    Payment verification email
    """
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Payment Status</h2>
            <p>Hi {username},</p>
            <p>Your payment of {amount} UZS has been {status.lower()}.</p>
            <p>If you have any questions, please contact support.</p>
        </body>
    </html>
    """
    
    send_mail(
        subject=f'Payment {status}',
        message=strip_tags(html_message),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        html_message=html_message,
        fail_silently=False,
    )


def send_ban_notification_email(email, username, ban_until):
    """
    Account ban notification
    """
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Account Suspended</h2>
            <p>Hi {username},</p>
            <p>Your account has been suspended due to violations.</p>
            <p>Your account will be restored on: {ban_until.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>If you believe this is a mistake, please contact support.</p>
        </body>
    </html>
    """
    
    send_mail(
        subject='Account Suspended',
        message=strip_tags(html_message),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        html_message=html_message,
        fail_silently=False,
    )
