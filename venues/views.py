from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from datetime import datetime
from .models import Property, Service, Booking, Category
from .serializers import (
    PropertyListSerializer, PropertyDetailSerializer, PropertyCreateSerializer,
    ServiceSerializer, BookingSerializer, CategorySerializer
)


class CustomPageNumberPagination(PageNumberPagination):
    """
    Kustom pagination klasy.
    URL görnüşi: /properties/?page=1&page_size=10
    """
    page_size_query_param = 'size'
    max_page_size = 100
    page_size = 10


class PropertyViewSet(viewsets.ModelViewSet):
    """Jaýlar API - diňe okamak üçin (admin panel arkaly goşulýar)"""
    queryset = Property.objects.filter(is_available=True)
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return PropertyCreateSerializer
        if self.action == 'retrieve':
            return PropertyDetailSerializer
        return PropertyListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        category_id = self.request.query_params.get('category_id', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)

            # Bron seneleri boýunça filter
            check_in = self.request.query_params.get('check_in', None)
            check_out = self.request.query_params.get('check_out', None)

            if check_in and check_out:
                try:
                    check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
                    check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()

                    # Şu senelerde bronlanan jaýlary tap
                    overlapping_bookings = Booking.objects.filter(
                        status__in=['confirmed'],
                        check_in__lt=check_out_date,  # Bron başlangyç senesi soňra check_out-dan
                        check_out__gt=check_in_date  # Bron gutarýan senesi öň check_in-dan
                    ).values_list('property_id', flat=True)

                    # Bronlanan jaýlary aýyr
                    queryset = queryset.exclude(id__in=overlapping_bookings)
                except ValueError:
                    pass  # Sene formaty nädogry bolsa, skip et

        # Gözleg
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(address__icontains=search)
            )

        # Bahadan filter
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)

        if min_price:
            queryset = queryset.filter(price_per_night__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_night__lte=max_price)

        # Myhmanlaryň sany
        guests = self.request.query_params.get('guests', None)
        if guests:
            queryset = queryset.filter(max_guests__gte=guests)

        # Ýatylýan otaglar
        bedrooms = self.request.query_params.get('bedrooms', None)
        if bedrooms:
            queryset = queryset.filter(bedrooms__gte=bedrooms)

        return queryset

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Jaýyň elýeterliligin barlamak"""
        property_obj = self.get_object()
        check_in = request.query_params.get('check_in')
        check_out = request.query_params.get('check_out')

        if not check_in or not check_out:
            return Response(
                {'error': 'check_in we check_out gerek'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Sene formaty nädogry (YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Bron barmy barla
        overlapping = Booking.objects.filter(
            property=property_obj,
            status__in=['pending', 'confirmed'],
            check_in__lt=check_out_date,
            check_out__gt=check_in_date
        )

        is_available = not overlapping.exists()

        return Response({
            'available': is_available,
            'message': 'Elýeterli' if is_available else 'Bu senelerde eýýäm bronlanan'
        })

    @action(detail=True, methods=['get'])
    def booked_dates(self, request, pk=None):
        """Bronlanan seneleri almak (calendar üçin)"""
        property_obj = self.get_object()

        bookings = Booking.objects.filter(
            property=property_obj,
            status__in=['pending', 'confirmed']
        ).values('check_in', 'check_out')

        booked_ranges = [
            {
                'start': booking['check_in'].isoformat(),
                'end': booking['check_out'].isoformat()
            }
            for booking in bookings
        ]

        return Response({'booked_dates': booked_ranges})


class CategoryViewSet(viewsets.ModelViewSet):
    """Kategoriýalar API - Goşmak, üýtgetmek we okamak üçin"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPageNumberPagination


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """Hyzmatlar API - diňe okamak üçin"""
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer


class BookingViewSet(viewsets.ModelViewSet):
    """Bronlar API - goşmak we okamak üçin"""
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Telefon belgisi boýunça gözleg (myhmanyň öz bronlaryny görmegi üçin)
        phone = self.request.query_params.get('phone', None)
        if phone:
            queryset = queryset.filter(customer_phone=phone)

        # Jaý boýunça filter
        property_id = self.request.query_params.get('property_id', None)
        if property_id:
            queryset = queryset.filter(property_id=property_id)

        # Status boýunça filter
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by('-created_at')

    def create(self, request, *args, **kwargs):
        """Täze bron döretmek"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {
                'message': 'Bron üstünlikli döredildi',
                'booking': serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Brony ýatirmak"""
        booking = self.get_object()

        if booking.status == 'cancelled':
            return Response(
                {'error': 'Bron eýýäm ýatyrylgan'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if booking.status == 'completed':
            return Response(
                {'error': 'Tamamlanan brony ýatyryp bolmaýar'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = 'cancelled'
        booking.save()

        return Response({
            'message': 'Bron ýatyryldy',
            'booking': BookingSerializer(booking).data
        })


class StatsViewSet(viewsets.ViewSet):
    """Statistika API - umumi maglumatlar"""

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Admin dashboard üçin statistika"""
        total_properties = Property.objects.count()
        available_properties = Property.objects.filter(is_available=True).count()
        total_bookings = Booking.objects.count()
        pending_bookings = Booking.objects.filter(status='pending').count()
        confirmed_bookings = Booking.objects.filter(status='confirmed').count()

        return Response({
            'properties': {
                'total': total_properties,
                'available': available_properties
            },
            'bookings': {
                'total': total_bookings,
                'pending': pending_bookings,
                'confirmed': confirmed_bookings
            }
        })
