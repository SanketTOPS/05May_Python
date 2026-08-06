from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from appointments.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('appointments/', include('appointments.urls')),
    path('payments/', include('payments.urls')),
    path('patient/', include('patient.urls')),
    path('doctor/', include('doctor.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
