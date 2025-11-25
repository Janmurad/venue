from rest_framework import serializers
from .models import Property, PropertyImage, Service, PropertyService, Booking, BookingService, Category
from datetime import date


class CategorySerializer(serializers.ModelSerializer):
    """Kategoriýa maglumatlary üçin"""

    class Meta:
        model = Category
        # 'description' we 'slug' goşdum, sebäbi olar modelde bar
        fields = ['id', 'name', 'slug', 'description', 'icon']

    def to_representation(self, instance):
        """Çykyşda 'icon' üçin doly URL berýär (Kotlin data class üçin)"""
        representation = super().to_representation(instance)

        # Icon meýdanyny doly URL bilen çalyş
        if instance.icon and hasattr(instance.icon, 'url'):
            request = self.context.get('request')
            if request:
                representation['icon'] = request.build_absolute_uri(instance.icon.url)
            else:
                # Request bolmasa (mysal üçin testde) diňe faýl ýoluny görkez
                representation['icon'] = instance.icon.url
        elif 'icon' in representation:
            # Eger ikonka ýok bolsa, null gaýdýar
            representation['icon'] = None

        return representation


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'is_main', 'order']


class PropertyImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        # Ensure 'property' field is excluded or set as read_only if you pass it in create()
        fields = ['image', 'is_main', 'order']


class PropertyCreateSerializer(serializers.ModelSerializer):
    """Jaý we oňa degişli suratlary döretmek üçin serializer"""

    # Use the writeable image serializer for nested input (many=True)
    images = PropertyImageUploadSerializer(many=True, required=False)

    class Meta:
        model = Property
        fields = [
            'title', 'description', 'address', 'category',
            'price_per_night', 'max_guests', 'area', 'images'  # Include 'images' field
        ]
        # It's crucial to NOT set 'images' as read_only here.

    def create(self, validated_data):
        """Property we PropertyImage obýektlerini döredýär"""
        # 1. Image datany aýyr
        images_data = validated_data.pop('images', [])

        # 2. Property obýektini döret
        property_obj = Property.objects.create(**validated_data)

        # 3. Her bir surat üçin PropertyImage obýektini döret
        for image_data in images_data:
            PropertyImage.objects.create(
                property=property_obj,
                **image_data
            )

        return property_obj


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'icon']


class PropertyServiceSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = PropertyService
        fields = ['id', 'service', 'price', 'is_included']


class PropertyListSerializer(serializers.ModelSerializer):
    """Jaýlaryň sanawy üçin - ýönekeý maglumat"""
    main_image = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'title', 'address', 'price_per_night', 'category',
            'max_guests', 'area', 'main_image', 'is_available'
        ]

    def get_main_image(self, obj):
        main_img = obj.images.filter(is_main=True).first()
        if main_img:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(main_img.image.url)
        return None


class PropertyDetailSerializer(serializers.ModelSerializer):
    """Jaýyň doly maglumaty üçin"""
    images = PropertyImageSerializer(many=True, read_only=True)
    property_services = PropertyServiceSerializer(many=True, read_only=True)
    available_services = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'title', 'description', 'address',
            'price_per_night', 'max_guests', 'area', 'is_available',
            'images', 'property_services', 'available_services',
            'created_at', 'updated_at', 'category'
        ]

    def get_available_services(self, obj):
        """Saýlanyp bilinjek goşmaça hyzmatlar"""
        services = obj.property_services.filter(
            service__is_active=True,
            is_included=False
        )
        return PropertyServiceSerializer(services, many=True).data


class BookingServiceSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)

    class Meta:
        model = BookingService
        fields = ['id', 'service', 'service_name', 'quantity', 'price']


class BookingSerializer(serializers.ModelSerializer):
    booking_services = BookingServiceSerializer(many=True, read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)
    services_data = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Booking
        fields = [
            'id', 'property', 'property_title', 'customer_name',
            'customer_phone', 'customer_email', 'check_in',
            'check_out', 'guests_count', 'total_price',
            'status', 'notes', 'booking_services', 'services_data',
            'created_at'
        ]
        read_only_fields = ['status', 'created_at']

    def validate(self, data):
        """Bron maglumatlary barlamak"""
        check_in = data.get('check_in')
        check_out = data.get('check_out')
        property_obj = data.get('property')
        guests_count = data.get('guests_count')

        # Seneleri barla
        if check_in and check_out:
            if check_in < date.today():
                raise serializers.ValidationError(
                    "Giriş senesi geçmişde bolup bilmez"
                )
            if check_out <= check_in:
                raise serializers.ValidationError(
                    "Çykyş senesi giriş senesinden soň bolmaly"
                )

        # Myhmanlaryň sanyny barla
        if property_obj and guests_count:
            if guests_count > property_obj.max_guests:
                raise serializers.ValidationError(
                    f"Bu jaýda iň köp {property_obj.max_guests} myhmana ýer bar"
                )

        # Şol senelerde başga bron barmy barla
        if property_obj and check_in and check_out:
            overlapping = Booking.objects.filter(
                property=property_obj,
                status__in=['pending', 'confirmed'],
                check_in__lt=check_out,
                check_out__gt=check_in
            )
            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise serializers.ValidationError(
                    "Bu senelerde jaý eýýäm bronlanan"
                )

        return data

    def create(self, validated_data):
        services_data = validated_data.pop('services_data', [])
        booking = Booking.objects.create(**validated_data)

        # Goşmaça hyzmatları goş
        for service_item in services_data:
            BookingService.objects.create(
                booking=booking,
                service_id=service_item['service_id'],
                quantity=service_item.get('quantity', 1),
                price=service_item['price']
            )

        return booking


class AvailabilitySerializer(serializers.Serializer):
    """Elýeterlilik barlamak üçin"""
    property_id = serializers.IntegerField()
    check_in = serializers.DateField()
    check_out = serializers.DateField()

    def validate(self, data):
        if data['check_out'] <= data['check_in']:
            raise serializers.ValidationError(
                "Çykyş senesi giriş senesinden soň bolmaly"
            )
        return data
