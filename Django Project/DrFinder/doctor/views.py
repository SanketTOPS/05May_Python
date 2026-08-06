from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q, Avg
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from datetime import datetime, timedelta, date

from accounts.models import DoctorProfile, PatientProfile, User
from appointments.models import AvailabilitySlot, Appointment, Prescription
from payments.models import Payment
from patient.models import MedicalReport

from .models import (
    DoctorEducation, DoctorExperience, DoctorAward,
    DoctorCertificate, DoctorLeave, ChatMessage
)
from .forms import (
    DoctorProfileForm, EducationForm, ExperienceForm,
    AwardForm, CertificateForm, SlotGenerationForm,
    LeaveForm, PrescriptionForm
)


# ─────────────────────────────────────────────────────────────────────────────
# Access Control Mixin
# ─────────────────────────────────────────────────────────────────────────────

class DoctorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'DOCTOR'

    def handle_no_permission(self):
        messages.error(self.request, "Access restricted to doctors only.")
        return redirect('dashboard')


def get_doctor_profile(request):
    return get_object_or_404(DoctorProfile, user=request.user)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Doctor Dashboard
# ─────────────────────────────────────────────────────────────────────────────

class DoctorDashboardView(DoctorRequiredMixin, TemplateView):
    template_name = 'doctor/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = get_doctor_profile(self.request)
        context['doctor'] = doctor
        context['active_tab'] = 'dashboard'

        # Account status check
        if doctor.status != 'APPROVED':
            context['pending_approval'] = True
            return context
        context['pending_approval'] = False

        # Stats
        appointments = Appointment.objects.filter(doctor=doctor)
        context['total_appointments'] = appointments.count()
        context['upcoming_appointments'] = appointments.filter(
            status='CONFIRMED', slot__date__gte=timezone.now().date()
        ).order_by('slot__date', 'slot__start_time')[:5]

        context['pending_appointments'] = appointments.filter(
            status='PENDING', slot__date__gte=timezone.now().date()
        ).count()

        context['completed_appointments'] = appointments.filter(status='COMPLETED').count()

        total_earnings = Payment.objects.filter(
            appointment__doctor=doctor, status='SUCCESS'
        ).aggregate(total=Sum('amount'))['total'] or 0
        context['total_earnings'] = total_earnings

        # Active Slots
        context['active_slots_count'] = AvailabilitySlot.objects.filter(
            doctor=doctor, date__gte=timezone.now().date(), is_booked=False
        ).count()

        # Chat unread messages count
        unread_chats = ChatMessage.objects.filter(receiver=self.request.user, is_read=False).count()
        context['unread_chats'] = unread_chats

        return context


# ─────────────────────────────────────────────────────────────────────────────
# 2. Profile Management
# ─────────────────────────────────────────────────────────────────────────────

