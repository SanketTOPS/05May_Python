from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid


class User(AbstractUser):
    ROLE_CHOICES = (
        ('PATIENT', 'Patient'),
        ('DOCTOR', 'Doctor'),
        ('ADMIN', 'Admin'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='PATIENT')
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # Email verification
    is_email_verified = models.BooleanField(default=False)

    # Account lockout
    failed_login_attempts = models.PositiveSmallIntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role.capitalize()})"

    def is_account_locked(self):
        """Returns True if the account is currently locked."""
        if self.account_locked_until and timezone.now() < self.account_locked_until:
            return True
        return False

    def lock_account(self, minutes=15):
        """Lock the account for the specified number of minutes."""
        self.account_locked_until = timezone.now() + timezone.timedelta(minutes=minutes)
        self.save(update_fields=['account_locked_until'])

    def reset_failed_attempts(self):
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.save(update_fields=['failed_login_attempts', 'account_locked_until'])

    def increment_failed_attempts(self):
        self.failed_login_attempts += 1
        self.save(update_fields=['failed_login_attempts'])


class PatientProfile(models.Model):
    GENDER_CHOICES = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Patient: {self.user.get_full_name() or self.user.username}"


class DoctorProfile(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Verification'),
        ('APPROVED', 'Approved'),
        ('SUSPENDED', 'Suspended'),
    )

    SPECIALIZATION_CHOICES = (
        ('GENERAL', 'General Physician'),
        ('CARDIOLOGY', 'Cardiologist'),
        ('DERMATOLOGY', 'Dermatologist'),
        ('PEDIATRICS', 'Pediatrician'),
        ('ORTHOPEDICS', 'Orthopedic Surgeon'),
        ('NEUROLOGY', 'Neurologist'),
        ('GYNECOLOGY', 'Gynecologist'),
        ('PSYCHIATRY', 'Psychiatrist'),
        ('OPHTHALMOLOGY', 'Ophthalmologist'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES, default='GENERAL')
    qualification = models.CharField(max_length=250)
    experience_years = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bio = models.TextField(blank=True, null=True)
    hospital_name = models.CharField(max_length=200)
    address = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username} ({self.get_specialization_display()})"


# ─────────────────────────────────────────────────────────────────────────────
# OTP Verification
# ─────────────────────────────────────────────────────────────────────────────

class OTPVerification(models.Model):
    PURPOSE_CHOICES = (
        ('REGISTRATION', 'Registration'),
        ('LOGIN_2FA',    '2FA Login'),
        ('PASSWORD_RESET', 'Password Reset'),
    )

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otps')
    otp_code   = models.CharField(max_length=6)
    purpose    = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='REGISTRATION')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used    = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'OTP Verification'
        ordering = ['-created_at']

    def __str__(self):
        return f"OTP [{self.otp_code}] for {self.user.username} — {self.purpose}"

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_valid(self):
        return not self.is_used and not self.is_expired()


# ─────────────────────────────────────────────────────────────────────────────
# Email Verification Token
# ─────────────────────────────────────────────────────────────────────────────

class EmailVerificationToken(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_tokens')
    token      = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used    = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Email Verification Token'
        ordering = ['-created_at']

    def __str__(self):
        return f"EmailToken for {self.user.username}"

    def is_expired(self):
        return timezone.now() > self.expires_at

    def is_valid(self):
        return not self.is_used and not self.is_expired()


# ─────────────────────────────────────────────────────────────────────────────
# Login History
# ─────────────────────────────────────────────────────────────────────────────

class LoginHistory(models.Model):
    STATUS_CHOICES = (
        ('SUCCESS', 'Success'),
        ('FAILED',  'Failed'),
        ('LOCKED',  'Account Locked'),
    )

    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history', null=True, blank=True)
    username_attempted = models.CharField(max_length=150, blank=True)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    user_agent  = models.TextField(blank=True)
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='SUCCESS')
    timestamp   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Login History'
        verbose_name_plural = 'Login Histories'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.username_attempted} — {self.status} @ {self.timestamp:%Y-%m-%d %H:%M}"

    def get_browser(self):
        ua = self.user_agent.lower()
        if 'chrome' in ua and 'chromium' not in ua and 'edg' not in ua:
            return 'Chrome'
        elif 'firefox' in ua:
            return 'Firefox'
        elif 'safari' in ua and 'chrome' not in ua:
            return 'Safari'
        elif 'edg' in ua:
            return 'Edge'
        elif 'opera' in ua or 'opr' in ua:
            return 'Opera'
        return 'Unknown Browser'

    def get_os(self):
        ua = self.user_agent.lower()
        if 'windows' in ua:
            return 'Windows'
        elif 'android' in ua:
            return 'Android'
        elif 'iphone' in ua or 'ipad' in ua:
            return 'iOS'
        elif 'mac' in ua:
            return 'macOS'
        elif 'linux' in ua:
            return 'Linux'
        return 'Unknown OS'


# ─────────────────────────────────────────────────────────────────────────────
# Active Session Tracking
# ─────────────────────────────────────────────────────────────────────────────

class UserSession(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    user_agent  = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Session'
        ordering = ['-last_active']

    def __str__(self):
        return f"Session for {self.user.username} from {self.ip_address}"

    def get_browser(self):
        ua = self.user_agent.lower()
        if 'chrome' in ua and 'chromium' not in ua and 'edg' not in ua:
            return 'Chrome'
        elif 'firefox' in ua:
            return 'Firefox'
        elif 'safari' in ua and 'chrome' not in ua:
            return 'Safari'
        elif 'edg' in ua:
            return 'Edge'
        return 'Unknown'

    def get_os(self):
        ua = self.user_agent.lower()
        if 'windows' in ua:
            return 'Windows'
        elif 'android' in ua:
            return 'Android'
        elif 'iphone' in ua or 'ipad' in ua:
            return 'iOS'
        elif 'mac' in ua:
            return 'macOS'
        elif 'linux' in ua:
            return 'Linux'
        return 'Unknown'
