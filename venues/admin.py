from django.contrib import admin
from django.utils.html import format_html
from .models import Property, PropertyImage, Service, PropertyService, Booking, BookingService


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ['image', 'is_main', 'order', 'image_preview']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "Surat ýok"

    image_preview.short_description = "Surat"


class PropertyServiceInline(admin.TabularInline):
    model = PropertyService
    extra = 1
    autocomplete_fields = ['service']


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'address', 'price_per_night', 'max_guests', 'is_available', 'created_at']
    list_filter = ['is_available', 'created_at']
    search_fields = ['title', 'address', 'description']
    list_editable = ['is_available']
    inlines = [PropertyImageInline, PropertyServiceInline]

    fieldsets = (
        ('Esasy maglumat', {
            'fields': ('title', 'description', 'address')
        }),
        ('Baha we aýratynlyklar', {
            'fields': ('price_per_night', 'max_guests', 'area')
        }),
        ('Status', {
            'fields': ('is_available',)
        }),
    )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'icon', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active']


class BookingServiceInline(admin.TabularInline):
    model = BookingService
    extra = 0
    readonly_fields = ['service', 'quantity', 'price']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['property', 'customer_name', 'customer_phone',
                    'check_in', 'check_out', 'guests_count',
                    'total_price', 'status', 'created_at']
    list_filter = ['status', 'check_in', 'check_out', 'created_at']
    search_fields = ['customer_name', 'customer_phone', 'customer_email',
                     'property__title']
    list_editable = ['status']
    date_hierarchy = 'check_in'
    inlines = [BookingServiceInline]

    fieldsets = (
        ('Jaý maglumaty', {
            'fields': ('property',)
        }),
        ('Müşderi maglumaty', {
            'fields': ('customer_name', 'customer_phone', 'customer_email')
        }),
        ('Bron maglumaty', {
            'fields': ('check_in', 'check_out', 'guests_count', 'total_price')
        }),
        ('Status we bellikler', {
            'fields': ('status', 'notes')
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing booking
            return self.readonly_fields + ['property', 'check_in', 'check_out',
                                           'customer_name', 'customer_phone',
                                           'customer_email', 'guests_count',
                                           'total_price']
        return self.readonly_fields


# Admin site customization
admin.site.site_header = "Palatka Ulgamy"
admin.site.site_title = "Admin Panel"
admin.site.index_title = "Dolandyryş Paneli"