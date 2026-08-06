from django import forms
from django.utils import timezone
from .models import AvailabilitySlot, Prescription
from accounts.forms import TailwindFormMixin

class SlotGenerationForm(TailwindFormMixin, forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date(),
        help_text="Select the date you want to generate slots for"
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        initial="09:00",
        help_text="Consultation start time"
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        initial="17:00",
        help_text="Consultation end time"
    )
    slot_duration = forms.IntegerField(
        initial=30,
        min_value=10,
        max_value=120,
        help_text="Duration per appointment in minutes"
    )

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date < timezone.now().date():
            raise forms.ValidationError("You cannot generate slots for a past date.")
        return date

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')
        if start and end and start >= end:
            self.add_error('end_time', "End time must be after start time.")
        return cleaned_data


class PrescriptionForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medicines', 'instructions', 'follow_up_date']
        widgets = {
            'medicines': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Enter medicines in format: \n1. Paracetamol 500mg - 1-0-1 - After Food - 5 Days\n2. Amoxicillin 250mg - 1-1-1 - Before Food - 7 Days'
            }),
            'instructions': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'General instructions (e.g., bed rest, drink plenty of water)'
            }),
            'follow_up_date': forms.DateInput(attrs={'type': 'date'}),
        }
