from django.urls import path
from .views import (
    PatientDashboardView,
    PatientProfileView,
    MedicalHistoryView,
    UploadReportsView,
    DeleteReportView,
    FamilyMembersView,
    DeleteFamilyMemberView,
    InsuranceView,
    FavoriteDoctorsView,
    ToggleFavoriteView,
    AppointmentHistoryView,
    UpcomingAppointmentsView,
    CancelledAppointmentsView,
    PrescriptionsView,
    PrintPrescriptionView,
    InvoicesView,
    WalletView,
    NotificationsView,
    ReviewsView,
    HelpCenterView,
    SupportTicketsView,
    SupportTicketDetailView,
)

urlpatterns = [
    # ── Dashboard ─────────────────────────────────────────────────────────────
    path('dashboard/', PatientDashboardView.as_view(), name='patient_dashboard'),

    # ── Profile ───────────────────────────────────────────────────────────────
    path('profile/', PatientProfileView.as_view(), name='patient_profile'),

    # ── Medical History ───────────────────────────────────────────────────────
    path('medical-history/', MedicalHistoryView.as_view(), name='medical_history'),

    # ── Upload Reports ────────────────────────────────────────────────────────
    path('reports/', UploadReportsView.as_view(), name='upload_reports'),
    path('reports/<int:pk>/delete/', DeleteReportView.as_view(), name='delete_report'),

    # ── Family Members ────────────────────────────────────────────────────────
    path('family/', FamilyMembersView.as_view(), name='family_members'),
    path('family/<int:pk>/delete/', DeleteFamilyMemberView.as_view(), name='delete_family_member'),

    # ── Insurance ─────────────────────────────────────────────────────────────
    path('insurance/', InsuranceView.as_view(), name='insurance_info'),

    # ── Favorite Doctors ──────────────────────────────────────────────────────
    path('favorites/', FavoriteDoctorsView.as_view(), name='favorite_doctors'),
    path('favorites/toggle/<int:doctor_id>/', ToggleFavoriteView.as_view(), name='toggle_favorite'),

    # ── Appointments ──────────────────────────────────────────────────────────
    path('appointments/history/', AppointmentHistoryView.as_view(), name='appointment_history'),
    path('appointments/upcoming/', UpcomingAppointmentsView.as_view(), name='upcoming_appointments_page'),
    path('appointments/cancelled/', CancelledAppointmentsView.as_view(), name='cancelled_appointments'),

    # ── Prescriptions ─────────────────────────────────────────────────────────
    path('prescriptions/', PrescriptionsView.as_view(), name='download_prescriptions'),
    path('prescriptions/<int:pk>/print/', PrintPrescriptionView.as_view(), name='print_prescription'),

    # ── Invoices ──────────────────────────────────────────────────────────────
    path('invoices/', InvoicesView.as_view(), name='patient_invoices'),

    # ── Wallet ────────────────────────────────────────────────────────────────
    path('wallet/', WalletView.as_view(), name='patient_wallet'),

    # ── Notifications ─────────────────────────────────────────────────────────
    path('notifications/', NotificationsView.as_view(), name='patient_notifications'),

    # ── Reviews & Ratings ─────────────────────────────────────────────────────
    path('reviews/', ReviewsView.as_view(), name='patient_reviews'),

    # ── Help Center ───────────────────────────────────────────────────────────
    path('help/', HelpCenterView.as_view(), name='help_center'),

    # ── Support Tickets ───────────────────────────────────────────────────────
    path('support/', SupportTicketsView.as_view(), name='support_tickets'),
    path('support/<int:pk>/', SupportTicketDetailView.as_view(), name='support_ticket_detail'),
]
