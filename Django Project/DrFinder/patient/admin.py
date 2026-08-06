from django.contrib import admin
from .models import (
    MedicalReport, FamilyMember, InsuranceInfo, FavoriteDoctor,
    Wallet, WalletTransaction, Notification, DoctorReview,
    SupportTicket, SupportMessage
)


@admin.register(MedicalReport)
class MedicalReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'patient', 'report_date', 'uploaded_at')
    list_filter = ('report_type', 'report_date')
    search_fields = ('title', 'patient__user__first_name', 'patient__user__last_name')


@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'relation', 'patient', 'gender', 'phone')
    list_filter = ('relation', 'gender')
    search_fields = ('full_name', 'patient__user__first_name')


@admin.register(InsuranceInfo)
class InsuranceInfoAdmin(admin.ModelAdmin):
    list_display = ('provider_name', 'policy_number', 'plan_type', 'patient', 'expiry_date')
    list_filter = ('plan_type',)
    search_fields = ('provider_name', 'policy_number', 'patient__user__first_name')


@admin.register(FavoriteDoctor)
class FavoriteDoctorAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'added_at')
    search_fields = ('patient__user__first_name', 'doctor__user__first_name')


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('patient', 'balance', 'updated_at')
    search_fields = ('patient__user__first_name',)


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'amount', 'description', 'created_at')
    list_filter = ('transaction_type',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('title', 'patient__user__first_name')


@admin.register(DoctorReview)
class DoctorReviewAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'rating', 'is_anonymous', 'created_at')
    list_filter = ('rating', 'is_anonymous')
    search_fields = ('patient__user__first_name', 'doctor__user__first_name')


class SupportMessageInline(admin.TabularInline):
    model = SupportMessage
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'patient', 'category', 'priority', 'status', 'created_at')
    list_filter = ('status', 'category', 'priority')
    search_fields = ('subject', 'patient__user__first_name')
    inlines = [SupportMessageInline]
