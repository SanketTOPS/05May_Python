from django.contrib import admin
from .models import (
    DoctorEducation, DoctorExperience, DoctorAward,
    DoctorCertificate, DoctorLeave, ChatMessage
)

@admin.register(DoctorEducation)
class DoctorEducationAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'degree', 'institute', 'year_of_completion')
    list_filter = ('degree',)
    search_fields = ('doctor__user__first_name', 'institute')

@admin.register(DoctorExperience)
class DoctorExperienceAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'designation', 'hospital_name', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current',)
    search_fields = ('doctor__user__first_name', 'hospital_name')

@admin.register(DoctorAward)
class DoctorAwardAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'title', 'year')
    search_fields = ('doctor__user__first_name', 'title')

@admin.register(DoctorCertificate)
class DoctorCertificateAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'title', 'issued_by', 'uploaded_at')
    search_fields = ('doctor__user__first_name', 'title')

@admin.register(DoctorLeave)
class DoctorLeaveAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'start_date', 'end_date', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('doctor__user__first_name',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'message', 'is_read', 'timestamp')
    list_filter = ('is_read',)
    search_fields = ('sender__username', 'receiver__username', 'message')
