from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from accounts.models import PatientProfile

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        user.role = 'PATIENT'
        user.is_email_verified = True
        user.save()
        
        # Ensure PatientProfile exists for the new Google user
        PatientProfile.objects.get_or_create(
            user=user,
            defaults={
                'gender': None,
                'blood_group': '',
                'medical_history': 'Registered via Google Login'
            }
        )
        return user
