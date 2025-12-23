from django.db import models
from django.core.validators import MinValueValidator
import uuid
from datetime import date
import os


def property_image_path(instance, filename):
    """
    Generates file path for uploaded property images:
    images/properties/<year>/<month>/<day>/<uuid>.<ext>
    """
    ext = filename.split('.')[-1]
    unique_name = f'{uuid.uuid4()}.{ext}'
    today = date.today()

    return os.path.join(
        'images',
        'properties',
        str(today.year),
        str(today.month).zfill(2),  # Use zfill to ensure two digits (e.g., 01)
        str(today.day).zfill(2),  # Use zfill to ensure two digits (e.g., 05)
        unique_name
    )


def category_icon_path(instance, filename):
    """
    Kategoriýa ikonkalary üçin faýl ýoluny döredýär:
    images/categories/<year>/<month>/<day>/<uuid>.<ext>
    """
    ext = filename.split('.')[-1]
    unique_name = f'{uuid.uuid4()}.{ext}'
    today = date.today()

    return os.path.join(
        'images',
        'categories',
        str(today.year),
        str(today.month).zfill(2),
        str(today.day).zfill(2),
        unique_name
    )


class Category(models.Model):
    """Jaý Kategoriýasy modeli"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Ady")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Düşündiriş")

    # CHARFIELD ýerine IMAGEFIELD hökmünde üýtgedildi
    icon = models.ImageField(
        upload_to=category_icon_path,  # Kustom faýl ýoly
        blank=True,
        null=True,  # Surat hökmünde goşulmazlygy mümkin
        verbose_name="Ikonka suraty"
    )

    class Meta:
        verbose_name = "Kategoriýa"
        verbose_name_plural = "Kategoriýalar"
        ordering = ['name']

    def __str__(self):
        return self.name


class Property(models.Model):
    """Jaý/Otag modeli"""
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,  # Kategoriýa ýatyrylsa, jaý NULL bolýar
        related_name='properties',
        null=True,
        blank=True,
        verbose_name="Kategoriýa"
    )
    title = models.CharField(max_length=255, verbose_name="Ady")
    description = models.TextField(verbose_name="Düşündiriş")
    address = models.CharField(max_length=500, verbose_name="Salgy")
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Bir gije üçin baha"
    )
    max_guests = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Iň köp myhmanlaryň sany"
    )
    area = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Meýdany (m²)",
        null=True,
        blank=True
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name="Elýeterli"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Palata"
        verbose_name_plural = "Palatkalar"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class PropertyImage(models.Model):
    """Jaýyň suratlary"""
    property = models.ForeignKey(
        Property,
        related_name='images',
        on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to=property_image_path,
        verbose_name="Surat"
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name="Esasy surat"
    )
    order = models.IntegerField(
        default=0,
        verbose_name="Tertip"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Surat"
        verbose_name_plural = "Suratlar"
        ordering = ['order', '-is_main']

    def __str__(self):
        return f"{self.property.title} - Surat {self.order}"


class Service(models.Model):
    """Goşmaça hyzmatlar"""
    name = models.CharField(max_length=255, verbose_name="Ady")
    description = models.TextField(
        blank=True,
        verbose_name="Düşündiriş"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Icon",
        help_text="Icon ady (meselem: 'utensils', 'snowflake')"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Işjeň"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Hyzmat"
        verbose_name_plural = "Hyzmatlar"
        ordering = ['name']

    def __str__(self):
        return self.name


class PropertyService(models.Model):
    """Jaýda elýeterli hyzmatlar we olaryň bahalary"""
    property = models.ForeignKey(
        Property,
        related_name='property_services',
        on_delete=models.CASCADE
    )
    service = models.ForeignKey(
        Service,
        related_name='property_services',
        on_delete=models.CASCADE
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Baha",
        help_text="Goşmaça töleg (0 = mugt)"
    )
    is_included = models.BooleanField(
        default=False,
        verbose_name="Bahada goşulan",
        help_text="Esasy bahada goşulan bolsa True"
    )

    class Meta:
        verbose_name = "Jaýyň hyzmaty"
        verbose_name_plural = "Jaýlaryň hyzmatlar"
        unique_together = ['property', 'service']

    def __str__(self):
        return f"{self.property.title} - {self.service.name}"


class Booking(models.Model):
    """Bronlamak modeli"""
    STATUS_CHOICES = [
        ('pending', 'Garaşylýar'),
        ('confirmed', 'Tassyklandy'),
        ('cancelled', 'Ýatyryldy'),
        ('completed', 'Tamamlandy'),
    ]

    property = models.ForeignKey(
        Property,
        related_name='bookings',
        on_delete=models.CASCADE
    )
    customer_name = models.CharField(
        max_length=255,
        verbose_name="Müşderiniň ady"
    )
    customer_phone = models.CharField(
        max_length=20,
        verbose_name="Telefon belgisi"
    )
    customer_email = models.EmailField(
        blank=True,
        verbose_name="Email"
    )
    check_in = models.DateField(verbose_name="Giriş senesi")
    check_out = models.DateField(verbose_name="Çykyş senesi")
    guests_count = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Myhmanlaryň sany"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Jemi baha"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Bellikler"
    )
    catering_menu = models.ForeignKey(
        'catering.WeddingMenu',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='bookings',
        verbose_name='Saýlanan toý menýusy'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bron"
        verbose_name_plural = "Bronlar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.property.title} - {self.customer_name} ({self.check_in})"


class BookingService(models.Model):
    """Bronda saýlanan goşmaça hyzmatlar"""
    booking = models.ForeignKey(
        Booking,
        related_name='booking_services',
        on_delete=models.CASCADE
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Mukdary"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Baha"
    )

    class Meta:
        verbose_name = "Bronyň hyzmaty"
        verbose_name_plural = "Bronlaryň hyzmatlar"

    def __str__(self):
        return f"{self.booking} - {self.service.name}"
