from django.db import models
from django.utils import timezone
from accounts.models import PatientProfile, DoctorProfile


# ─────────────────────────────────────────────────────────────────────────────
# Medical Report Upload
# ─────────────────────────────────────────────────────────────────────────────

class MedicalReport(models.Model):
    REPORT_TYPE_CHOICES = (
        ('BLOOD_TEST', 'Blood Test'),
        ('XRAY', 'X-Ray'),
        ('MRI', 'MRI Scan'),
        ('CT_SCAN', 'CT Scan'),
        ('URINE_TEST', 'Urine Test'),
        ('ECG', 'ECG'),
        ('ULTRASOUND', 'Ultrasound'),
        ('OTHER', 'Other'),
    )

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='medical_reports')
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, default='OTHER')
    report_file = models.FileField(upload_to='medical_reports/')
    notes = models.TextField(blank=True, null=True)
    report_date = models.DateField(default=timezone.now)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Medical Report'

    def __str__(self):
        return f"{self.title} — {self.patient.user.get_full_name()}"

    def get_file_extension(self):
        import os
        _, ext = os.path.splitext(self.report_file.name)
        return ext.lower()

    def is_image(self):
        return self.get_file_extension() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']


# ─────────────────────────────────────────────────────────────────────────────
# Family Members
# ─────────────────────────────────────────────────────────────────────────────

class FamilyMember(models.Model):
    RELATION_CHOICES = (
        ('SPOUSE', 'Spouse'),
        ('CHILD', 'Child'),
        ('PARENT', 'Parent'),
        ('SIBLING', 'Sibling'),
        ('GRANDPARENT', 'Grandparent'),
        ('OTHER', 'Other'),
    )

    GENDER_CHOICES = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
    )

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='family_members')
    full_name = models.CharField(max_length=150)
    relation = models.CharField(max_length=20, choices=RELATION_CHOICES, default='OTHER')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    medical_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['full_name']
        verbose_name = 'Family Member'

    def __str__(self):
        return f"{self.full_name} ({self.get_relation_display()}) — {self.patient.user.get_full_name()}"

    def age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Insurance Information
# ─────────────────────────────────────────────────────────────────────────────

class InsuranceInfo(models.Model):
    PLAN_TYPE_CHOICES = (
        ('INDIVIDUAL', 'Individual'),
        ('FAMILY', 'Family'),
        ('GROUP', 'Group'),
        ('GOVERNMENT', 'Government'),
    )

    patient = models.OneToOneField(PatientProfile, on_delete=models.CASCADE, related_name='insurance_info')
    provider_name = models.CharField(max_length=200)
    policy_number = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, default='INDIVIDUAL')
    coverage_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    expiry_date = models.DateField()
    holder_name = models.CharField(max_length=150)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Insurance Info'

    def __str__(self):
        return f"{self.provider_name} — {self.policy_number}"

    def is_expired(self):
        return timezone.now().date() > self.expiry_date

    def days_until_expiry(self):
        delta = self.expiry_date - timezone.now().date()
        return delta.days


# ─────────────────────────────────────────────────────────────────────────────
# Favorite Doctors
# ─────────────────────────────────────────────────────────────────────────────

class FavoriteDoctor(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='favorite_doctors')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('patient', 'doctor')
        ordering = ['-added_at']
        verbose_name = 'Favorite Doctor'

    def __str__(self):
        return f"{self.patient.user.get_full_name()} ❤ Dr. {self.doctor.user.get_full_name()}"


# ─────────────────────────────────────────────────────────────────────────────
# Wallet
# ─────────────────────────────────────────────────────────────────────────────

class Wallet(models.Model):
    patient = models.OneToOneField(PatientProfile, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet of {self.patient.user.get_full_name()} — ₹{self.balance}"


class WalletTransaction(models.Model):
    TYPE_CHOICES = (
        ('CREDIT', 'Credit'),
        ('DEBIT', 'Debit'),
    )

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=300)
    reference = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Wallet Transaction'

    def __str__(self):
        return f"{self.transaction_type} ₹{self.amount} — {self.description}"


# ─────────────────────────────────────────────────────────────────────────────
# Notifications
# ─────────────────────────────────────────────────────────────────────────────

class Notification(models.Model):
    TYPE_CHOICES = (
        ('APPOINTMENT', 'Appointment'),
        ('PRESCRIPTION', 'Prescription'),
        ('PAYMENT', 'Payment'),
        ('SYSTEM', 'System'),
        ('REMINDER', 'Reminder'),
    )

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='SYSTEM')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'

    def __str__(self):
        return f"[{self.notification_type}] {self.title} — {self.patient.user.get_full_name()}"


# ─────────────────────────────────────────────────────────────────────────────
# Doctor Reviews & Ratings
# ─────────────────────────────────────────────────────────────────────────────

class DoctorReview(models.Model):
    RATING_CHOICES = (
        (1, '⭐ Poor'),
        (2, '⭐⭐ Fair'),
        (3, '⭐⭐⭐ Good'),
        (4, '⭐⭐⭐⭐ Very Good'),
        (5, '⭐⭐⭐⭐⭐ Excellent'),
    )

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='reviews')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='reviews')
    appointment = models.OneToOneField(
        'appointments.Appointment',
        on_delete=models.CASCADE,
        related_name='review',
        null=True,
        blank=True
    )
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    review_text = models.TextField(blank=True, null=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Doctor Review'

    def __str__(self):
        return f"{self.rating}★ by {self.patient.user.get_full_name()} for Dr. {self.doctor.user.get_full_name()}"


# ─────────────────────────────────────────────────────────────────────────────
# Support Tickets
# ─────────────────────────────────────────────────────────────────────────────

class SupportTicket(models.Model):
    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    )

    CATEGORY_CHOICES = (
        ('APPOINTMENT', 'Appointment Issue'),
        ('PAYMENT', 'Payment Issue'),
        ('PRESCRIPTION', 'Prescription Issue'),
        ('ACCOUNT', 'Account Issue'),
        ('TECHNICAL', 'Technical Issue'),
        ('OTHER', 'Other'),
    )

    PRIORITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    )

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=300)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Support Ticket'

    def __str__(self):
        return f"#{self.id} {self.subject} [{self.status}]"


class SupportMessage(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='messages')
    sender_patient = models.ForeignKey(PatientProfile, on_delete=models.SET_NULL, null=True, blank=True)
    is_staff_reply = models.BooleanField(default=False)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        sender = "Staff" if self.is_staff_reply else self.ticket.patient.user.get_full_name()
        return f"Message by {sender} on #{self.ticket.id}"
