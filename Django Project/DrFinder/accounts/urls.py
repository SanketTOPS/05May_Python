from django.urls import path
from .views import (
    PatientRegisterView,
    DoctorRegisterView,
    UserLoginView,
    UserLogoutView,
    DashboardRedirectView,
    ProfileUpdateView,
    AdminVerificationView,
    # OTP & Email Verification
    OTPVerifyView,
    ResendOTPView,
    EmailVerifyView,
    ResendVerificationEmailView,
    # Forgot / Reset Password
    ForgotPasswordView,
    ResetPasswordView,
    # Login History & Sessions
    LoginHistoryView,
    ActiveSessionsView,
    TerminateSessionView,
)

urlpatterns = [
    # ── Registration ──────────────────────────────────────────────────────────
    path('register/patient/',  PatientRegisterView.as_view(),  name='register_patient'),
    path('register/doctor/',   DoctorRegisterView.as_view(),   name='register_doctor'),

    # ── Login / Logout ────────────────────────────────────────────────────────
    path('login/',   UserLoginView.as_view(),  name='login'),
    path('logout/',  UserLogoutView.as_view(), name='logout'),

    # ── Dashboard Redirect ────────────────────────────────────────────────────
    path('dashboard/', DashboardRedirectView.as_view(), name='dashboard'),

    # ── Profile ───────────────────────────────────────────────────────────────
    path('profile/', ProfileUpdateView.as_view(), name='profile'),

    # ── OTP Verification ──────────────────────────────────────────────────────
    path('verify-otp/',  OTPVerifyView.as_view(),  name='verify_otp'),
    path('resend-otp/',  ResendOTPView.as_view(),  name='resend_otp'),

    # ── Email Verification ────────────────────────────────────────────────────
    path('verify-email/<uuid:token>/', EmailVerifyView.as_view(), name='verify_email'),
    path('resend-verification/',       ResendVerificationEmailView.as_view(), name='resend_verification'),

    # ── Forgot / Reset Password ───────────────────────────────────────────────
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/',  ResetPasswordView.as_view(),  name='reset_password'),

    # ── Login History ─────────────────────────────────────────────────────────
    path('login-history/', LoginHistoryView.as_view(), name='login_history'),

    # ── Session Management ────────────────────────────────────────────────────
    path('sessions/',                          ActiveSessionsView.as_view(),  name='active_sessions'),
    path('sessions/<str:session_key>/terminate/', TerminateSessionView.as_view(), name='terminate_session'),

    # ── Admin Controls ────────────────────────────────────────────────────────
    path('admin/doctor/<int:doctor_id>/<str:action>/', AdminVerificationView.as_view(), name='admin_doctor_verify'),
]
