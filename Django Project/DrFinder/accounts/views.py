from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, View
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login, logout, update_session_auth_hash
from django.conf import settings
from django.utils import timezone

from .models import (
    User, PatientProfile, DoctorProfile,
    OTPVerification, EmailVerificationToken,
    LoginHistory, UserSession
)
from .forms import (
    PatientRegistrationForm,
    DoctorRegistrationForm,
    UserUpdateForm,
    PatientProfileUpdateForm,
    DoctorProfileUpdateForm,
    OTPVerifyForm,
    ForgotPasswordForm,
    ResetPasswordForm,
    ResendVerificationForm,
)
from .utils import (
    create_otp, send_otp_email,
    send_verification_email,
    send_password_reset_email,
    terminate_user_session,
    log_login_attempt,
)
from appointments.models import Appointment
from payments.models import Payment


# ─────────────────────────────────────────────────────────────────────────────
# Registration Views
# ─────────────────────────────────────────────────────────────────────────────

class PatientRegisterView(CreateView):
    model = User
    form_class = PatientRegistrationForm
    template_name = 'accounts/register_patient.html'
    success_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        # Send OTP for registration verification
        try:
            otp_obj = create_otp(user, purpose='REGISTRATION')
            send_otp_email(user, otp_obj, self.request)
        except Exception:
            pass  # Don't block registration if email fails

        # Send email verification link
        try:
            send_verification_email(user, self.request)
        except Exception:
            pass

        # Store user id in session for OTP step
        self.request.session['pending_otp_user_id'] = user.pk
        self.request.session['pending_otp_purpose'] = 'REGISTRATION'

        messages.success(
            self.request,
            f"Account created! A 6-digit OTP has been sent to {user.email}. Please verify to activate your account."
        )
        return redirect('verify_otp')


class DoctorRegisterView(CreateView):
    model = User
    form_class = DoctorRegistrationForm
    template_name = 'accounts/register_doctor.html'
    success_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        # Send OTP for registration verification
        try:
            otp_obj = create_otp(user, purpose='REGISTRATION')
            send_otp_email(user, otp_obj, self.request)
        except Exception:
            pass

        try:
            send_verification_email(user, self.request)
        except Exception:
            pass

        self.request.session['pending_otp_user_id'] = user.pk
        self.request.session['pending_otp_purpose'] = 'REGISTRATION'

        messages.success(
            self.request,
            f"Doctor account created! An OTP has been sent to {user.email}. Verify to continue."
        )
        return redirect('verify_otp')


# ─────────────────────────────────────────────────────────────────────────────
# OTP Verification View
# ─────────────────────────────────────────────────────────────────────────────

class OTPVerifyView(View):
    template_name = 'accounts/verify_otp.html'

    def _get_pending_user(self, request):
        user_id = request.session.get('pending_otp_user_id')
        purpose = request.session.get('pending_otp_purpose', 'REGISTRATION')
        if not user_id:
            return None, None
        try:
            return User.objects.get(pk=user_id), purpose
        except User.DoesNotExist:
            return None, None

    def get(self, request, *args, **kwargs):
        user, purpose = self._get_pending_user(request)
        if not user:
            messages.error(request, "Session expired. Please register or log in again.")
            return redirect('login')
        form = OTPVerifyForm()
        return render(request, self.template_name, {
            'form': form,
            'email_hint': f"{user.email[:3]}***@{user.email.split('@')[1]}",
            'purpose': purpose,
        })

    def post(self, request, *args, **kwargs):
        user, purpose = self._get_pending_user(request)
        if not user:
            messages.error(request, "Session expired. Please register or log in again.")
            return redirect('login')

        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data['otp_code']
            otp_obj = OTPVerification.objects.filter(
                user=user, purpose=purpose, is_used=False
            ).order_by('-created_at').first()

            if not otp_obj:
                messages.error(request, "No active OTP found. Please request a new one.")
            elif otp_obj.is_expired():
                messages.error(request, "OTP has expired. Please request a new one.")
            elif otp_obj.otp_code != entered_code:
                messages.error(request, "Incorrect OTP. Please try again.")
            else:
                # Mark OTP as used
                otp_obj.is_used = True
                otp_obj.save()

                if purpose == 'REGISTRATION':
                    user.is_active = True
                    user.save(update_fields=['is_active'])
                    login(request, user)
                    del request.session['pending_otp_user_id']
                    del request.session['pending_otp_purpose']
                    messages.success(request, "Email verified! Welcome to DrFinder.")
                    return redirect('dashboard')

                elif purpose == 'PASSWORD_RESET':
                    request.session['otp_verified_user_id'] = user.pk
                    del request.session['pending_otp_user_id']
                    del request.session['pending_otp_purpose']
                    return redirect('reset_password')

        return render(request, self.template_name, {
            'form': form,
            'email_hint': f"{user.email[:3]}***@{user.email.split('@')[1]}",
            'purpose': purpose,
        })


