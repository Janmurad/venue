from django.db import models
from django.core.validators import MinValueValidator


class DishCategory(models.TextChoices):
    """Tagam kategoriýalary"""
    APPETIZER = 'appetizer', 'Başlangyç'
    SOUP = 'soup', 'Çorba'
    MAIN_COURSE = 'main_course', 'Esasy tagam'
    SIDE_DISH = 'side_dish', 'Garnir'
    DESSERT = 'dessert', 'Desert'
    BEVERAGE = 'beverage', 'Içgi'


class Dish(models.Model):
    """Tagam modeli"""
    name = models.CharField(max_length=200, verbose_name='Tagam ady')
    description = models.TextField(blank=True, verbose_name='Düşündiriş')
    category = models.CharField(
        max_length=20,
        choices=DishCategory.choices,
        verbose_name='Kategoriýa'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Baha'
    )
    weight = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Agramy (gram)'
    )
    is_vegetarian = models.BooleanField(
        default=False,
        verbose_name='Wegetarian'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Işjeň'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tagam'
        verbose_name_plural = 'Tagamlar'
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Salad(models.Model):
    """Salat modeli"""
    name = models.CharField(max_length=200, verbose_name='Salat ady')
    description = models.TextField(blank=True, verbose_name='Düşündiriş')
    ingredients = models.TextField(verbose_name='Düzümi')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Baha'
    )
    weight = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Agramy (gram)'
    )
    is_vegetarian = models.BooleanField(
        default=False,
        verbose_name='Wegetarian'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Işjeň'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Salat'
        verbose_name_plural = 'Salatlar'
        ordering = ['name']

    def __str__(self):
        return self.name


class WeddingMenu(models.Model):
    """Toý menýusy modeli"""
    name = models.CharField(max_length=200, verbose_name='Menýu ady')
    description = models.TextField(blank=True, verbose_name='Düşündiriş')
    dishes = models.ManyToManyField(
        Dish,
        through='MenuDish',
        related_name='wedding_menus',
        verbose_name='Tagamlar'
    )
    salads = models.ManyToManyField(
        Salad,
        through='MenuSalad',
        related_name='wedding_menus',
        verbose_name='Salatlar'
    )
    price_per_person = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        verbose_name='Bir adama baha'
    )
    min_guests = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Iň az myhmanlaryň sany'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Işjeň'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Toý menýusy'
        verbose_name_plural = 'Toý menýulary'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def calculate_total_price(self):
        """Menýunyň jemi bahasyny hasaplamak"""
        dishes_total = sum(
            md.dish.price * md.quantity 
            for md in self.menudish_set.all()
        )
        salads_total = sum(
            ms.salad.price * ms.quantity 
            for ms in self.menusalad_set.all()
        )
        return dishes_total + salads_total


class MenuDish(models.Model):
    """Menýu we tagam arasyndaky baglanyşyk"""
    menu = models.ForeignKey(
        WeddingMenu,
        on_delete=models.CASCADE,
        verbose_name='Menýu'
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.CASCADE,
        verbose_name='Tagam'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Mukdary'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Tertip'
    )

    class Meta:
        verbose_name = 'Menýudaky tagam'
        verbose_name_plural = 'Menýudaky tagamlar'
        ordering = ['order', 'dish__category']
        unique_together = ['menu', 'dish']

    def __str__(self):
        return f"{self.dish.name} - {self.menu.name}"


class MenuSalad(models.Model):
    """Menýu we salat arasyndaky baglanyşyk"""
    menu = models.ForeignKey(
        WeddingMenu,
        on_delete=models.CASCADE,
        verbose_name='Menýu'
    )
    salad = models.ForeignKey(
        Salad,
        on_delete=models.CASCADE,
        verbose_name='Salat'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Mukdary'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Tertip'
    )

    class Meta:
        verbose_name = 'Menýudaky salat'
        verbose_name_plural = 'Menýudaky salatlar'
        ordering = ['order']
        unique_together = ['menu', 'salad']

    def __str__(self):
        return f"{self.salad.name} - {self.menu.name}"