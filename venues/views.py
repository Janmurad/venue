from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Venue
from .serializers import VenueListSerializer, VenueDetailSerializer
from .filters import VenueFilter

class VenueListView(generics.ListAPIView):
    """
    List all active venues with filtering and pagination support.
    
    Filters:
    - date: Show only venues available on specific date (YYYY-MM-DD)
    - service_type: Filter by package type (standard/gold/vip)
    - capacity_min: Minimum capacity required
    - price_max: Maximum price filter
    """
    
    queryset = Venue.objects.filter(status='active').prefetch_related('images', 'packages')
    serializer_class = VenueListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = VenueFilter
    search_fields = ['name_tm', 'name_ru', 'address_tm', 'address_ru']
    ordering_fields = ['name_tm', 'base_price', 'capacity_max']
    ordering = ['name_tm']
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter venues available on specific date (YYYY-MM-DD)'
            ),
            OpenApiParameter(
                name='service_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by package type',
                enum=['standard', 'gold', 'vip']
            ),
            OpenApiParameter(
                name='capacity_min',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Minimum capacity required'
            ),
            OpenApiParameter(
                name='price_max',
                type=OpenApiTypes.NUMBER,
                location=OpenApiParameter.QUERY,
                description='Maximum price filter'
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search in venue names and addresses'
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class VenueDetailView(generics.RetrieveAPIView):
    """
    Retrieve detailed information about a specific venue including:
    - Basic information
    - Image gallery
    - Available packages
    - Availability calendar for next 12 months
    """
    
    queryset = Venue.objects.filter(status='active').prefetch_related(
        'images', 'packages', 'availability_blocks'
    )
    serializer_class = VenueDetailSerializer
    lookup_field = 'id'

@api_view(['GET'])
def api_health(request):
    """Simple health check endpoint"""
    return Response({'status': 'healthy', 'version': '1.0.0'})