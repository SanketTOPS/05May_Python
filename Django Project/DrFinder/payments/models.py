from django.db import models
from appointments.models import Appointment


class Payment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    )

    appointment       = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='payment')
    amount            = models.DecimalField(max_digits=10, decimal_places=2)
    status            = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    transaction_id    = models.CharField(max_length=100, unique=True)
    payment_method    = models.CharField(max_length=50, blank=True, null=True)
    timestamp         = models.DateTimeField(auto_now_add=True)

    # Razorpay-specific fields
    razorpay_order_id   = models.CharField(max_length=120, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=120, blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    @property
    def formatted_payment_method(self):
        return self.payment_method.replace('_', ' ').title() if self.payment_method else ""

    def __str__(self):
        return f"Payment #{self.transaction_id} - {self.amount} - {self.status}"
