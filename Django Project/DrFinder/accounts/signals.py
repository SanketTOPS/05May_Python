from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .utils import create_user_session, log_login_attempt

@receiver(user_logged_in)
def handle_user_login(sender, request, user, **kwargs):
    # Ensure active session is tracked
    create_user_session(user, request)
    # Log successful login
    log_login_attempt(request, user.username, user, 'SUCCESS')
