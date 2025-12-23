# API Router
from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet, ServiceViewSet, BookingViewSet, StatsViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'stats', StatsViewSet, basename='stats')
