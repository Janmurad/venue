from rest_framework import serializers
from .models import Dish, Salad, WeddingMenu, MenuDish, MenuSalad


class DishSerializer(serializers.ModelSerializer):
    """Tagam serializer"""
    category_display = serializers.CharField(
        source='get_category_display',
        read_only=True
    )
    
    class Meta:
        model = Dish
        fields = [
            'id',
            'name',
            'description',
            'category',
            'category_display',
            'price',
            'weight',
            'is_vegetarian',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SaladSerializer(serializers.ModelSerializer):
    """Salat serializer"""
    
    class Meta:
        model = Salad
        fields = [
            'id',
            'name',
            'description',
            'ingredients',
            'price',
            'weight',
            'is_vegetarian',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class MenuDishSerializer(serializers.ModelSerializer):
    """Menýudaky tagam serializer"""
    dish_detail = DishSerializer(source='dish', read_only=True)
    
    class Meta:
        model = MenuDish
        fields = ['id', 'dish', 'dish_detail', 'quantity', 'order']


class MenuSaladSerializer(serializers.ModelSerializer):
    """Menýudaky salat serializer"""
    salad_detail = SaladSerializer(source='salad', read_only=True)
    
    class Meta:
        model = MenuSalad
        fields = ['id', 'salad', 'salad_detail', 'quantity', 'order']


class WeddingMenuSerializer(serializers.ModelSerializer):
    """Toý menýusy serializer (list üçin)"""
    dishes_count = serializers.SerializerMethodField()
    salads_count = serializers.SerializerMethodField()
    
    class Meta:
        model = WeddingMenu
        fields = [
            'id',
            'name',
            'description',
            'price_per_person',
            'min_guests',
            'is_active',
            'dishes_count',
            'salads_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_dishes_count(self, obj):
        return obj.menudish_set.count()
    
    def get_salads_count(self, obj):
        return obj.menusalad_set.count()


class WeddingMenuDetailSerializer(serializers.ModelSerializer):
    """Toý menýusy serializer (detail üçin)"""
    menu_dishes = MenuDishSerializer(source='menudish_set', many=True, read_only=True)
    menu_salads = MenuSaladSerializer(source='menusalad_set', many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = WeddingMenu
        fields = [
            'id',
            'name',
            'description',
            'price_per_person',
            'min_guests',
            'is_active',
            'menu_dishes',
            'menu_salads',
            'total_price',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_price(self, obj):
        return obj.calculate_total_price()