class DoctorProfileView(DoctorRequiredMixin, View):
    template_name = 'doctor/profile.html'

    def get_forms(self, request, doctor):
        return {
            'profile_form': DoctorProfileForm(instance=doctor, initial={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'phone': request.user.phone
            }),
            'edu_form': EducationForm(),
            'exp_form': ExperienceForm(),
            'award_form': AwardForm(),
            'cert_form': CertificateForm()
        }

    def get(self, request, *args, **kwargs):
        doctor = get_doctor_profile(request)
        context = self.get_forms(request, doctor)
        context.update({
            'doctor': doctor,
            'education': doctor.education.all(),
            'experience': doctor.experience.all(),
            'awards': doctor.awards.all(),
            'certificates': doctor.certificates.all(),
            'active_tab': 'profile'
        })
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        doctor = get_doctor_profile(request)
        action = request.POST.get('action')

        if action == 'update_profile':
            form = DoctorProfileForm(request.POST, instance=doctor)
            if form.is_valid():
                # Save user fields
                request.user.first_name = form.cleaned_data['first_name']
                request.user.last_name = form.cleaned_data['last_name']
                request.user.phone = form.cleaned_data['phone']
                request.user.save()
                form.save()
                messages.success(request, "Profile updated successfully!")
            else:
                messages.error(request, "Failed to update profile. Please verify fields.")

        elif action == 'add_education':
            form = EducationForm(request.POST)
            if form.is_valid():
                edu = form.save(commit=False)
                edu.doctor = doctor
                edu.save()
                messages.success(request, "Education detail added!")
            else:
                messages.error(request, "Invalid education input details.")

        elif action == 'add_experience':
            form = ExperienceForm(request.POST)
            if form.is_valid():
                exp = form.save(commit=False)
                exp.doctor = doctor
                exp.save()
                messages.success(request, "Experience record added!")
            else:
                messages.error(request, "Invalid experience input details.")

        elif action == 'add_award':
            form = AwardForm(request.POST)
            if form.is_valid():
                award = form.save(commit=False)
                award.doctor = doctor
                award.save()
                messages.success(request, "Award detail added!")
            else:
                messages.error(request, "Invalid award input details.")

        elif action == 'add_certificate':
            form = CertificateForm(request.POST, request.FILES)
            if form.is_valid():
                cert = form.save(commit=False)
                cert.doctor = doctor
                cert.save()
                messages.success(request, "Certificate uploaded successfully!")
            else:
                messages.error(request, "Failed to upload certificate.")

        elif action == 'delete_edu':
            DoctorEducation.objects.filter(id=request.POST.get('item_id'), doctor=doctor).delete()
            messages.success(request, "Education record deleted.")

        elif action == 'delete_exp':
            DoctorExperience.objects.filter(id=request.POST.get('item_id'), doctor=doctor).delete()
            messages.success(request, "Experience record deleted.")

        elif action == 'delete_award':
            DoctorAward.objects.filter(id=request.POST.get('item_id'), doctor=doctor).delete()
            messages.success(request, "Award record deleted.")

        elif action == 'delete_cert':
            cert = DoctorCertificate.objects.filter(id=request.POST.get('item_id'), doctor=doctor).first()
            if cert:
                cert.certificate_file.delete(save=False)
                cert.delete()
                messages.success(request, "Certificate record deleted.")

        return redirect('doctor_profile')


# ─────────────────────────────────────────────────────────────────────────────
# 3. Availability Schedule & Time Slots
# ─────────────────────────────────────────────────────────────────────────────

class AvailabilityScheduleView(DoctorRequiredMixin, View):
    template_name = 'doctor/schedule.html'

    def get(self, request, *args, **kwargs):
        doctor = get_doctor_profile(request)
        slots = AvailabilitySlot.objects.filter(
            doctor=doctor, date__gte=timezone.now().date()
        ).order_by('date', 'start_time')

        return render(request, self.template_name, {
            'slots': slots,
            'slot_form': SlotGenerationForm(),
            'doctor': doctor,
            'active_tab': 'schedule'
        })

    def post(self, request, *args, **kwargs):
        doctor = get_doctor_profile(request)
        form = SlotGenerationForm(request.POST)

        if form.is_valid():
            slot_date = form.cleaned_data['date']
            start_t = form.cleaned_data['start_time']
            end_t = form.cleaned_data['end_time']
            duration = form.cleaned_data['slot_duration']

            # Check if doctor is on leave
            on_leave = DoctorLeave.objects.filter(
                doctor=doctor, status='APPROVED',
                start_date__lte=slot_date, end_date__gte=slot_date
            ).exists()

            if on_leave:
                messages.error(request, f"You are on leave on {slot_date}. Cannot generate slots.")
                return redirect('availability_schedule')

            start_dt = datetime.combine(slot_date, start_t)
            end_dt = datetime.combine(slot_date, end_t)
            delta = timedelta(minutes=duration)

            current_dt = start_dt
            slots_created = 0

            while current_dt + delta <= end_dt:
                slot_start = current_dt.time()
                slot_end = (current_dt + delta).time()

                exists = AvailabilitySlot.objects.filter(
                    doctor=doctor, date=slot_date, start_time=slot_start
                ).exists()

                if not exists:
                    AvailabilitySlot.objects.create(
                        doctor=doctor, date=slot_date,
                        start_time=slot_start, end_time=slot_end
                    )
                    slots_created += 1

                current_dt += delta

            if slots_created > 0:
                messages.success(request, f"Generated {slots_created} slots for {slot_date}.")
            else:
                messages.warning(request, "No new slots generated. Slots may already exist.")
        else:
            messages.error(request, "Invalid slot generation configurations.")

        return redirect('availability_schedule')


