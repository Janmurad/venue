import django_filters
from django.db.models import Q
from .models import Venue, Package
from datetime import date

class VenueFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(method='filter_by_date', label='Available Date')
    service_type = django_filters.ChoiceFilter(
        choices=Package.PACKAGE_TYPES,
        method='filter_by_service_type',
        label='Service Type'
    )
    capacity_min = django_filters.NumberFilter(
        field_name='capacity_max',
        lookup_expr='gte',
        label='Minimum Capacity Required'
    )
    price_max = django_filters.NumberFilter(method='filter_by_max_price', label='Maximum Price')
    
    class Meta:
        model = Venue
        fields = ['status']
    
    def filter_by_date(self, queryset, name, value):
        if not value:
            return queryset
        
        # Exclude venues that are blocked on the requested date
        blocked_venue_ids = queryset.filter(
            availability_blocks__date=value,
            availability_blocks__is_closed=True
        ).values_list('id', flat=True)
        
        return queryset.exclude(id__in=blocked_venue_ids)
    
    def filter_by_service_type(self, queryset, name, value):
        if not value:
            return queryset
        
        # Only include venues that have the requested package type
        return queryset.filter(
            packages__name=value,
            packages__is_active=True
        ).distinct()
    
    def filter_by_max_price(self, queryset, name, value):
        if not value:
            return queryset
        
        # Filter by venues that have at least one package within price range
        return queryset.filter(
            packages__price__lte=value,
            packages__is_active=True
        ).distinct()