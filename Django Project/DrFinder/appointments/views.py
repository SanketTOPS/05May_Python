from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Sum, Count
from datetime import datetime, timedelta, time

from accounts.models import DoctorProfile, PatientProfile, User
from .models import AvailabilitySlot, Appointment, Prescription
from payments.models import Payment
from .forms import SlotGenerationForm, PrescriptionForm

class PatientRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'PATIENT'

class DoctorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'DOCTOR'

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.role == 'ADMIN' or self.request.user.is_superuser)


class HomeView(TemplateView):
    template_name = 'appointments/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['doctors'] = DoctorProfile.objects.filter(status='APPROVED').order_by('-experience_years')[:4]
        context['specializations'] = DoctorProfile.SPECIALIZATION_CHOICES
        context['stats'] = {
            'doctors_count': DoctorProfile.objects.filter(status='APPROVED').count(),
            'appointments_count': Appointment.objects.filter(status='CONFIRMED').count(),
            'patients_count': User.objects.filter(role='PATIENT').count(),
        }
        return context


class PatientDashboardView(PatientRequiredMixin, TemplateView):
    template_name = 'appointments/patient_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient_profile = get_object_or_404(PatientProfile, user=self.request.user)
        
        # Get appointments
        appointments = Appointment.objects.filter(patient=patient_profile)
        context['upcoming_appointments'] = appointments.filter(
            Q(status='CONFIRMED') | Q(status='PENDING'),
            slot__date__gte=timezone.now().date()
        ).order_by('slot__date', 'slot__start_time')
        
        context['past_appointments'] = appointments.filter(
            Q(status='COMPLETED') | Q(status='CANCELLED') | Q(slot__date__lt=timezone.now().date())
        ).order_by('-slot__date', '-slot__start_time')

        # Get prescriptions
        context['prescriptions'] = Prescription.objects.filter(patient=patient_profile).order_by('-created_at')
        
        return context

class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'appointments/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Analytics
        context['stats'] = {
            'total_doctors': DoctorProfile.objects.count(),
            'total_patients': User.objects.filter(role='PATIENT').count(),
            'total_appointments': Appointment.objects.count(),
            'total_revenue': Payment.objects.filter(status='SUCCESS').aggregate(sum_amount=Sum('amount'))['sum_amount'] or 0.00
        }
        
        context['pending_doctors'] = DoctorProfile.objects.filter(status='PENDING').order_by('user__date_joined')
        context['verified_doctors'] = DoctorProfile.objects.exclude(status='PENDING').order_by('user__first_name')
        context['all_appointments'] = Appointment.objects.all().order_by('-created_at')[:20]
        context['recent_payments'] = Payment.objects.all().order_by('-timestamp')[:20]
        
        return context


class DoctorSearchView(LoginRequiredMixin, ListView):
    model = DoctorProfile
    template_name = 'appointments/doctor_search.html'
    context_object_name = 'doctors'
    paginate_by = 6

    def get_queryset(self):
        queryset = DoctorProfile.objects.filter(status='APPROVED')
        
        query = self.request.GET.get('q')
        specialization = self.request.GET.get('specialization')
        min_fee = self.request.GET.get('min_fee')
        max_fee = self.request.GET.get('max_fee')

        if query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(hospital_name__icontains=query) |
                Q(bio__icontains=query)
            )
            
        if specialization and specialization != 'ALL':
            queryset = queryset.filter(specialization=specialization)
            
        if min_fee:
            queryset = queryset.filter(consultation_fee__gte=min_fee)
            
        if max_fee:
            queryset = queryset.filter(consultation_fee__lte=max_fee)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['specializations'] = DoctorProfile.SPECIALIZATION_CHOICES
        context['selected_specialization'] = self.request.GET.get('specialization', 'ALL')
        context['q'] = self.request.GET.get('q', '')
        context['min_fee'] = self.request.GET.get('min_fee', '')
        context['max_fee'] = self.request.GET.get('max_fee', '')
        return context


class DoctorDetailView(LoginRequiredMixin, DetailView):
    model = DoctorProfile
    template_name = 'appointments/doctor_detail.html'
    context_object_name = 'doctor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch active slots for this doctor starting today
        context['available_slots'] = AvailabilitySlot.objects.filter(
            doctor=self.object,
            date__gte=timezone.now().date(),
            is_booked=False
        ).order_by('date', 'start_time')
        return context


class BookAppointmentView(PatientRequiredMixin, View):
    def post(self, request, slot_id, *args, **kwargs):
        slot = get_object_or_404(AvailabilitySlot, id=slot_id, is_booked=False)
        patient_profile = get_object_or_404(PatientProfile, user=request.user)
        
        symptoms = request.POST.get('symptoms', '').strip()
        notes = request.POST.get('notes', '').strip()
        
        if not symptoms:
            messages.error(request, "Please enter your symptoms before booking.")
            return redirect('doctor_detail', pk=slot.doctor.pk)
        
        # Check if slot date is past
        if slot.date < timezone.now().date():
            messages.error(request, "This slot has expired.")
            return redirect('doctor_detail', pk=slot.doctor.pk)

        # Reserve the slot and create appointment in PENDING status
        slot.is_booked = True
        slot.save()
        
        appointment = Appointment.objects.create(
            patient=patient_profile,
            doctor=slot.doctor,
            slot=slot,
            status='PENDING', # Pending payment
            symptoms=symptoms,
            notes=notes
        )
        
        # Redirect to payment checkout
        return redirect('payment_checkout', appointment_id=appointment.id)


class AppointmentActionView(LoginRequiredMixin, View):
    def post(self, request, appointment_id, action, *args, **kwargs):
        appointment = get_object_or_404(Appointment, id=appointment_id)
        user = request.user
        
        # Access control
        is_doctor = (user.role == 'DOCTOR' and appointment.doctor.user == user)
        is_patient = (user.role == 'PATIENT' and appointment.patient.user == user)
        is_admin = (user.role == 'ADMIN' or user.is_superuser)
        
        if not (is_doctor or is_patient or is_admin):
            messages.error(request, "Unauthorized action.")
            return redirect('dashboard')
            
        if action == 'accept' and is_doctor:
            if appointment.status == 'PENDING':
                messages.error(request, "Cannot accept an appointment without payment completion.")
            else:
                appointment.status = 'CONFIRMED'
                messages.success(request, "Appointment confirmed successfully!")
                appointment.save()
                
        elif action == 'complete' and is_doctor:
            appointment.status = 'COMPLETED'
            messages.success(request, "Appointment marked as completed. You can now issue a prescription.")
            appointment.save()
            
        elif action == 'cancel':
            # Release slot
            slot = appointment.slot
            slot.is_booked = False
            slot.save()
            
            appointment.status = 'CANCELLED'
            messages.warning(request, "Appointment cancelled successfully.")
            appointment.save()
            
        return redirect('dashboard')