class DeleteSlotView(DoctorRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        doctor = get_doctor_profile(request)
        slot = get_object_or_404(AvailabilitySlot, id=pk, doctor=doctor)
        if slot.is_booked:
            messages.error(request, "Cannot delete slot with active bookings.")
        else:
            slot.delete()
            messages.success(request, "Slot deleted successfully.")
        return redirect('availability_schedule')


# ─────────────────────────────────────────────────────────────────────────────
# 4. Leave Management
# ─────────────────────────────────────────────────────────────────────────────

class LeaveManagementView(DoctorRequiredMixin, View):
    template_name = 'doctor/leave.html'

    def get(self, request, *args, **kwargs):
        doctor = get_doctor_profile(request)
        leaves = DoctorLeave.objects.filter(doctor=doctor)
        return render(request, self.template_name, {
            'leaves': leaves,
            'form': LeaveForm(),
            'doctor': doctor,
            'active_tab': 'leave'
        })

    def post(self, request, *args, **kwargs):
        doctor = get_doctor_profile(request)
        form = LeaveForm(request.POST)

        if form.is_valid():
            leave = form.save(commit=False)
            leave.doctor = doctor
            leave.save()

            # Optional/Integration check: block/cancel any slots in leave date range
            booked_count = AvailabilitySlot.objects.filter(
                doctor=doctor, date__range=(leave.start_date, leave.end_date), is_booked=True
            ).count()

            # Auto release/delete unbooked slots in that range
            AvailabilitySlot.objects.filter(
                doctor=doctor, date__range=(leave.start_date, leave.end_date), is_booked=False
            ).delete()

            if booked_count > 0:
                messages.warning(request, f"Leave scheduled. Note: There are {booked_count} booked appointments during this time. Please contact support or cancel them.")
            else:
                messages.success(request, f"Leave applied from {leave.start_date} to {leave.end_date} successfully.")

            return redirect('leave_management')
        
        leaves = DoctorLeave.objects.filter(doctor=doctor)
        return render(request, self.template_name, {
            'leaves': leaves,
            'form': form,
            'doctor': doctor,
            'active_tab': 'leave'
        })


class DeleteLeaveView(DoctorRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        doctor = get_doctor_profile(request)
        leave = get_object_or_404(DoctorLeave, id=pk, doctor=doctor)
        leave.delete()
        messages.success(request, "Leave entry cancelled.")
        return redirect('leave_management')


# ─────────────────────────────────────────────────────────────────────────────
# 5. Appointment Management
# ─────────────────────────────────────────────────────────────────────────────

class AppointmentManagementView(DoctorRequiredMixin, TemplateView):
    template_name = 'doctor/appointments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = get_doctor_profile(self.request)
        appointments = Appointment.objects.filter(doctor=doctor)

        context['pending'] = appointments.filter(status='PENDING').order_by('slot__date', 'slot__start_time')
        context['upcoming'] = appointments.filter(status='CONFIRMED').order_by('slot__date', 'slot__start_time')
        context['past'] = appointments.filter(Q(status='COMPLETED') | Q(status='CANCELLED')).order_by('-slot__date')
        context['doctor'] = doctor
        context['active_tab'] = 'appointments'
        return context


class AppointmentActionView(DoctorRequiredMixin, View):
    def post(self, request, pk, action, *args, **kwargs):
        doctor = get_doctor_profile(request)
        appointment = get_object_or_404(Appointment, id=pk, doctor=doctor)

        if action == 'confirm' and appointment.status == 'PENDING':
            # Check payment details (should be paid before confirm, or direct cash confirmation)
            appointment.status = 'CONFIRMED'
            appointment.save()
            messages.success(request, f"Appointment #{appointment.id} confirmed!")
        elif action == 'complete' and appointment.status == 'CONFIRMED':
            appointment.status = 'COMPLETED'
            appointment.save()
            messages.success(request, f"Appointment #{appointment.id} marked as completed.")
        elif action == 'cancel':
            # Release slot
            slot = appointment.slot
            slot.is_booked = False
            slot.save()

            appointment.status = 'CANCELLED'
            appointment.save()
            messages.warning(request, f"Appointment #{appointment.id} cancelled.")

        return redirect('appointment_management')


# ─────────────────────────────────────────────────────────────────────────────
# 6. Patient History Directory
# ─────────────────────────────────────────────────────────────────────────────

class PatientHistoryView(DoctorRequiredMixin, TemplateView):
    template_name = 'doctor/patient_history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = get_doctor_profile(self.request)

        # Get all patients consulted
        consulted_patients = PatientProfile.objects.filter(
            appointments__doctor=doctor
        ).annotate(
            total_consultations=Count('appointments', filter=Q(appointments__doctor=doctor)),
            last_consultation=Sum('appointments__slot__date')  # Sort helper
        ).order_by('-last_consultation')

        context['patients'] = consulted_patients
        context['doctor'] = doctor
        context['active_tab'] = 'patients'
        return context


class PatientDetailView(DoctorRequiredMixin, DetailView):
    model = PatientProfile
    template_name = 'doctor/patient_detail.html'
    context_object_name = 'patient_profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = get_doctor_profile(self.request)
        patient = self.object

        # Patient appointments with THIS doctor
        context['appointments'] = Appointment.objects.filter(
            doctor=doctor, patient=patient
        ).order_by('-slot__date')

        # Uploaded medical reports
        context['reports'] = MedicalReport.objects.filter(patient=patient)

        # Prescriptions written by this doctor
        context['prescriptions'] = Prescription.objects.filter(
            doctor=doctor, patient=patient
        ).order_by('-created_at')

        context['doctor'] = doctor
        context['active_tab'] = 'patients'
        return context


# ─────────────────────────────────────────────────────────────────────────────
# 7. Write Prescription
# ─────────────────────────────────────────────────────────────────────────────

class WritePrescriptionView(DoctorRequiredMixin, View):
    template_name = 'doctor/write_prescription.html'

    def get(self, request, appointment_id, *args, **kwargs):
        doctor = get_doctor_profile(request)
        appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)

        try:
            prescription = appointment.prescription
            form = PrescriptionForm(instance=prescription)
        except Prescription.DoesNotExist:
            form = PrescriptionForm()

        return render(request, self.template_name, {
            'form': form,
            'appointment': appointment,
            'doctor': doctor,
            'active_tab': 'appointments'
        })

    def post(self, request, appointment_id, *args, **kwargs):
        doctor = get_doctor_profile(request)
        appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)

        try:
            prescription = appointment.prescription
            form = PrescriptionForm(request.POST, instance=prescription)
        except Prescription.DoesNotExist:
            prescription = None
            form = PrescriptionForm(request.POST)

        if form.is_valid():
            presc = form.save(commit=False)
            if not prescription:
                presc.appointment = appointment
                presc.doctor = doctor
                presc.patient = appointment.patient
            presc.save()

            if appointment.status != 'COMPLETED':
                appointment.status = 'COMPLETED'
                appointment.save()

            messages.success(request, "Prescription saved and sent successfully!")
            return redirect('appointment_management')

        return render(request, self.template_name, {
            'form': form,
            'appointment': appointment,
            'doctor': doctor,
            'active_tab': 'appointments'
        })


