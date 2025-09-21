from rest_framework import serializers
from .models import Venue, VenueImage, Package, AvailabilityBlock
from datetime import date, timedelta

class VenueImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueImage
        fields = ['id', 'image', 'alt_text_tm', 'alt_text_ru', 'order']

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = [
            'id', 'name', 'name_tm', 'name_ru', 
            'price', 'details_tm', 'details_ru'
        ]

class AvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailabilityBlock
        fields = ['date', 'is_closed', 'reason_tm', 'reason_ru']

class VenueListSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    price_range = serializers.SerializerMethodField()
    
    class Meta:
        model = Venue
        fields = [
            'id', 'name_tm', 'name_ru', 'address_tm', 'address_ru',
            'capacity_min', 'capacity_max', 'base_price', 'price_range',
            'image_url'
        ]
    
    def get_image_url(self, obj):
        first_image = obj.images.first()
        if first_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_image.image.url)
        return None
    
    def get_price_range(self, obj):
        packages = obj.packages.filter(is_active=True)
        if packages.exists():
            min_price = min(pkg.price for pkg in packages)
            max_price = max(pkg.price for pkg in packages)
            return {
                'min': float(min_price),
                'max': float(max_price)
            }
        return {
            'min': float(obj.base_price),
            'max': float(obj.base_price)
        }

class VenueDetailSerializer(serializers.ModelSerializer):
    images = VenueImageSerializer(many=True, read_only=True)
    packages = PackageSerializer(many=True, read_only=True)
    availability_calendar = serializers.SerializerMethodField()
    price_range = serializers.SerializerMethodField()
    
    class Meta:
        model = Venue
        fields = [
            'id', 'name_tm', 'name_ru', 'address_tm', 'address_ru',
            'capacity_min', 'capacity_max', 'base_price', 'price_range',
            'description_tm', 'description_ru', 'status',
            'images', 'packages', 'availability_calendar'
        ]
    
    def get_availability_calendar(self, obj):
        # Return availability for next 12 months
        today = date.today()
        end_date = today + timedelta(days=365)
        
        # Get all blocked dates
        blocked_dates = set(
            obj.availability_blocks.filter(
                date__gte=today,
                date__lte=end_date,
                is_closed=True
            ).values_list('date', flat=True)
        )
        
        # Generate calendar
        calendar = []
        current_date = today
        
        while current_date <= end_date:
            calendar.append({
                'date': current_date.isoformat(),
                'is_available': current_date not in blocked_dates
            })
            current_date += timedelta(days=1)
        
        return calendar
    
    def get_price_range(self, obj):
        packages = obj.packages.filter(is_active=True)
        if packages.exists():
            min_price = min(pkg.price for pkg in packages)
            max_price = max(pkg.price for pkg in packages)
            return {
                'min': float(min_price),
                'max': float(max_price)
            }
        return {
            'min': float(obj.base_price),
            'max': float(obj.base_price)
        }