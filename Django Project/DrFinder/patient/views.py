import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Q, Count, Sum
from django.core.paginator import Paginator

from accounts.models import PatientProfile, DoctorProfile
from accounts.forms import UserUpdateForm, PatientProfileUpdateForm
from appointments.models import Appointment, Prescription
from payments.models import Payment

from .models import (
    MedicalReport, FamilyMember, InsuranceInfo, FavoriteDoctor,
    Wallet, WalletTransaction, Notification, DoctorReview,
    SupportTicket, SupportMessage
)
from .forms import (
    MedicalHistoryForm, MedicalReportForm, FamilyMemberForm,
    InsuranceForm, DoctorReviewForm, SupportTicketForm,
    SupportReplyForm, WalletTopUpForm
)


# ─────────────────────────────────────────────────────────────────────────────
# Mixin
# ─────────────────────────────────────────────────────────────────────────────

class PatientRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'PATIENT'

    def handle_no_permission(self):
        messages.error(self.request, "Access restricted to patients only.")
        return redirect('dashboard')


def get_patient_profile(request):
    return get_object_or_404(PatientProfile, user=request.user)


def get_or_create_wallet(patient):
    wallet, _ = Wallet.objects.get_or_create(patient=patient)
    return wallet


def unread_notification_count(patient):
    return Notification.objects.filter(patient=patient, is_read=False).count()


# ─────────────────────────────────────────────────────────────────────────────
# 1. Dashboard
# ─────────────────────────────────────────────────────────────────────────────

class PatientDashboardView(PatientRequiredMixin, TemplateView):
    template_name = 'patient/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = get_patient_profile(self.request)
        appointments = Appointment.objects.filter(patient=patient)
        wallet = get_or_create_wallet(patient)

        context['patient'] = patient
        context['active_tab'] = 'dashboard'
        context['unread_notifications'] = unread_notification_count(patient)
        context['wallet'] = wallet

        context['upcoming_count'] = appointments.filter(
            Q(status='CONFIRMED') | Q(status='PENDING'),
            slot__date__gte=timezone.now().date()
        ).count()
        context['completed_count'] = appointments.filter(status='COMPLETED').count()
        context['cancelled_count'] = appointments.filter(status='CANCELLED').count()
        context['prescription_count'] = Prescription.objects.filter(patient=patient).count()

        context['recent_appointments'] = appointments.filter(
            Q(status='CONFIRMED') | Q(status='PENDING'),
            slot__date__gte=timezone.now().date()
        ).order_by('slot__date', 'slot__start_time')[:3]

        context['recent_prescriptions'] = Prescription.objects.filter(
            patient=patient
        ).order_by('-created_at')[:3]

        context['recent_notifications'] = Notification.objects.filter(
            patient=patient
        ).order_by('-created_at')[:5]

        return context


# ─────────────────────────────────────────────────────────────────────────────
# 2. Profile
# ─────────────────────────────────────────────────────────────────────────────

class PatientProfileView(PatientRequiredMixin, View):
    template_name = 'patient/profile.html'

    def get(self, request, *args, **kwargs):
        patient = get_patient_profile(request)
        user_form = UserUpdateForm(instance=request.user)
        profile_form = PatientProfileUpdateForm(instance=patient)
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
            'patient': patient,
            'active_tab': 'profile',
            'unread_notifications': unread_notification_count(patient),
        })

    def post(self, request, *args, **kwargs):
        patient = get_patient_profile(request)
        user_form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
        profile_form = PatientProfileUpdateForm(request.POST, instance=patient)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('patient_profile')
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form,
            'patient': patient,
            'active_tab': 'profile',
            'unread_notifications': unread_notification_count(patient),
        })


# ─────────────────────────────────────────────────────────────────────────────
# 3. Medical History
# ─────────────────────────────────────────────────────────────────────────────

class MedicalHistoryView(PatientRequiredMixin, View):
    template_name = 'patient/medical_history.html'

    def get(self, request, *args, **kwargs):
        patient = get_patient_profile(request)
        form = MedicalHistoryForm(instance=patient)
        return render(request, self.template_name, {
            'form': form,
            'patient': patient,
            'active_tab': 'medical_history',
            'unread_notifications': unread_notification_count(patient),
        })

    def post(self, request, *args, **kwargs):
        patient = get_patient_profile(request)
        form = MedicalHistoryForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, "Medical history updated successfully!")
            return redirect('medical_history')
        return render(request, self.template_name, {
            'form': form,
            'patient': patient,
            'active_tab': 'medical_history',
            'unread_notifications': unread_notification_count(patient),
        })


