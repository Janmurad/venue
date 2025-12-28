"""
Management command: catering/management/commands/seed_catering.py

Ulanylyşy:
python manage.py seed_catering
python manage.py seed_catering --dishes 50 --salads 30 --menus 10
python manage.py seed_catering --clear  # öňki maglumatlary pozup täzeden doldurýar
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
import random
from catering.models import Dish, Salad, WeddingMenu, MenuDish, MenuSalad, DishCategory


class Command(BaseCommand):
    help = 'Catering app-yna Faker bilen maglumat doldurýar'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dishes',
            type=int,
            default=30,
            help='Tagamlaryň sany (default: 30)'
        )
        parser.add_argument(
            '--salads',
            type=int,
            default=20,
            help='Salatlaryň sany (default: 20)'
        )
        parser.add_argument(
            '--menus',
            type=int,
            default=8,
            help='Menýularyň sany (default: 8)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Öňki maglumatlary pozýar'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        fake = Faker(['ru_RU', 'en_US'])

        dishes_count = options['dishes']
        salads_count = options['salads']
        menus_count = options['menus']

        # Öňki maglumatlary pozmak
        if options['clear']:
            self.stdout.write(self.style.WARNING('Öňki maglumatlar pozulýar...'))
            MenuDish.objects.all().delete()
            MenuSalad.objects.all().delete()
            WeddingMenu.objects.all().delete()
            Dish.objects.all().delete()
            Salad.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Maglumatlar pozuldy'))

        self.stdout.write(self.style.SUCCESS('Maglumatlar döredilýär...'))

        # ============== TAGAMLAR ==============
        self.stdout.write('Tagamlar döredilýär...')
        dishes = []

        # Türkmen tagamlary
        turkmen_dishes = {
            DishCategory.APPETIZER: ['Çig börek', 'Samsa', 'Gutap', 'Börek', 'Işlekli'],
            DishCategory.SOUP: ['Dograma', 'Unaş', 'Mastawa', 'Piti', 'Kelle-paça'],
            DishCategory.MAIN_COURSE: ['Palaw', 'Şaşlyk', 'Manti', 'Govurdak', 'Çekdirme', 'Kebap', 'Kourma'],
            DishCategory.SIDE_DISH: ['Şille', 'Çörek', 'Gara çörek', 'Garnyýar'],
            DishCategory.DESSERT: ['Pähel', 'Çäkçäk', 'Gatlak', 'Bal', 'Peýnir'],
            DishCategory.BEVERAGE: ['Gök çaý', 'Süýt çaý', 'Şerbet', 'Aýran', 'Gowşak']
        }

        # Halkara tagamlary
        international_dishes = {
            DishCategory.APPETIZER: ['Брускетта', 'Капрезе', 'Мини-канапе', 'Тартар из лосося', 'Фалафель'],
            DishCategory.SOUP: ['Том ям', 'Минестроне', 'Крем-суп', 'Гаспачо', 'Буйабес'],
            DishCategory.MAIN_COURSE: ['Стейк Рибай', 'Утка по-пекински', 'Лазанья', 'Ризотто', 'Паэлья',
                                       'Баранина на гриле'],
            DishCategory.SIDE_DISH: ['Картофель фри', 'Овощи гриль', 'Рис с овощами', 'Картофельное пюре'],
            DishCategory.DESSERT: ['Тирамису', 'Крем-брюле', 'Чизкейк', 'Панна-котта', 'Эклеры', 'Макаронс'],
            DishCategory.BEVERAGE: ['Фреш апельсиновый', 'Мохито', 'Лимонад', 'Кофе эспрессо', 'Смузи']
        }

        for category in DishCategory.choices:
            cat_code = category[0]

            # Türkmen tagamlary
            if cat_code in turkmen_dishes:
                for name in turkmen_dishes[cat_code]:
                    dish = Dish.objects.create(
                        name=name,
                        description=fake.text(max_nb_chars=150),
                        category=cat_code,
                        price=random.randint(15, 150),
                        weight=random.randint(150, 500),
                        is_vegetarian=random.choice([True, False]),
                        is_active=random.choice([True, True, True, False])  # 75% işjeň
                    )
                    dishes.append(dish)

            # Halkara tagamlary
            if cat_code in international_dishes:
                for name in international_dishes[cat_code]:
                    dish = Dish.objects.create(
                        name=name,
                        description=fake.text(max_nb_chars=150),
                        category=cat_code,
                        price=random.randint(20, 200),
                        weight=random.randint(150, 500),
                        is_vegetarian=random.choice([True, False]),
                        is_active=random.choice([True, True, True, False])
                    )
                    dishes.append(dish)

        # Goşmaça random tagamlar
        remaining = dishes_count - len(dishes)
        if remaining > 0:
            for _ in range(remaining):
                dish = Dish.objects.create(
                    name=fake.word().capitalize() + ' ' + fake.word(),
                    description=fake.text(max_nb_chars=200),
                    category=random.choice([c[0] for c in DishCategory.choices]),
                    price=random.randint(20, 180),
                    weight=random.randint(150, 500),
                    is_vegetarian=random.choice([True, False]),
                    is_active=random.choice([True, True, True, False])
                )
                dishes.append(dish)

        self.stdout.write(self.style.SUCCESS(f'✓ {len(dishes)} tagam döredildi'))

        # ============== SALATLAR ==============
        self.stdout.write('Salatlar döredilýär...')
        salads = []

        salad_names = [
            'Çoban salaty', 'Salat Nowruz', 'Rus salaty', 'Olivýe',
            'Цезарь', 'Греческий', 'Капрезе', 'Овощной микс',
            'Салат с тунцом', 'Салат с креветками', 'Нисуаз',
            'Витаминный', 'Свекольный', 'Фунчоза', 'Табуле',
            'Коул-слоу', 'Салат с курицей', 'Теплый салат'
        ]

        for name in salad_names[:salads_count]:
            ingredients = ', '.join([fake.word() for _ in range(random.randint(4, 8))])

            salad = Salad.objects.create(
                name=name,
                description=fake.text(max_nb_chars=150),
                ingredients=ingredients,
                price=random.randint(15, 80),
                weight=random.randint(150, 350),
                is_vegetarian=random.choice([True, True, False]),  # 66% wegetarian
                is_active=random.choice([True, True, True, False])
            )
            salads.append(salad)

        self.stdout.write(self.style.SUCCESS(f'✓ {len(salads)} salat döredildi'))

        # ============== MENÝULAR ==============
        self.stdout.write('Menýular döredilýär...')

        menu_types = [
            ('Эконом', 50, 80, 30),
            ('Стандарт', 80, 120, 40),
            ('Премиум', 120, 200, 50),
            ('VIP', 200, 350, 30),
            ('Детский', 40, 60, 20),
            ('Вегетарианский', 70, 100, 25),
            ('Национальный', 90, 150, 40),
            ('Европейский', 100, 180, 35),
        ]

        for i in range(menus_count):
            menu_type = random.choice(menu_types)
            name = f"Menýu '{menu_type[0]}' - {fake.word().capitalize()}"

            menu = WeddingMenu.objects.create(
                name=name,
                description=fake.text(max_nb_chars=250),
                price_per_person=random.randint(menu_type[1], menu_type[2]),
                min_guests=menu_type[3],
                is_active=random.choice([True, True, True, False])
            )

            # Menýä tagamlary goşmak
            selected_dishes = random.sample(
                [d for d in dishes if d.is_active],
                k=min(random.randint(8, 15), len([d for d in dishes if d.is_active]))
            )

            for order, dish in enumerate(selected_dishes, start=1):
                MenuDish.objects.create(
                    menu=menu,
                    dish=dish,
                    quantity=random.randint(1, 3),
                    order=order
                )

            # Menýä salatlary goşmak
            selected_salads = random.sample(
                [s for s in salads if s.is_active],
                k=min(random.randint(3, 6), len([s for s in salads if s.is_active]))
            )

            for order, salad in enumerate(selected_salads, start=1):
                MenuSalad.objects.create(
                    menu=menu,
                    salad=salad,
                    quantity=random.randint(1, 2),
                    order=order
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f'  ✓ {menu.name} ({selected_dishes.__len__()} tagam, {selected_salads.__len__()} salat)'
                )
            )

        # Jemi statistika
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('JEMI STATISTIKA:'))
        self.stdout.write(self.style.SUCCESS(f'  Tagamlar: {Dish.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Salatlar: {Salad.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Menýular: {WeddingMenu.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Menýudaky tagamlar: {MenuDish.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'  Menýudaky salatlar: {MenuSalad.objects.count()}'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('✓ Ähli maglumatlar üstünlikli döredildi!'))