from django.contrib import admin
from .models import Dish, Salad, WeddingMenu, MenuDish, MenuSalad


class MenuDishInline(admin.TabularInline):
    """Menýuda tagamlary görkezmek"""
    model = MenuDish
    extra = 1
    autocomplete_fields = ['dish']


class MenuSaladInline(admin.TabularInline):
    """Menýuda salatlary görkezmek"""
    model = MenuSalad
    extra = 1
    autocomplete_fields = ['salad']


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'weight', 'is_vegetarian', 'is_active']
    list_filter = ['category', 'is_vegetarian', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    ordering = ['category', 'name']
    
    fieldsets = (
        ('Esasy maglumat', {
            'fields': ('name', 'description', 'category')
        }),
        ('Baha we agramy', {
            'fields': ('price', 'weight')
        }),
        ('Goşmaça', {
            'fields': ('is_vegetarian', 'is_active')
        }),
    )


@admin.register(Salad)
class SaladAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'weight', 'is_vegetarian', 'is_active']
    list_filter = ['is_vegetarian', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'ingredients']
    list_editable = ['is_active']
    ordering = ['name']
    
    fieldsets = (
        ('Esasy maglumat', {
            'fields': ('name', 'description', 'ingredients')
        }),
        ('Baha we agramy', {
            'fields': ('price', 'weight')
        }),
        ('Goşmaça', {
            'fields': ('is_vegetarian', 'is_active')
        }),
    )


@admin.register(WeddingMenu)
class WeddingMenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_person', 'min_guests', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']
    ordering = ['-created_at']
    inlines = [MenuDishInline, MenuSaladInline]
    
    fieldsets = (
        ('Esasy maglumat', {
            'fields': ('name', 'description')
        }),
        ('Baha', {
            'fields': ('price_per_person', 'min_guests')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Created_at we updated_at görkezmek"""
        if obj:
            return ['created_at', 'updated_at']
        return []