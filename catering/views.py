from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Dish, Salad, WeddingMenu
from .serializers import (
    DishSerializer,
    SaladSerializer,
    WeddingMenuSerializer,
    WeddingMenuDetailSerializer
)


class DishViewSet(viewsets.ModelViewSet):
    """Tagamlar ViewSet"""
    queryset = Dish.objects.filter(is_active=True)
    serializer_class = DishSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_vegetarian']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['category', 'name']


class SaladViewSet(viewsets.ModelViewSet):
    """Salatlar ViewSet"""
    queryset = Salad.objects.filter(is_active=True)
    serializer_class = SaladSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_vegetarian']
    search_fields = ['name', 'description', 'ingredients']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['name']


class WeddingMenuViewSet(viewsets.ModelViewSet):
    """Toý menýulary ViewSet"""
    queryset = WeddingMenu.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price_per_person', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Detail üçin başga serializer ulanmak"""
        if self.action == 'retrieve':
            return WeddingMenuDetailSerializer
        return WeddingMenuSerializer
    
    @action(detail=True, methods=['get'])
    def calculate_price(self, request, pk=None):
        """Menýunyň jemi bahasyny hasaplamak"""
        menu = self.get_object()
        guests = request.query_params.get('guests', 1)
        
        try:
            guests = int(guests)
        except ValueError:
            guests = 1
        
        total_per_person = menu.calculate_total_price()
        total_for_guests = total_per_person * guests
        
        return Response({
            'menu_id': menu.id,
            'menu_name': menu.name,
            'guests_count': guests,
            'price_per_person': total_per_person,
            'total_price': total_for_guests
        })