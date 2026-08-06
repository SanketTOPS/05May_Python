from django.contrib import admin
from .models import AvailabilitySlot, Appointment, Prescription


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'start_time', 'end_time', 'is_booked')
    list_filter = ('is_booked', 'date')
    search_fields = ('doctor__user__first_name', 'doctor__user__last_name')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'slot', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('patient__user__first_name', 'doctor__user__first_name')
    readonly_fields = ('created_at',)


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'doctor', 'patient', 'follow_up_date', 'created_at')
    search_fields = ('doctor__user__first_name', 'patient__user__first_name')
    readonly_fields = ('created_at',)
