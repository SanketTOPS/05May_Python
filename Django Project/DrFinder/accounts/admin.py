from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, PatientProfile, DoctorProfile,
    OTPVerification, EmailVerificationToken,
    LoginHistory, UserSession
)


# ─── Inline Profiles ─────────────────────────────────────────────────────────

class PatientProfileInline(admin.StackedInline):
    model = PatientProfile
    can_delete = False
    verbose_name_plural = 'Patient Profile'
    fk_name = 'user'
    extra = 0


class DoctorProfileInline(admin.StackedInline):
    model = DoctorProfile
    can_delete = False
    verbose_name_plural = 'Doctor Profile'
    fk_name = 'user'
    extra = 0


# ─── Custom User Admin ────────────────────────────────────────────────────────

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'role', 'is_email_verified', 'is_active', 'failed_login_attempts', 'date_joined'
    )
    list_filter = ('role', 'is_email_verified', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('DrFinder Profile', {
            'fields': ('role', 'phone', 'profile_picture', 'is_email_verified')
        }),
        ('Account Security', {
            'fields': ('failed_login_attempts', 'account_locked_until'),
            'classes': ('collapse',),
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('DrFinder Info', {
            'fields': ('role', 'email', 'phone', 'first_name', 'last_name')
        }),
    )

    def get_inlines(self, request, obj=None):
        if obj:
            if obj.role == 'PATIENT':
                return [PatientProfileInline]
            elif obj.role == 'DOCTOR':
                return [DoctorProfileInline]
        return []

    actions = ['unlock_accounts', 'verify_emails']

    @admin.action(description='Unlock selected accounts')
    def unlock_accounts(self, request, queryset):
        queryset.update(failed_login_attempts=0, account_locked_until=None)
        self.message_user(request, f"{queryset.count()} account(s) unlocked.")

    @admin.action(description='Mark selected emails as verified')
    def verify_emails(self, request, queryset):
        queryset.update(is_email_verified=True)
        self.message_user(request, f"{queryset.count()} email(s) verified.")


# ─── Profile Admins ───────────────────────────────────────────────────────────

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'blood_group', 'date_of_birth')
    search_fields = ('user__username', 'user__email', 'user__first_name')
    list_filter = ('gender', 'blood_group')


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'hospital_name', 'experience_years', 'consultation_fee', 'status')
    list_filter = ('specialization', 'status')
    search_fields = ('user__username', 'user__email', 'hospital_name')
    list_editable = ('status',)
    actions = ['approve_doctors', 'suspend_doctors']

    @admin.action(description='Approve selected doctors')
    def approve_doctors(self, request, queryset):
        queryset.update(status='APPROVED')
        self.message_user(request, f"{queryset.count()} doctor(s) approved.")

    @admin.action(description='Suspend selected doctors')
    def suspend_doctors(self, request, queryset):
        queryset.update(status='SUSPENDED')
        self.message_user(request, f"{queryset.count()} doctor(s) suspended.")


# ─── OTP Admin ───────────────────────────────────────────────────────────────

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp_code', 'purpose', 'created_at', 'expires_at', 'is_used')
    list_filter = ('purpose', 'is_used')
    search_fields = ('user__username', 'user__email', 'otp_code')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


# ─── Email Verification Token Admin ──────────────────────────────────────────

@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('token', 'created_at')
    ordering = ('-created_at',)


# ─── Login History Admin ──────────────────────────────────────────────────────

@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('username_attempted', 'user', 'status', 'ip_address', 'timestamp')
    list_filter = ('status',)
    search_fields = ('username_attempted', 'ip_address', 'user__email')
    readonly_fields = ('timestamp', 'ip_address', 'user_agent')
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False  # Read-only log

    def has_change_permission(self, request, obj=None):
        return False  # Read-only log


# ─── User Session Admin ───────────────────────────────────────────────────────

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_key', 'ip_address', 'created_at', 'last_active')
    search_fields = ('user__username', 'ip_address', 'session_key')
    readonly_fields = ('created_at', 'last_active', 'session_key')
    ordering = ('-last_active',)