class ResendOTPView(LoginRequiredMixin, View):
    """Re-send OTP to the user's email from session."""

    def post(self, request, *args, **kwargs):
        user_id = request.session.get('pending_otp_user_id')
        purpose = request.session.get('pending_otp_purpose', 'REGISTRATION')
        if not user_id:
            messages.error(request, "No pending verification found.")
            return redirect('login')
        try:
            user = User.objects.get(pk=user_id)
            otp_obj = create_otp(user, purpose=purpose)
            send_otp_email(user, otp_obj, request)
            messages.success(request, "A new OTP has been sent to your email.")
        except Exception as e:
            messages.error(request, "Failed to resend OTP. Please try again later.")
        return redirect('verify_otp')


# ─────────────────────────────────────────────────────────────────────────────
# Email Verification View
# ─────────────────────────────────────────────────────────────────────────────

class EmailVerifyView(View):
    template_name = 'accounts/verify_email.html'

    def get(self, request, token, *args, **kwargs):
        try:
            token_obj = EmailVerificationToken.objects.get(token=token)
        except EmailVerificationToken.DoesNotExist:
            return render(request, self.template_name, {'status': 'invalid'})

        if not token_obj.is_valid():
            return render(request, self.template_name, {'status': 'expired'})

        user = token_obj.user
        user.is_email_verified = True
        user.save(update_fields=['is_email_verified'])
        token_obj.is_used = True
        token_obj.save(update_fields=['is_used'])

        return render(request, self.template_name, {'status': 'success', 'user': user})


class ResendVerificationEmailView(View):
    template_name = 'accounts/resend_verification.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_email_verified:
            messages.info(request, "Your email is already verified.")
            return redirect('dashboard')
        form = ResendVerificationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ResendVerificationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                if user.is_email_verified:
                    messages.info(request, "This email is already verified. Please log in.")
                else:
                    send_verification_email(user, request)
                    messages.success(request, f"Verification email sent to {email}. Check your inbox.")
            except User.DoesNotExist:
                # Security: don't reveal whether email exists
                messages.success(request, f"If {email} is registered, a verification link has been sent.")
        return render(request, self.template_name, {'form': form})


# ─────────────────────────────────────────────────────────────────────────────
# Login / Logout Views (Enhanced)
# ─────────────────────────────────────────────────────────────────────────────

class UserLoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        from django.contrib.auth.forms import AuthenticationForm
        form = AuthenticationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        from django.contrib.auth import authenticate
        from django.contrib.auth.forms import AuthenticationForm

        form = AuthenticationForm(request, data=request.POST)
        username = request.POST.get('username', '').strip()
        max_attempts = getattr(settings, 'MAX_FAILED_LOGIN_ATTEMPTS', 5)
        lockout_minutes = getattr(settings, 'ACCOUNT_LOCKOUT_MINUTES', 15)

        # Check if user exists and if account is locked
        try:
            user_obj = User.objects.get(username=username)
            if user_obj.is_account_locked():
                log_login_attempt(request, username, user_obj, 'LOCKED')
                unlock_time = user_obj.account_locked_until
                messages.error(
                    request,
                    f"Account is temporarily locked due to too many failed attempts. "
                    f"Try again after {unlock_time.strftime('%H:%M')} UTC."
                )
                return render(request, self.template_name, {'form': form})
        except User.DoesNotExist:
            user_obj = None

        if form.is_valid():
            user = form.get_user()
            user.reset_failed_attempts()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next') or reverse('dashboard')
            return redirect(next_url)
        else:
            # Failed login
            if user_obj:
                user_obj.increment_failed_attempts()
                if user_obj.failed_login_attempts >= max_attempts:
                    user_obj.lock_account(lockout_minutes)
                    log_login_attempt(request, username, user_obj, 'LOCKED')
                    messages.error(
                        request,
                        f"Too many failed attempts. Your account has been locked for {lockout_minutes} minutes."
                    )
                    return render(request, self.template_name, {'form': form})
                remaining = max_attempts - user_obj.failed_login_attempts
                log_login_attempt(request, username, user_obj, 'FAILED')
                messages.error(
                    request,
                    f"Invalid username or password. {remaining} attempt(s) remaining before lockout."
                )
            else:
                log_login_attempt(request, username, None, 'FAILED')
                messages.error(request, "Invalid username or password.")

        return render(request, self.template_name, {'form': form})


