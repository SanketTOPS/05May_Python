from django import forms
from .models import (
    DoctorEducation, DoctorExperience, DoctorAward,
    DoctorCertificate, DoctorLeave, ChatMessage
)
from accounts.models import DoctorProfile
from appointments.models import AvailabilitySlot, Prescription


class DoctorProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-input'}))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = DoctorProfile
        fields = ['specialization', 'qualification', 'experience_years', 'consultation_fee', 'hospital_name', 'address', 'bio']
        widgets = {
            'specialization': forms.Select(attrs={'class': 'form-input'}),
            'qualification': forms.TextInput(attrs={'class': 'form-input'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-input', 'min': 0}),
            'hospital_name': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Write a brief description of yourself...'}),
        }


class EducationForm(forms.ModelForm):
    class Meta:
        model = DoctorEducation
        fields = ['degree', 'institute', 'year_of_completion']
        widgets = {
            'degree': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. MBBS, MD'}),
            'institute': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. AIIMS'}),
            'year_of_completion': forms.NumberInput(attrs={'class': 'form-input', 'min': 1950, 'max': 2100}),
        }


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = DoctorExperience
        fields = ['designation', 'hospital_name', 'start_date', 'end_date', 'is_current']
        widgets = {
            'designation': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Registrar'}),
            'hospital_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Apollo Hospital'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class AwardForm(forms.ModelForm):
    class Meta:
        model = DoctorAward
        fields = ['title', 'year', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Medical Excellence Award'}),
            'year': forms.NumberInput(attrs={'class': 'form-input', 'min': 1950, 'max': 2100}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
        }


class CertificateForm(forms.ModelForm):
    class Meta:
        model = DoctorCertificate
        fields = ['title', 'issued_by', 'certificate_file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Medical License'}),
            'issued_by': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Medical Council of India'}),
            'certificate_file': forms.FileInput(attrs={'class': 'form-input'}),
        }


class LeaveForm(forms.ModelForm):
    class Meta:
        model = DoctorLeave
        fields = ['start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'reason': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Describe the reason for leave...'}),
        }


class SlotGenerationForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}))
    slot_duration = forms.IntegerField(
        min_value=5, max_value=120, initial=30,
        widget=forms.NumberInput(attrs={'class': 'form-input'})
    )


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medicines', 'instructions', 'follow_up_date']
        widgets = {
            'medicines': forms.Textarea(attrs={'class': 'form-input', 'rows': 5, 'placeholder': 'Medicine Name - Dosage - Frequency - Duration...'}),
            'instructions': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'e.g. Take after food, drink plenty of water'}),
            'follow_up_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        }
