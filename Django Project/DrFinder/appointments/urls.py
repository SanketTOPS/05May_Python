from django.urls import path
from .views import (
    AdminDashboardView,
    DoctorSearchView,
    DoctorDetailView,
    BookAppointmentView,
    AppointmentActionView,
)

urlpatterns = [
    path('dashboard/admin/', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('search/', DoctorSearchView.as_view(), name='doctor_search'),
    path('doctor/<int:pk>/', DoctorDetailView.as_view(), name='doctor_detail'),
    path('book/<int:slot_id>/', BookAppointmentView.as_view(), name='book_appointment'),
    path('action/<int:appointment_id>/<str:action>/', AppointmentActionView.as_view(), name='appointment_action'),
]

