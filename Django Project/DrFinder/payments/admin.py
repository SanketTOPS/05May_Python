from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'appointment', 'amount', 'status', 'payment_method', 'timestamp')
    list_filter = ('status', 'payment_method', 'timestamp')
    search_fields = ('transaction_id',)
    readonly_fields = ('timestamp',)
