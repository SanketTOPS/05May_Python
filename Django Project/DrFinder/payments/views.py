import uuid
import hmac
import hashlib

import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from appointments.models import Appointment, AvailabilitySlot
from .models import Payment


# ─── Helper mixin ─────────────────────────────────────────────────────────────

class PatientRequiredMixin(LoginRequiredMixin):
    """Allow only authenticated PATIENT-role users."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'PATIENT':
            messages.error(request, "Access restricted to patients only.")
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


# ─── Razorpay client factory ──────────────────────────────────────────────────

def get_razorpay_client():
    return razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )


# ─── Views ────────────────────────────────────────────────────────────────────

class PaymentCheckoutView(PatientRequiredMixin, View):
    """
    Creates a Razorpay Order server-side and renders the checkout page
    with the Razorpay JS SDK pre-configured.
    """
    template_name = 'payments/checkout.html'

    def get(self, request, appointment_id, *args, **kwargs):
        appointment = get_object_or_404(
            Appointment, id=appointment_id, patient__user=request.user
        )

        if appointment.status != 'PENDING':
            messages.warning(request, "This appointment has already been processed.")
            return redirect('dashboard')

        fee = appointment.doctor.consultation_fee
        # Razorpay expects amount in paise (1 INR = 100 paise)
        amount_paise = int(fee * 100)

        client = get_razorpay_client()
        razorpay_order = client.order.create({
            'amount': amount_paise,
            'currency': 'INR',
            'payment_capture': 1,  # auto-capture on success
            'notes': {
                'appointment_id': str(appointment.id),
                'patient': request.user.get_full_name(),
                'doctor': appointment.doctor.user.get_full_name(),
            }
        })

        context = {
            'appointment':      appointment,
            'fee':              fee,
            'razorpay_key_id':  settings.RAZORPAY_KEY_ID,
            'razorpay_order_id': razorpay_order['id'],
            'amount_paise':     amount_paise,
            'user_name':        request.user.get_full_name(),
            'user_email':       request.user.email,
        }
        return render(request, self.template_name, context)


@method_decorator(csrf_exempt, name='dispatch')
class RazorpayCallbackView(PatientRequiredMixin, View):
    """
    Handles the payment success callback from Razorpay JS SDK.
    Verifies HMAC signature, then confirms the appointment.
    """

    def post(self, request, appointment_id, *args, **kwargs):
        appointment = get_object_or_404(
            Appointment, id=appointment_id, patient__user=request.user
        )

        if appointment.status != 'PENDING':
            messages.warning(request, "This appointment has already been processed.")
            return redirect('dashboard')

        razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id   = request.POST.get('razorpay_order_id', '')
        razorpay_signature  = request.POST.get('razorpay_signature', '')

        # ── HMAC-SHA256 signature verification ────────────────────────────────
        secret = settings.RAZORPAY_KEY_SECRET.encode('utf-8')
        msg    = f"{razorpay_order_id}|{razorpay_payment_id}".encode('utf-8')
        expected_sig = hmac.new(secret, msg, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected_sig, razorpay_signature):
            messages.error(request, "Payment verification failed. Please contact support.")
            return redirect('payment_checkout', appointment_id=appointment.id)

        # ── All good – persist payment record ─────────────────────────────────
        txn_id = f"RZP-{razorpay_payment_id[-12:].upper()}"

        payment = Payment.objects.create(
            appointment         = appointment,
            amount              = appointment.doctor.consultation_fee,
            status              = 'SUCCESS',
            transaction_id      = txn_id,
            payment_method      = 'RAZORPAY',
            razorpay_order_id   = razorpay_order_id,
            razorpay_payment_id = razorpay_payment_id,
        )

        # ── Confirm appointment & lock slot ───────────────────────────────────
        appointment.status = 'CONFIRMED'
        appointment.save()

        slot = appointment.slot
        slot.is_booked = True
        slot.save()

        messages.success(
            request,
            f"Payment of ₹{payment.amount} successful! Your appointment is confirmed."
        )
        return redirect('payment_receipt', payment_id=payment.id)


class PaymentReceiptView(LoginRequiredMixin, View):
    """Show the receipt – accessible by patient, doctor of the appointment, or admin."""
    template_name = 'payments/receipt.html'

    def get(self, request, payment_id, *args, **kwargs):
        payment = get_object_or_404(Payment, id=payment_id)

        user       = request.user
        is_patient = (user.role == 'PATIENT' and payment.appointment.patient.user == user)
        is_doctor  = (user.role == 'DOCTOR'  and payment.appointment.doctor.user == user)
        is_admin   = (user.role == 'ADMIN' or user.is_superuser)

        if not (is_patient or is_doctor or is_admin):
            messages.error(request, "Unauthorized to view this page.")
            return redirect('dashboard')

        return render(request, self.template_name, {'payment': payment})