# ─────────────────────────────────────────────────────────────────────────────
# 8. Video Consultation
# ─────────────────────────────────────────────────────────────────────────────

class VideoConsultationView(DoctorRequiredMixin, TemplateView):
    template_name = 'doctor/video.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = get_doctor_profile(self.request)
        appointment_id = self.kwargs.get('appointment_id')
        appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)

        context['appointment'] = appointment
        context['doctor'] = doctor
        context['active_tab'] = 'appointments'
        return context


# ─────────────────────────────────────────────────────────────────────────────
# 9. Private Chat System
# ─────────────────────────────────────────────────────────────────────────────

class ChatInboxView(DoctorRequiredMixin, TemplateView):
    template_name = 'doctor/chat_inbox.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = get_doctor_profile(self.request)

        # Get list of patients who have consulted this doctor
        patients = PatientProfile.objects.filter(appointments__doctor=doctor).distinct()
        
        # Add last message context helper
        chat_list = []
        for p in patients:
            last_msg = ChatMessage.objects.filter(
                Q(sender=self.request.user, receiver=p.user) |
                Q(sender=p.user, receiver=self.request.user)
            ).order_by('-timestamp').first()

            unread_count = ChatMessage.objects.filter(
                sender=p.user, receiver=self.request.user, is_read=False
            ).count()

            chat_list.append({
                'patient': p,
                'last_msg': last_msg,
                'unread_count': unread_count
            })

        context['chat_list'] = chat_list
        context['doctor'] = doctor
        context['active_tab'] = 'chat'
        return context


