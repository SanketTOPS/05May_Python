from django.urls import path
from .views import PaymentCheckoutView, RazorpayCallbackView, PaymentReceiptView

urlpatterns = [
    path('checkout/<int:appointment_id>/', PaymentCheckoutView.as_view(), name='payment_checkout'),
    path('razorpay-callback/<int:appointment_id>/', RazorpayCallbackView.as_view(), name='razorpay_callback'),
    path('receipt/<int:payment_id>/', PaymentReceiptView.as_view(), name='payment_receipt'),
]