class UserLogoutView(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            session_key = request.session.session_key
            if session_key:
                UserSession.objects.filter(session_key=session_key).delete()
        logout(request)
        messages.success(request, "You have been securely logged out.")
        return redirect('home')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


# ─────────────────────────────────────────────────────────────────────────────
# Forgot / Reset Password Views
# ─────────────────────────────────────────────────────────────────────────────

class ForgotPasswordView(View):
    template_name = 'accounts/forgot_password.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = ForgotPasswordForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                try:
                    send_password_reset_email(user, request)
                except Exception:
                    pass
                # Store user id in session for OTP step
                request.session['pending_otp_user_id'] = user.pk
                request.session['pending_otp_purpose'] = 'PASSWORD_RESET'
            except User.DoesNotExist:
                pass  # Don't reveal if email exists

            # Always show the same message for security
            messages.success(
                request,
                f"If an account with {email} exists, a password reset OTP has been sent."
            )
            return redirect('verify_otp')

        return render(request, self.template_name, {'form': form})


class ResetPasswordView(View):
    template_name = 'accounts/reset_password.html'

    def _get_verified_user(self, request):
        user_id = request.session.get('otp_verified_user_id')
        if not user_id:
            return None
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        user = self._get_verified_user(request)
        if not user:
            messages.error(request, "Password reset session expired. Please start again.")
            return redirect('forgot_password')
        form = ResetPasswordForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        user = self._get_verified_user(request)
        if not user:
            messages.error(request, "Password reset session expired.")
            return redirect('forgot_password')

        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password'])
            user.reset_failed_attempts()
            user.save()
            del request.session['otp_verified_user_id']
            messages.success(request, "Password reset successful! Please log in with your new password.")
            return redirect('login')

        return render(request, self.template_name, {'form': form})


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard Redirect View
# ─────────────────────────────────────────────────────────────────────────────

class DashboardRedirectView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.role == 'ADMIN' or request.user.is_superuser:
            return redirect('admin_dashboard')
        elif request.user.role == 'DOCTOR':
            return redirect('doctor_dashboard')
        else:
            return redirect('patient_dashboard')


# ─────────────────────────────────────────────────────────────────────────────
# Profile Update View
# ─────────────────────────────────────────────────────────────────────────────

class ProfileUpdateView(LoginRequiredMixin, View):
    template_name = 'accounts/profile.html'

    def get(self, request, *args, **kwargs):
        user_form = UserUpdateForm(instance=request.user)

        if request.user.role == 'PATIENT':
            profile = get_object_or_404(PatientProfile, user=request.user)
            profile_form = PatientProfileUpdateForm(instance=profile)
        elif request.user.role == 'DOCTOR':
            profile = get_object_or_404(DoctorProfile, user=request.user)
            profile_form = DoctorProfileUpdateForm(instance=profile)
        else:
            profile_form = None

        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form
        })

    def post(self, request, *args, **kwargs):
        user_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)

        if request.user.role == 'PATIENT':
            profile = get_object_or_404(PatientProfile, user=request.user)
            profile_form = PatientProfileUpdateForm(request.POST, instance=profile)
        elif request.user.role == 'DOCTOR':
            profile = get_object_or_404(DoctorProfile, user=request.user)
            profile_form = DoctorProfileUpdateForm(request.POST, instance=profile)
        else:
            profile_form = None

        if user_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')

        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form
        })


# ─────────────────────────────────────────────────────────────────────────────
# Admin Doctor Verification
# ─────────────────────────────────────────────────────────────────────────────

class AdminVerificationView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.role == 'ADMIN' or self.request.user.is_superuser

    def post(self, request, doctor_id, action, *args, **kwargs):
        doctor = get_object_or_404(DoctorProfile, id=doctor_id)
        if action == 'approve':
            doctor.status = 'APPROVED'
            messages.success(request, f"Dr. {doctor.user.get_full_name()} has been approved.")
        elif action == 'suspend':
            doctor.status = 'SUSPENDED'
            messages.warning(request, f"Dr. {doctor.user.get_full_name()} has been suspended.")
        doctor.save()
        return redirect('admin_dashboard')


# ─────────────────────────────────────────────────────────────────────────────
# Login History View
# ─────────────────────────────────────────────────────────────────────────────

class LoginHistoryView(LoginRequiredMixin, View):
    template_name = 'accounts/login_history.html'

    def get(self, request, *args, **kwargs):
        history = LoginHistory.objects.filter(user=request.user).order_by('-timestamp')[:50]
        return render(request, self.template_name, {'history': history})


# ─────────────────────────────────────────────────────────────────────────────
# Active Sessions View
# ─────────────────────────────────────────────────────────────────────────────

class ActiveSessionsView(LoginRequiredMixin, View):
    template_name = 'accounts/active_sessions.html'

    def get(self, request, *args, **kwargs):
        sessions = UserSession.objects.filter(user=request.user)
        current_key = request.session.session_key
        return render(request, self.template_name, {
            'sessions': sessions,
            'current_session_key': current_key,
        })


class TerminateSessionView(LoginRequiredMixin, View):
    def post(self, request, session_key, *args, **kwargs):
        # Only allow terminating own sessions
        session = get_object_or_404(UserSession, session_key=session_key, user=request.user)
        is_current = session_key == request.session.session_key
        terminate_user_session(session_key)

        if is_current:
            messages.success(request, "Current session terminated. You have been logged out.")
            return redirect('login')

        messages.success(request, "Session has been terminated successfully.")
        return redirect('active_sessions')