# ─────────────────────────────────────────────────────────────────────────────
# 4. Upload Reports
# ─────────────────────────────────────────────────────────────────────────────

class UploadReportsView(PatientRequiredMixin, View):
    template_name = 'patient/upload_reports.html'

    def get(self, request, *args, **kwargs):
        patient = get_patient_profile(request)
        form = MedicalReportForm()
        reports = MedicalReport.objects.filter(patient=patient)
        return render(request, self.template_name, {
            'form': form,
            'reports': reports,
            'patient': patient,
            'active_tab': 'upload_reports',
            'unread_notifications': unread_notification_count(patient),
        })

    def post(self, request, *args, **kwargs):
        patient = get_patient_profile(request)
        form = MedicalReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.patient = patient
            report.save()
            messages.success(request, "Report uploaded successfully!")
            return redirect('upload_reports')
        reports = MedicalReport.objects.filter(patient=patient)
        return render(request, self.template_name, {
            'form': form,
            'reports': reports,
            'patient': patient,
            'active_tab': 'upload_reports',
            'unread_notifications': unread_notification_count(patient),
        })


class DeleteReportView(PatientRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        patient = get_patient_profile(request)
        report = get_object_or_404(MedicalReport, id=pk, patient=patient)
        report.report_file.delete(save=False)
        report.delete()
        messages.success(request, "Report deleted successfully.")
        return redirect('upload_reports')


# ─────────────────────────────────────────────────────────────────────────────
# 5. Family Members
# ─────────────────────────────────────────────────────────────────────────────

class FamilyMembersView(PatientRequiredMixin, View):
    template_name = 'patient/family_members.html'

    def get(self, request, *args, **kwargs):
        patient = get_patient_profile(request)
        form = FamilyMemberForm()
        members = FamilyMember.objects.filter(patient=patient)
        return render(request, self.template_name, {
            'form': form,
            'members': members,
            'patient': patient,
            'active_tab': 'family_members',
            'unread_notifications': unread_notification_count(patient),
        })

    def post(self, request, *args, **kwargs):
        patient = get_patient_profile(request)
        form = FamilyMemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.patient = patient
            member.save()
            messages.success(request, f"{member.full_name} added to family members!")
            return redirect('family_members')
        members = FamilyMember.objects.filter(patient=patient)
        return render(request, self.template_name, {
            'form': form,
            'members': members,
            'patient': patient,
            'active_tab': 'family_members',
            'unread_notifications': unread_notification_count(patient),
        })


class DeleteFamilyMemberView(PatientRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        patient = get_patient_profile(request)
        member = get_object_or_404(FamilyMember, id=pk, patient=patient)
        member.delete()
        messages.success(request, "Family member removed.")
        return redirect('family_members')


# ─────────────────────────────────────────────────────────────────────────────
# 6. Insurance Information
# ─────────────────────────────────────────────────────────────────────────────

class InsuranceView(PatientRequiredMixin, View):
    template_name = 'patient/insurance.html'

    def _get_insurance(self, patient):
        try:
            return patient.insurance_info
        except InsuranceInfo.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        patient = get_patient_profile(request)
        insurance = self._get_insurance(patient)
        form = InsuranceForm(instance=insurance)
        return render(request, self.template_name, {
            'form': form,
            'insurance': insurance,
            'patient': patient,
            'active_tab': 'insurance',
            'unread_notifications': unread_notification_count(patient),
        })

    def post(self, request, *args, **kwargs):
        patient = get_patient_profile(request)
        insurance = self._get_insurance(patient)
        form = InsuranceForm(request.POST, instance=insurance)
        if form.is_valid():
            ins = form.save(commit=False)
            ins.patient = patient
            ins.save()
            messages.success(request, "Insurance information saved!")
            return redirect('insurance_info')
        return render(request, self.template_name, {
            'form': form,
            'insurance': insurance,
            'patient': patient,
            'active_tab': 'insurance',
            'unread_notifications': unread_notification_count(patient),
        })


# ─────────────────────────────────────────────────────────────────────────────
# 7. Favorite Doctors
# ─────────────────────────────────────────────────────────────────────────────

class FavoriteDoctorsView(PatientRequiredMixin, TemplateView):
    template_name = 'patient/favorite_doctors.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = get_patient_profile(self.request)
        favorites = FavoriteDoctor.objects.filter(patient=patient).select_related('doctor__user')
        context['favorites'] = favorites
        context['patient'] = patient
        context['active_tab'] = 'favorite_doctors'
        context['unread_notifications'] = unread_notification_count(patient)
        return context


class ToggleFavoriteView(PatientRequiredMixin, View):
    def post(self, request, doctor_id, *args, **kwargs):
        patient = get_patient_profile(request)
        doctor = get_object_or_404(DoctorProfile, id=doctor_id)
        fav = FavoriteDoctor.objects.filter(patient=patient, doctor=doctor).first()
        if fav:
            fav.delete()
            messages.success(request, f"Dr. {doctor.user.get_full_name()} removed from favorites.")
        else:
            FavoriteDoctor.objects.create(patient=patient, doctor=doctor)
            messages.success(request, f"Dr. {doctor.user.get_full_name()} added to favorites!")
        next_url = request.POST.get('next', 'favorite_doctors')
        return redirect(next_url)


# ─────────────────────────────────────────────────────────────────────────────
# 8. Appointment History
# ─────────────────────────────────────────────────────────────────────────────

class AppointmentHistoryView(PatientRequiredMixin, TemplateView):
    template_name = 'patient/appointment_history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = get_patient_profile(self.request)
        all_appointments = Appointment.objects.filter(patient=patient).order_by('-slot__date', '-slot__start_time')
        paginator = Paginator(all_appointments, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj
        context['patient'] = patient
        context['active_tab'] = 'appointment_history'
        context['unread_notifications'] = unread_notification_count(patient)
        return context


# ─────────────────────────────────────────────────────────────────────────────
# 9. Upcoming Appointments
# ─────────────────────────────────────────────────────────────────────────────

class UpcomingAppointmentsView(PatientRequiredMixin, TemplateView):
    template_name = 'patient/upcoming_appointments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = get_patient_profile(self.request)
        upcoming = Appointment.objects.filter(
            patient=patient,
            slot__date__gte=timezone.now().date()
        ).filter(
            Q(status='CONFIRMED') | Q(status='PENDING')
        ).order_by('slot__date', 'slot__start_time')
        context['upcoming'] = upcoming
        context['patient'] = patient
        context['active_tab'] = 'upcoming_appointments'
        context['unread_notifications'] = unread_notification_count(patient)
        return context


# ─────────────────────────────────────────────────────────────────────────────
# 10. Cancelled Appointments
# ─────────────────────────────────────────────────────────────────────────────

class CancelledAppointmentsView(PatientRequiredMixin, TemplateView):
    template_name = 'patient/cancelled_appointments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = get_patient_profile(self.request)
        cancelled = Appointment.objects.filter(
            patient=patient, status='CANCELLED'
        ).order_by('-slot__date')
        context['cancelled'] = cancelled
        context['patient'] = patient
        context['active_tab'] = 'cancelled_appointments'
        context['unread_notifications'] = unread_notification_count(patient)
        return context


# ─────────────────────────────────────────────────────────────────────────────
# 11. Download Prescriptions
# ─────────────────────────────────────────────────────────────────────────────

class PrescriptionsView(PatientRequiredMixin, TemplateView):
    template_name = 'patient/prescriptions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = get_patient_profile(self.request)
        prescriptions = Prescription.objects.filter(patient=patient).order_by('-created_at')
        context['prescriptions'] = prescriptions
        context['patient'] = patient
        context['active_tab'] = 'prescriptions'
        context['unread_notifications'] = unread_notification_count(patient)
        return context


class PrintPrescriptionView(PatientRequiredMixin, View):
    template_name = 'patient/print_prescription.html'

    def get(self, request, pk, *args, **kwargs):
        patient = get_patient_profile(request)
        prescription = get_object_or_404(Prescription, id=pk, patient=patient)
        return render(request, self.template_name, {'prescription': prescription})


# ─────────────────────────────────────────────────────────────────────────────
# 12. Invoices
# ─────────────────────────────────────────────────────────────────────────────

class InvoicesView(PatientRequiredMixin, TemplateView):
    template_name = 'patient/invoices.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = get_patient_profile(self.request)
        payments = Payment.objects.filter(
            appointment__patient=patient
        ).order_by('-timestamp')
        total_spent = payments.filter(status='SUCCESS').aggregate(
            total=Sum('amount')
        )['total'] or 0
        context['payments'] = payments
        context['total_spent'] = total_spent
        context['patient'] = patient
        context['active_tab'] = 'invoices'
        context['unread_notifications'] = unread_notification_count(patient)
        return context


# ─────────────────────────────────────────────────────────────────────────────
# 13. Wallet
# ─────────────────────────────────────────────────────────────────────────────

class WalletView(PatientRequiredMixin, View):
    template_name = 'patient/wallet.html'

    def get(self, request, *args, **kwargs):
        patient = get_patient_profile(request)
        wallet = get_or_create_wallet(patient)
        transactions = wallet.transactions.all()[:20]
        form = WalletTopUpForm()
        return render(request, self.template_name, {
            'wallet': wallet,
            'transactions': transactions,
            'form': form,
            'patient': patient,
            'active_tab': 'wallet',
            'unread_notifications': unread_notification_count(patient),
        })

    def post(self, request, *args, **kwargs):
        patient = get_patient_profile(request)
        wallet = get_or_create_wallet(patient)
        form = WalletTopUpForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['final_amount']
            wallet.balance += amount
            wallet.save()
            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type='CREDIT',
                amount=amount,
                description='Wallet Top-Up',
                reference=f'TOPUP-{uuid.uuid4().hex[:8].upper()}'
            )
            messages.success(request, f"₹{amount} added to your wallet successfully!")
            return redirect('patient_wallet')
        transactions = wallet.transactions.all()[:20]
        return render(request, self.template_name, {
            'wallet': wallet,
            'transactions': transactions,
            'form': form,
            'patient': patient,
            'active_tab': 'wallet',
            'unread_notifications': unread_notification_count(patient),
        })


# ─────────────────────────────────────────────────────────────────────────────
# 14. Notifications
# ─────────────────────────────────────────────────────────────────────────────

class NotificationsView(PatientRequiredMixin, View):
    template_name = 'patient/notifications.html'

    def get(self, request, *args, **kwargs):
        patient = get_patient_profile(request)
        notifications = Notification.objects.filter(patient=patient)
        return render(request, self.template_name, {
            'notifications': notifications,
            'patient': patient,
            'active_tab': 'notifications',
            'unread_notifications': unread_notification_count(patient),
        })

    def post(self, request, *args, **kwargs):
        patient = get_patient_profile(request)
        action = request.POST.get('action')
        notif_id = request.POST.get('notif_id')

        if action == 'mark_all_read':
            Notification.objects.filter(patient=patient, is_read=False).update(is_read=True)
            messages.success(request, "All notifications marked as read.")
        elif action == 'mark_read' and notif_id:
            Notification.objects.filter(id=notif_id, patient=patient).update(is_read=True)
        elif action == 'delete' and notif_id:
            Notification.objects.filter(id=notif_id, patient=patient).delete()

        return redirect('patient_notifications')


# ─────────────────────────────────────────────────────────────────────────────
# 15. Reviews & Ratings
# ─────────────────────────────────────────────────────────────────────────────

class ReviewsView(PatientRequiredMixin, View):
    template_name = 'patient/reviews.html'

    def get(self, request, *args, **kwargs):
        patient = get_patient_profile(request)
        my_reviews = DoctorReview.objects.filter(patient=patient)
        # Get completed appointments that don't yet have a review
        reviewed_appointment_ids = DoctorReview.objects.filter(
            patient=patient
        ).values_list('appointment_id', flat=True)
        reviewable = Appointment.objects.filter(
            patient=patient, status='COMPLETED'
        ).exclude(id__in=reviewed_appointment_ids)

        return render(request, self.template_name, {
            'my_reviews': my_reviews,
            'reviewable': reviewable,
            'form': DoctorReviewForm(),
            'patient': patient,
            'active_tab': 'reviews',
            'unread_notifications': unread_notification_count(patient),
        })

    def post(self, request, *args, **kwargs):
        patient = get_patient_profile(request)
        appointment_id = request.POST.get('appointment_id')
        appointment = get_object_or_404(Appointment, id=appointment_id, patient=patient, status='COMPLETED')

        # Prevent duplicate review
        if DoctorReview.objects.filter(appointment=appointment).exists():
            messages.error(request, "You have already reviewed this appointment.")
            return redirect('patient_reviews')

        form = DoctorReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.patient = patient
            review.doctor = appointment.doctor
            review.appointment = appointment
            review.save()
            messages.success(request, "Your review has been submitted. Thank you!")
            return redirect('patient_reviews')

        my_reviews = DoctorReview.objects.filter(patient=patient)
        reviewed_ids = DoctorReview.objects.filter(patient=patient).values_list('appointment_id', flat=True)
        reviewable = Appointment.objects.filter(patient=patient, status='COMPLETED').exclude(id__in=reviewed_ids)
        return render(request, self.template_name, {
            'my_reviews': my_reviews,
            'reviewable': reviewable,
            'form': form,
            'patient': patient,
            'active_tab': 'reviews',
            'unread_notifications': unread_notification_count(patient),
        })


# ─────────────────────────────────────────────────────────────────────────────
# 16. Help Center
# ─────────────────────────────────────────────────────────────────────────────

class HelpCenterView(PatientRequiredMixin, TemplateView):
    template_name = 'patient/help_center.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = get_patient_profile(self.request)
        context['patient'] = patient
        context['active_tab'] = 'help_center'
        context['unread_notifications'] = unread_notification_count(patient)
        return context


# ─────────────────────────────────────────────────────────────────────────────
# 17. Support Tickets
# ─────────────────────────────────────────────────────────────────────────────

class SupportTicketsView(PatientRequiredMixin, View):
    template_name = 'patient/support_tickets.html'

    def get(self, request, *args, **kwargs):
        patient = get_patient_profile(request)
        tickets = SupportTicket.objects.filter(patient=patient)
        form = SupportTicketForm()
        return render(request, self.template_name, {
            'tickets': tickets,
            'form': form,
            'patient': patient,
            'active_tab': 'support_tickets',
            'unread_notifications': unread_notification_count(patient),
        })

    def post(self, request, *args, **kwargs):
        patient = get_patient_profile(request)
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = SupportTicket.objects.create(
                patient=patient,
                subject=form.cleaned_data['subject'],
                category=form.cleaned_data['category'],
                priority=form.cleaned_data['priority'],
            )
            SupportMessage.objects.create(
                ticket=ticket,
                sender_patient=patient,
                message=form.cleaned_data['initial_message'],
                is_staff_reply=False
            )
            messages.success(request, f"Support ticket #{ticket.id} created successfully!")
            return redirect('support_ticket_detail', pk=ticket.id)
        tickets = SupportTicket.objects.filter(patient=patient)
        return render(request, self.template_name, {
            'tickets': tickets,
            'form': form,
            'patient': patient,
            'active_tab': 'support_tickets',
            'unread_notifications': unread_notification_count(patient),
        })


class SupportTicketDetailView(PatientRequiredMixin, View):
    template_name = 'patient/support_ticket_detail.html'

    def get(self, request, pk, *args, **kwargs):
        patient = get_patient_profile(request)
        ticket = get_object_or_404(SupportTicket, id=pk, patient=patient)
        messages_qs = ticket.messages.order_by('created_at')
        reply_form = SupportReplyForm()
        return render(request, self.template_name, {
            'ticket': ticket,
            'ticket_messages': messages_qs,
            'reply_form': reply_form,
            'patient': patient,
            'active_tab': 'support_tickets',
            'unread_notifications': unread_notification_count(patient),
        })

    def post(self, request, pk, *args, **kwargs):
        patient = get_patient_profile(request)
        ticket = get_object_or_404(SupportTicket, id=pk, patient=patient)
        if ticket.status == 'CLOSED':
            messages.error(request, "This ticket is closed. Please open a new ticket.")
            return redirect('support_ticket_detail', pk=pk)
        reply_form = SupportReplyForm(request.POST)
        if reply_form.is_valid():
            msg = reply_form.save(commit=False)
            msg.ticket = ticket
            msg.sender_patient = patient
            msg.is_staff_reply = False
            msg.save()
            if ticket.status == 'RESOLVED':
                ticket.status = 'OPEN'
                ticket.save()
            messages.success(request, "Your reply has been sent.")
            return redirect('support_ticket_detail', pk=pk)
        messages_qs = ticket.messages.order_by('created_at')
        return render(request, self.template_name, {
            'ticket': ticket,
            'ticket_messages': messages_qs,
            'reply_form': reply_form,
            'patient': patient,
            'active_tab': 'support_tickets',
            'unread_notifications': unread_notification_count(patient),
        })
