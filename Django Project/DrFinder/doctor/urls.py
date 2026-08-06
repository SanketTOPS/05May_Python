from django.urls import path
from .views import (
    DoctorDashboardView,
    DoctorProfileView,
    AvailabilityScheduleView,
    DeleteSlotView,
    LeaveManagementView,
    DeleteLeaveView,
    AppointmentManagementView,
    AppointmentActionView,
    PatientHistoryView,
    PatientDetailView,
    WritePrescriptionView,
    VideoConsultationView,
    ChatInboxView,
    ChatRoomView,
    RevenueDashboardView,
    PaymentHistoryView,
    AnalyticsView,
)

urlpatterns = [
    # ── Dashboard ─────────────────────────────────────────────────────────────
    path('dashboard/', DoctorDashboardView.as_view(), name='doctor_dashboard'),

    # ── Profile ───────────────────────────────────────────────────────────────
    path('profile/', DoctorProfileView.as_view(), name='doctor_profile'),

    # ── Schedule & Availability ──────────────────────────────────────────────
    path('schedule/', AvailabilityScheduleView.as_view(), name='availability_schedule'),
    path('slots/delete/<int:pk>/', DeleteSlotView.as_view(), name='doctor_delete_slot'),

    # ── Leaves ────────────────────────────────────────────────────────────────
    path('leaves/', LeaveManagementView.as_view(), name='leave_management'),
    path('leaves/delete/<int:pk>/', DeleteLeaveView.as_view(), name='delete_leave'),

    # ── Appointments ──────────────────────────────────────────────────────────
    path('appointments/', AppointmentManagementView.as_view(), name='appointment_management'),
    path('appointments/<int:pk>/action/<str:action>/', AppointmentActionView.as_view(), name='doctor_appointment_action'),

    # ── Patient History ───────────────────────────────────────────────────────
    path('patients/', PatientHistoryView.as_view(), name='patient_history'),
    path('patients/<int:pk>/', PatientDetailView.as_view(), name='patient_detail'),

    # ── Prescription ──────────────────────────────────────────────────────────
    path('prescription/write/<int:appointment_id>/', WritePrescriptionView.as_view(), name='doctor_write_prescription'),

    # ── Video Consultation ────────────────────────────────────────────────────
    path('video/<int:appointment_id>/', VideoConsultationView.as_view(), name='video_consultation'),

    # ── Chat System ───────────────────────────────────────────────────────────
    path('chat/', ChatInboxView.as_view(), name='doctor_chat_inbox'),
    path('chat/<int:patient_id>/', ChatRoomView.as_view(), name='doctor_chat_room'),

    # ── Revenue & Billing ─────────────────────────────────────────────────────
    path('revenue/', RevenueDashboardView.as_view(), name='revenue_dashboard'),
    path('payments/', PaymentHistoryView.as_view(), name='doctor_payment_history'),

    # ── Analytics ─────────────────────────────────────────────────────────────
    path('analytics/', AnalyticsView.as_view(), name='doctor_analytics'),
]
