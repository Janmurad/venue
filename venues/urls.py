from django.urls import path
from .views import VenueListView, VenueDetailView, api_health

urlpatterns = [
    path('health/', api_health, name='api-health'),
    path('venues/', VenueListView.as_view(), name='venue-list'),
    path('venues/<int:id>/', VenueDetailView.as_view(), name='venue-detail'),
]