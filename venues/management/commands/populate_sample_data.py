from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from venues.models import Venue, Package, AvailabilityBlock
from datetime import date, timedelta
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Populate database with sample venue data'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating sample venues...')
        
        # Sample venue data
        venues_data = [
            {
                'name_tm': 'Aýdyň Köşk',
                'name_ru': 'Светлый Дворец',
                'address_tm': 'Aşgabat şäheri, Berkararlyk şaýoly 15',
                'address_ru': 'г. Ашгабад, проспект Независимости 15',
                'capacity_min': 50,
                'capacity_max': 200,
                'base_price': Decimal('1500.00'),
                'description_tm': 'Ajaýyp toýhanasy, ähli amatlylylar bilen',
                'description_ru': 'Прекрасный банкетный зал со всеми удобствами',
            },
            {
                'name_tm': 'Altyn Gül Restorany',
                'name_ru': 'Ресторан Золотая Роза',
                'address_tm': 'Aşgabat şäheri, Magtymguly şaýoly 45',
                'address_ru': 'г. Ашгабад, проспект Махтумкули 45',
                'capacity_min': 30,
                'capacity_max': 150,
                'base_price': Decimal('1200.00'),
                'description_tm': 'Romantik atmosfera we ýokary hylly hyzmat',
                'description_ru': 'Романтическая атмосфера и высококачественное обслуживание',
            },
            {
                'name_tm': 'Şadyýan Saraý',
                'name_ru': 'Дворец Радости',
                'address_tm': 'Aşgabat şäheri, Oguzhan şaýoly 12',
                'address_ru': 'г. Ашгабад, проспект Огузхана 12',
                'capacity_min': 80,
                'capacity_max': 300,
                'base_price': Decimal('2000.00'),
                'description_tm': 'Uly toýlar üçin iň oňat saýlaw',
                'description_ru': 'Лучший выбор для больших торжеств',
            }
        ]
        
        for venue_data in venues_data:
            venue, created = Venue.objects.get_or_create(
                name_tm=venue_data['name_tm'],
                defaults=venue_data
            )
            
            if created:
                self.stdout.write(f'Created venue: {venue.name_tm}')
                
                # Create packages
                packages_data = [
                    {
                        'name': 'standard',
                        'name_tm': 'Standart paket',
                        'name_ru': 'Стандартный пакет',
                        'price': venue.base_price,
                        'details_tm': 'Esasy hyzmatlar: otagy, oýun-rejeler, iýmit',
                        'details_ru': 'Основные услуги: зал, развлечения, питание',
                    },
                    {
                        'name': 'gold',
                        'name_tm': 'Altyn paket',
                        'name_ru': 'Золотой пакет',
                        'price': venue.base_price * Decimal('1.5'),
                        'details_tm': 'Ýokary derejeli hyzmatlar we goşmaça amatlylylar',
                        'details_ru': 'Услуги высокого уровня и дополнительные удобства',
                    },
                    {
                        'name': 'vip',
                        'name_tm': 'VIP paket',
                        'name_ru': 'VIP пакет',
                        'price': venue.base_price * Decimal('2.0'),
                        'details_tm': 'Iň ýokary derejeli hyzmatlar we şahsy hyzmatkar',
                        'details_ru': 'Услуги высшего уровня и персональный обслуживающий персонал',
                    }
                ]
                
                for pkg_data in packages_data:
                    Package.objects.create(venue=venue, **pkg_data)
                
                # Create some random availability blocks
                today = date.today()
                for i in range(50):
                    random_date = today + timedelta(days=random.randint(1, 365))
                    if random.random() < 0.1:  # 10% chance of being blocked
                        AvailabilityBlock.objects.get_or_create(
                            venue=venue,
                            date=random_date,
                            defaults={
                                'is_closed': True,
                                'reason_tm': 'Eýýäm ätiýaç edilen',
                                'reason_ru': 'Already booked'
                            }
                        )
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))