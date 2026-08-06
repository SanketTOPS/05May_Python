from django import forms
from .models import (
    MedicalReport, FamilyMember, InsuranceInfo,
    DoctorReview, SupportTicket, SupportMessage, WalletTransaction
)
from accounts.models import PatientProfile, User


class MedicalHistoryForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['date_of_birth', 'gender', 'blood_group', 'medical_history']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'gender': forms.Select(attrs={'class': 'form-input'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. A+, B-, O+'}),
            'medical_history': forms.Textarea(attrs={'rows': 5, 'class': 'form-input', 'placeholder': 'List any chronic conditions, surgeries, or known allergies...'}),
        }


class MedicalReportForm(forms.ModelForm):
    class Meta:
        model = MedicalReport
        fields = ['title', 'report_type', 'report_date', 'report_file', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Blood CBC Report'}),
            'report_type': forms.Select(attrs={'class': 'form-input'}),
            'report_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'report_file': forms.FileInput(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-input', 'placeholder': 'Optional notes about this report...'}),
        }


class FamilyMemberForm(forms.ModelForm):
    class Meta:
        model = FamilyMember
        fields = ['full_name', 'relation', 'gender', 'date_of_birth', 'blood_group', 'phone', 'medical_notes']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full name'}),
            'relation': forms.Select(attrs={'class': 'form-input'}),
            'gender': forms.Select(attrs={'class': 'form-input'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'blood_group': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. A+'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone number'}),
            'medical_notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-input', 'placeholder': 'Known conditions, allergies...'}),
        }


class InsuranceForm(forms.ModelForm):
    class Meta:
        model = InsuranceInfo
        fields = ['provider_name', 'policy_number', 'plan_type', 'holder_name', 'coverage_amount', 'expiry_date', 'notes']
        widgets = {
            'provider_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Star Health Insurance'}),
            'policy_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Policy number'}),
            'plan_type': forms.Select(attrs={'class': 'form-input'}),
            'holder_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Policyholder full name'}),
            'coverage_amount': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Coverage amount in ₹'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-input', 'placeholder': 'Additional notes...'}),
        }


class DoctorReviewForm(forms.ModelForm):
    class Meta:
        model = DoctorReview
        fields = ['rating', 'review_text', 'is_anonymous']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'star-radio'}),
            'review_text': forms.Textarea(attrs={'rows': 4, 'class': 'form-input', 'placeholder': 'Share your experience with this doctor...'}),
            'is_anonymous': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class SupportTicketForm(forms.ModelForm):
    initial_message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'class': 'form-input', 'placeholder': 'Describe your issue in detail...'}),
        label='Describe your issue'
    )

    class Meta:
        model = SupportTicket
        fields = ['subject', 'category', 'priority', 'initial_message']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Brief subject of your issue'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'priority': forms.Select(attrs={'class': 'form-input'}),
        }


class SupportReplyForm(forms.ModelForm):
    class Meta:
        model = SupportMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'class': 'form-input', 'placeholder': 'Type your reply...'}),
        }


class WalletTopUpForm(forms.Form):
    AMOUNT_CHOICES = [
        (500, '₹500'),
        (1000, '₹1,000'),
        (2000, '₹2,000'),
        (5000, '₹5,000'),
    ]
    amount = forms.ChoiceField(choices=AMOUNT_CHOICES, widget=forms.RadioSelect(attrs={'class': 'amount-radio'}))
    custom_amount = forms.DecimalField(
        required=False,
        min_value=100,
        max_value=50000,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Or enter custom amount (min ₹100)'})
    )

    def clean(self):
        cleaned_data = super().clean()
        custom = cleaned_data.get('custom_amount')
        if custom:
            cleaned_data['final_amount'] = custom
        else:
            cleaned_data['final_amount'] = int(cleaned_data.get('amount', 500))
        return cleaned_data
