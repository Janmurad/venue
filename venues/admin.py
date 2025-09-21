from django.contrib import admin
from .models import Venue, VenueImage, Package, AvailabilityBlock

class VenueImageInline(admin.TabularInline):
    model = VenueImage
    extra = 1
    fields = ['image', 'alt_text_tm', 'alt_text_ru', 'order']

class PackageInline(admin.TabularInline):
    model = Package
    extra = 1
    fields = ['name', 'name_tm', 'name_ru', 'price', 'is_active']

class AvailabilityBlockInline(admin.TabularInline):
    model = AvailabilityBlock
    extra = 0
    fields = ['date', 'is_closed', 'reason_tm', 'reason_ru']

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ['name_tm', 'name_ru', 'capacity_min', 'capacity_max', 'base_price', 'status']
    list_filter = ['status', 'created_at']
    search_fields = ['name_tm', 'name_ru', 'address_tm', 'address_ru']
    inlines = [VenueImageInline, PackageInline, AvailabilityBlockInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name_tm', 'name_ru', 'status')
        }),
        ('Location', {
            'fields': ('address_tm', 'address_ru')
        }),
        ('Capacity & Pricing', {
            'fields': ('capacity_min', 'capacity_max', 'base_price')
        }),
        ('Description', {
            'fields': ('description_tm', 'description_ru')
        }),
    )

@admin.register(VenueImage)
class VenueImageAdmin(admin.ModelAdmin):
    list_display = ['venue', 'order', 'created_at']
    list_filter = ['venue', 'created_at']
    ordering = ['venue', 'order']

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ['venue', 'name', 'name_tm', 'price', 'is_active']
    list_filter = ['name', 'is_active', 'venue']
    search_fields = ['venue__name_tm', 'name_tm', 'name_ru']

@admin.register(AvailabilityBlock)
class AvailabilityBlockAdmin(admin.ModelAdmin):
    list_display = ['venue', 'date', 'is_closed']
    list_filter = ['is_closed', 'date', 'venue']
    date_hierarchy = 'date'
    search_fields = ['venue__name_tm']
