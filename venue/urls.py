from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from venues.views import PropertyViewSet, ServiceViewSet, BookingViewSet, StatsViewSet

# API Router
router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'stats', StatsViewSet, basename='stats')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]

# Media faýllar üçin (DEBUG=True wagtynda)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)