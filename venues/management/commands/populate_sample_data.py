import random
import uuid
from decimal import Decimal
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from faker import Faker

from venues.models import Category, Property, Service, PropertyService, PropertyImage

class Command(BaseCommand):
    help = 'Populate database with sample data using Faker'

    def handle(self, *args, **options):
        self.stdout.write('Deleting old data...')
        PropertyService.objects.all().delete()
        PropertyImage.objects.all().delete()
        Property.objects.all().delete()
        Category.objects.all().delete()
        Service.objects.all().delete()

        fake = Faker()
        
        # 1. Create Categories
        self.stdout.write('Creating categories...')
        categories_data = ['Apartment', 'House', 'Villa', 'Studio', 'Cottage']
        categories = []
        for name in categories_data:
            cat, created = Category.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slugify(name),
                    'description': fake.text(max_nb_chars=200)
                }
            )
            categories.append(cat)

        # 2. Create Services
        self.stdout.write('Creating services...')
        services_data = [
            ('WiFi', 'wifi'),
            ('Air Conditioning', 'snowflake'),
            ('Kitchen', 'utensils'),
            ('Parking', 'car'),
            ('Pool', 'water'),
            ('Gym', 'dumbbell'),
            ('TV', 'tv'),
            ('Washing Machine', 'tshirt')
        ]
        services = []
        for name, icon in services_data:
            service, created = Service.objects.get_or_create(
                name=name,
                defaults={
                    'description': fake.sentence(),
                    'icon': icon
                }
            )
            services.append(service)

        # 3. Create Properties
        self.stdout.write('Creating properties...')
        
        # Helper to create a dummy image
        def create_dummy_image(name):
            # 1x1 pixel red dot
            return ContentFile(
                b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82',
                name=name
            )

        for _ in range(20):  # Create 20 properties
            category = random.choice(categories)
            title = f"{fake.word().title()} {category.name}"
            
            property_obj = Property.objects.create(
                category=category,
                title=title,
                description=fake.paragraph(nb_sentences=5),
                address=fake.address(),
                price_per_night=Decimal(random.randint(50, 500)),
                max_guests=random.randint(1, 10),
                area=random.randint(20, 300),
                is_available=True
            )

            # Add Services to Property
            # Randomly select 3-6 services
            selected_services = random.sample(services, k=random.randint(3, 6))
            for service in selected_services:
                PropertyService.objects.create(
                    property=property_obj,
                    service=service,
                    price=Decimal(random.choice([0, 10, 20, 50])),
                    is_included=random.choice([True, False])
                )

            # Add Images to Property
            for i in range(random.randint(1, 4)):
                img_name = f"prop_{property_obj.id}_{i}.png"
                PropertyImage.objects.create(
                    property=property_obj,
                    image=create_dummy_image(img_name),
                    is_main=(i == 0),
                    order=i
                )

        self.stdout.write(self.style.SUCCESS('Successfully populated sample data!'))