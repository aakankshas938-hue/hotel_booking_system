from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

# Temporary view to test if Django is working
def test_view(request):
    return HttpResponse("🏨 Hotel Booking System is working!")

urlpatterns = [
    path('', test_view),  # Temporary root view
    path('', include('booking.urls')),  # Your booking app URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)