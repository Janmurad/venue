from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Venue(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
    ]
    
    name_tm = models.CharField(max_length=255, verbose_name="Name (Turkmen)")
    name_ru = models.CharField(max_length=255, verbose_name="Name (Russian)")
    address_tm = models.TextField(verbose_name="Address (Turkmen)")
    address_ru = models.TextField(verbose_name="Address (Russian)")
    capacity_min = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Minimum Capacity"
    )
    capacity_max = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Maximum Capacity"
    )
    base_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Base Price"
    )
    description_tm = models.TextField(verbose_name="Description (Turkmen)")
    description_ru = models.TextField(verbose_name="Description (Russian)")
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='active',
        verbose_name="Status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Venue"
        verbose_name_plural = "Venues"
        ordering = ['name_tm']
    
    def __str__(self):
        return self.name_tm
    
    @property
    def is_available(self):
        return self.status == 'active'

class VenueImage(models.Model):
    venue = models.ForeignKey(
        Venue, 
        related_name='images', 
        on_delete=models.CASCADE,
        verbose_name="Venue"
    )
    image = models.ImageField(
        upload_to='venues/images/',
        verbose_name="Image"
    )
    alt_text_tm = models.CharField(max_length=255, blank=True, verbose_name="Alt Text (Turkmen)")
    alt_text_ru = models.CharField(max_length=255, blank=True, verbose_name="Alt Text (Russian)")
    order = models.PositiveIntegerField(default=0, verbose_name="Order")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Venue Image"
        verbose_name_plural = "Venue Images"
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"{self.venue.name_tm} - Image {self.order}"

class Package(models.Model):
    PACKAGE_TYPES = [
        ('standard', 'Standard'),
        ('gold', 'Gold'),
        ('vip', 'VIP'),
    ]
    
    venue = models.ForeignKey(
        Venue, 
        related_name='packages', 
        on_delete=models.CASCADE,
        verbose_name="Venue"
    )
    name = models.CharField(
        max_length=20, 
        choices=PACKAGE_TYPES,
        verbose_name="Package Type"
    )
    name_tm = models.CharField(max_length=100, verbose_name="Display Name (Turkmen)")
    name_ru = models.CharField(max_length=100, verbose_name="Display Name (Russian)")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Price"
    )
    details_tm = models.TextField(verbose_name="Details (Turkmen)")
    details_ru = models.TextField(verbose_name="Details (Russian)")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Package"
        verbose_name_plural = "Packages"
        unique_together = ['venue', 'name']
        ordering = ['venue', 'name']
    
    def __str__(self):
        return f"{self.venue.name_tm} - {self.get_name_display()}"

class AvailabilityBlock(models.Model):
    venue = models.ForeignKey(
        Venue, 
        related_name='availability_blocks', 
        on_delete=models.CASCADE,
        verbose_name="Venue"
    )
    date = models.DateField(verbose_name="Date")
    is_closed = models.BooleanField(
        default=True, 
        verbose_name="Is Closed",
        help_text="True means venue is NOT available on this date"
    )
    reason_tm = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name="Reason (Turkmen)"
    )
    reason_ru = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name="Reason (Russian)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Availability Block"
        verbose_name_plural = "Availability Blocks"
        unique_together = ['venue', 'date']
        ordering = ['date']
    
    def __str__(self):
        status = "Closed" if self.is_closed else "Available"
        return f"{self.venue.name_tm} - {self.date} ({status})"