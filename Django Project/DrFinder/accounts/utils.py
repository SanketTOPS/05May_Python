"""
accounts/utils.py
Utility helpers for the authentication module:
  - OTP generation & email sending
  - Email verification token creation & sending
  - Password reset email
  - IP / User-Agent extraction
  - Session tracking helpers
"""

import random
import string
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.urls import reverse


# ─────────────────────────────────────────────────────────────────────────────
# IP & Device Helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_client_ip(request):
    """Extract the real client IP, honouring X-Forwarded-For if present."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Return the raw User-Agent string."""
    return request.META.get('HTTP_USER_AGENT', '')


# ─────────────────────────────────────────────────────────────────────────────
# OTP Helpers
# ─────────────────────────────────────────────────────────────────────────────

def generate_otp(length=6):
    """Generate a secure numeric OTP of the given length."""
    return ''.join(random.choices(string.digits, k=length))


def create_otp(user, purpose='REGISTRATION'):
    """
    Invalidate old unused OTPs for this user/purpose,
    then create and return a fresh OTPVerification object.
    """
    from .models import OTPVerification

    expiry_minutes = getattr(settings, 'OTP_EXPIRY_MINUTES', 10)

    # Expire old OTPs
    OTPVerification.objects.filter(user=user, purpose=purpose, is_used=False).update(is_used=True)

    otp = OTPVerification.objects.create(
        user=user,
        otp_code=generate_otp(),
        purpose=purpose,
        expires_at=timezone.now() + timezone.timedelta(minutes=expiry_minutes),
    )
    return otp


def send_otp_email(user, otp_obj, request=None):
    """Send OTP code to user email."""
    subject = f"DrFinder — Your OTP Code: {otp_obj.otp_code}"
    body = render_to_string('accounts/email/otp_email.html', {
        'user': user,
        'otp_code': otp_obj.otp_code,
        'expiry_minutes': getattr(settings, 'OTP_EXPIRY_MINUTES', 10),
        'purpose': otp_obj.get_purpose_display(),
    })
    send_mail(
        subject=subject,
        message=f"Your OTP is: {otp_obj.otp_code}. Valid for {getattr(settings, 'OTP_EXPIRY_MINUTES', 10)} minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=body,
        fail_silently=False,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Email Verification Helpers
# ─────────────────────────────────────────────────────────────────────────────

def create_email_verification_token(user):
    """Create and return a new EmailVerificationToken for the user (24h validity)."""
    from .models import EmailVerificationToken

    # Expire old tokens
    EmailVerificationToken.objects.filter(user=user, is_used=False).update(is_used=True)

    token = EmailVerificationToken.objects.create(
        user=user,
        expires_at=timezone.now() + timezone.timedelta(hours=24),
    )
    return token


def send_verification_email(user, request):
    """Send email-verification link to the user."""
    token_obj = create_email_verification_token(user)
    verify_url = request.build_absolute_uri(
        reverse('verify_email', kwargs={'token': str(token_obj.token)})
    )
    subject = "DrFinder — Verify Your Email Address"
    body = render_to_string('accounts/email/verification_email.html', {
        'user': user,
        'verify_url': verify_url,
    })
    send_mail(
        subject=subject,
        message=f"Please verify your email by visiting: {verify_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=body,
        fail_silently=False,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Password Reset Helpers
# ─────────────────────────────────────────────────────────────────────────────

def send_password_reset_email(user, request):
    """Generate a password-reset OTP and email it to the user."""
    otp_obj = create_otp(user, purpose='PASSWORD_RESET')
    subject = "DrFinder — Password Reset OTP"
    body = render_to_string('accounts/email/password_reset_email.html', {
        'user': user,
        'otp_code': otp_obj.otp_code,
        'expiry_minutes': getattr(settings, 'OTP_EXPIRY_MINUTES', 10),
    })
    send_mail(
        subject=subject,
        message=f"Your password reset OTP is: {otp_obj.otp_code}. Valid for {getattr(settings, 'OTP_EXPIRY_MINUTES', 10)} minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=body,
        fail_silently=False,
    )
    return otp_obj


# ─────────────────────────────────────────────────────────────────────────────
# Session Tracking Helpers
# ─────────────────────────────────────────────────────────────────────────────

def create_user_session(user, request):
    """Create or update a UserSession record for this Django session."""
    from .models import UserSession
    from django.contrib.sessions.backends.db import SessionStore

    session_key = request.session.session_key
    if not session_key:
        request.session.save()
        session_key = request.session.session_key

    UserSession.objects.update_or_create(
        session_key=session_key,
        defaults={
            'user': user,
            'ip_address': get_client_ip(request),
            'user_agent': get_user_agent(request),
        }
    )


def terminate_user_session(session_key):
    """Delete the Django session and remove the UserSession record."""
    from .models import UserSession
    from django.contrib.sessions.models import Session

    UserSession.objects.filter(session_key=session_key).delete()
    try:
        Session.objects.get(session_key=session_key).delete()
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Login History Helper
# ─────────────────────────────────────────────────────────────────────────────

def log_login_attempt(request, username, user=None, status='SUCCESS'):
    """Record a login attempt in LoginHistory."""
    from .models import LoginHistory

    LoginHistory.objects.create(
        user=user,
        username_attempted=username,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        status=status,
    )