class ChatRoomView(DoctorRequiredMixin, View):
    template_name = 'doctor/chat_room.html'

    def get(self, request, patient_id, *args, **kwargs):
        doctor = get_doctor_profile(request)
        patient_user = get_object_or_404(User, id=patient_id, role='PATIENT')

        # Mark incoming messages as read
        ChatMessage.objects.filter(sender=patient_user, receiver=request.user, is_read=False).update(is_read=True)

        messages_qs = ChatMessage.objects.filter(
            Q(sender=request.user, receiver=patient_user) |
            Q(sender=patient_user, receiver=request.user)
        ).order_by('timestamp')

        return render(request, self.template_name, {
            'patient_user': patient_user,
            'chat_messages': messages_qs,
            'doctor': doctor,
            'active_tab': 'chat'
        })

    def post(self, request, patient_id, *args, **kwargs):
        patient_user = get_object_or_404(User, id=patient_id, role='PATIENT')
        message_text = request.POST.get('message', '').strip()

        if message_text:
            ChatMessage.objects.create(
                sender=request.user,
                receiver=patient_user,
                message=message_text
            )
        return redirect('doctor_chat_room', patient_id=patient_id)


# ─────────────────────────────────────────────────────────────────────────────
# 10. Revenue Dashboard
# ─────────────────────────────────────────────────────────────────────────────

class RevenueDashboardView(DoctorRequiredMixin, TemplateView):
    template_name = 'doctor/revenue.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = get_doctor_profile(self.request)

        payments = Payment.objects.filter(
            appointment__doctor=doctor, status='SUCCESS'
        ).order_by('-timestamp')

        # Calculate metrics
        total_revenue = payments.aggregate(total=Sum('amount'))['total'] or 0
        this_month = timezone.now().month
        this_month_revenue = payments.filter(
            timestamp__month=this_month
        ).aggregate(total=Sum('amount'))['total'] or 0

        # Group by month
        monthly_earnings = payments.annotate(
            month=TruncMonth('timestamp')
        ).values('month').annotate(
            earnings=Sum('amount'), count=Count('id')
        ).order_by('-month')

        context['payments'] = payments[:15]
        context['total_revenue'] = total_revenue
        context['this_month_revenue'] = this_month_revenue
        context['monthly_earnings'] = monthly_earnings
        context['doctor'] = doctor
        context['active_tab'] = 'revenue'
        return context


# ─────────────────────────────────────────────────────────────────────────────
# 11. Payment History
# ─────────────────────────────────────────────────────────────────────────────

class PaymentHistoryView(DoctorRequiredMixin, TemplateView):
    template_name = 'doctor/payment_history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = get_doctor_profile(self.request)

        context['payments'] = Payment.objects.filter(
            appointment__doctor=doctor
        ).order_by('-timestamp')

        context['doctor'] = doctor
        context['active_tab'] = 'payments'
        return context


# ─────────────────────────────────────────────────────────────────────────────
# 12. Analytics & Visuals
# ─────────────────────────────────────────────────────────────────────────────

class AnalyticsView(DoctorRequiredMixin, TemplateView):
    template_name = 'doctor/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        doctor = get_doctor_profile(self.request)

        # Basic Stats
        appointments = Appointment.objects.filter(doctor=doctor)
        completed = appointments.filter(status='COMPLETED')
        cancelled = appointments.filter(status='CANCELLED')

        context['consultations_count'] = completed.count()
        context['cancellations_count'] = cancelled.count()

        # Demographics breakdown by gender
        gender_data = completed.values('patient__gender').annotate(
            count=Count('id')
        )
        context['gender_stats'] = gender_data

        # Weekdays stats
        weekday_stats = completed.values('slot__date__week_day').annotate(
            count=Count('id')
        ).order_by('slot__date__week_day')
        context['weekday_stats'] = weekday_stats

        context['doctor'] = doctor
        context['active_tab'] = 'analytics'
        return context
