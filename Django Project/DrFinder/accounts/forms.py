from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from .models import User, PatientProfile, DoctorProfile

class TailwindFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Apply standard Tailwind CSS classes to all fields
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"mt-1 block w-full rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-gray-900 shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 sm:text-sm transition duration-150 {existing_classes}"


class PatientRegistrationForm(TailwindFormMixin, forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    profile_picture = forms.ImageField(required=False)
    
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    gender = forms.ChoiceField(choices=PatientProfile.GENDER_CHOICES, required=False)
    blood_group = forms.CharField(max_length=5, required=False)
    medical_history = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'profile_picture']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = 'PATIENT'
        if commit:
            user.save()
            PatientProfile.objects.create(
                user=user,
                date_of_birth=self.cleaned_data.get('date_of_birth'),
                gender=self.cleaned_data.get('gender'),
                blood_group=self.cleaned_data.get('blood_group'),
                medical_history=self.cleaned_data.get('medical_history')
            )
        return user


class DoctorRegistrationForm(TailwindFormMixin, forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    profile_picture = forms.ImageField(required=True, help_text="Upload your medical avatar/profile picture")
    
    specialization = forms.ChoiceField(choices=DoctorProfile.SPECIALIZATION_CHOICES, initial='GENERAL')
    qualification = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={'placeholder': 'e.g., MBBS, MD, DM Cardiology'}))
    experience_years = forms.IntegerField(min_value=0, required=True)
    consultation_fee = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    hospital_name = forms.CharField(max_length=200, required=True)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'profile_picture']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = 'DOCTOR'
        if commit:
            user.save()
            DoctorProfile.objects.create(
                user=user,
                specialization=self.cleaned_data.get('specialization'),
                qualification=self.cleaned_data.get('qualification'),
                experience_years=self.cleaned_data.get('experience_years'),
                consultation_fee=self.cleaned_data.get('consultation_fee'),
                bio=self.cleaned_data.get('bio'),
                hospital_name=self.cleaned_data.get('hospital_name'),
                address=self.cleaned_data.get('address'),
                status='PENDING' # Pending Admin Verification
            )
        return user


class UserUpdateForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'profile_picture']


class PatientProfileUpdateForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = ['date_of_birth', 'gender', 'blood_group', 'medical_history']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'medical_history': forms.Textarea(attrs={'rows': 4}),
        }


class DoctorProfileUpdateForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['specialization', 'qualification', 'experience_years', 'consultation_fee', 'bio', 'hospital_name', 'address']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }


# ─────────────────────────────────────────────────────────────────────────────
# OTP Verification Form
# ─────────────────────────────────────────────────────────────────────────────

class OTPVerifyForm(TailwindFormMixin, forms.Form):
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        label="6-Digit OTP",
        widget=forms.TextInput(attrs={
            'placeholder': '••••••',
            'maxlength': '6',
            'inputmode': 'numeric',
            'autocomplete': 'one-time-code',
            'class': 'text-center text-2xl font-mono tracking-widest letter-spacing-4',
        })
    )

    def clean_otp_code(self):
        code = self.cleaned_data.get('otp_code', '').strip()
        if not code.isdigit():
            raise forms.ValidationError("OTP must contain only digits.")
        return code


# ─────────────────────────────────────────────────────────────────────────────
# Forgot Password Form
# ─────────────────────────────────────────────────────────────────────────────

class ForgotPasswordForm(TailwindFormMixin, forms.Form):
    email = forms.EmailField(
        label="Registered Email Address",
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not User.objects.filter(email=email).exists():
            # We deliberately do not tell the user if email exists for security
            # but we raise internally to prevent sending — handled in view
            pass
        return email


# ─────────────────────────────────────────────────────────────────────────────
# Reset Password Form (after OTP)
# ─────────────────────────────────────────────────────────────────────────────

class ResetPasswordForm(TailwindFormMixin, forms.Form):
    otp_code = forms.CharField(
        max_length=6,
        min_length=6,
        label="OTP Code",
        widget=forms.TextInput(attrs={
            'placeholder': '6-digit OTP',
            'inputmode': 'numeric',
        })
    )
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter new password'}),
        min_length=8,
    )
    confirm_password = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Repeat new password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    def clean_otp_code(self):
        code = self.cleaned_data.get('otp_code', '').strip()
        if not code.isdigit():
            raise forms.ValidationError("OTP must contain only digits.")
        return code


# ─────────────────────────────────────────────────────────────────────────────
# Resend Verification Email Form
# ─────────────────────────────────────────────────────────────────────────────

class ResendVerificationForm(TailwindFormMixin, forms.Form):
    email = forms.EmailField(
        label="Your Email Address",
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'})
    )
