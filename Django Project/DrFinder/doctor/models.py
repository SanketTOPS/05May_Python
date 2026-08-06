from django.db import models
from django.utils import timezone
from accounts.models import DoctorProfile, PatientProfile, User


# ─────────────────────────────────────────────────────────────────────────────
# Education
# ─────────────────────────────────────────────────────────────────────────────

class DoctorEducation(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='education')
    degree = models.CharField(max_length=150)
    institute = models.CharField(max_length=200)
    year_of_completion = models.PositiveIntegerField()

    class Meta:
        ordering = ['-year_of_completion']
        verbose_name = 'Doctor Education'
        verbose_name_plural = 'Doctor Education'

    def __str__(self):
        return f"{self.degree} from {self.institute} ({self.year_of_completion})"


# ─────────────────────────────────────────────────────────────────────────────
# Experience
# ─────────────────────────────────────────────────────────────────────────────

class DoctorExperience(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='experience')
    designation = models.CharField(max_length=150)
    hospital_name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Doctor Experience'
        verbose_name_plural = 'Doctor Experience'

    def __str__(self):
        end = "Present" if self.is_current else self.end_date
        return f"{self.designation} at {self.hospital_name} ({self.start_date} to {end})"


# ─────────────────────────────────────────────────────────────────────────────
# Awards
# ─────────────────────────────────────────────────────────────────────────────

class DoctorAward(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='awards')
    title = models.CharField(max_length=200)
    year = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-year']
        verbose_name = 'Doctor Award'

    def __str__(self):
        return f"{self.title} ({self.year})"


# ─────────────────────────────────────────────────────────────────────────────
# Certificates
# ─────────────────────────────────────────────────────────────────────────────

class DoctorCertificate(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='certificates')
    title = models.CharField(max_length=200)
    certificate_file = models.FileField(upload_to='doctor_certificates/')
    issued_by = models.CharField(max_length=200, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Doctor Certificate'

    def __str__(self):
        return f"{self.title} — Dr. {self.doctor.user.get_full_name()}"


# ─────────────────────────────────────────────────────────────────────────────
# Leave Management
# ─────────────────────────────────────────────────────────────────────────────

class DoctorLeave(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='leaves')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='APPROVED')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Doctor Leave'

    def __str__(self):
        return f"Leave for Dr. {self.doctor.user.get_full_name()} ({self.start_date} to {self.end_date})"

    def is_upcoming(self):
        return self.start_date >= timezone.now().date()

    def is_active(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date


# ─────────────────────────────────────────────────────────────────────────────
# Patient-Doctor Live Chat
# ─────────────────────────────────────────────────────────────────────────────

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Chat Message'

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username} @ {self.timestamp}"
