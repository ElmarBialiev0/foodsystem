from django.db import models
from django.contrib.auth.models import AbstractUser

# Роли пользователей
class Role(models.TextChoices):
    ADMIN = 'admin', 'Администратор'
    COOK = 'cook', 'Повар'
    CLIENT = 'client', 'Клиент'
    STOCKMAN = 'stockman', 'Кладовщик'
    CASHIER = 'cashier', 'Буфетчик'  # на будущее

# Кастомный пользователь
class User(AbstractUser):
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

# Ингредиенты на складе
class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    unit = models.CharField(max_length=20)  # г, кг, мл, л и т.п.
    quantity = models.FloatField(default=0)

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"

# Технические карты (рецепты)
class Recipe(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    output_weight = models.FloatField(help_text="Выходной вес (граммы)")
    
    def __str__(self):
        return self.name

# Ингредиенты в рецепте
class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField(help_text="Необходимое количество")

    def __str__(self):
        return f"{self.ingredient.name} для {self.recipe.name}"

# Меню — блюда, доступные к заказу
class MenuItem(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    date_available = models.DateField()

    def __str__(self):
        return f"{self.recipe.name} ({self.date_available})"

# Заказ клиента
class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('ready', 'Готов'),
        ('completed', 'Выдан'),
        ('cancelled', 'Отменён'),
    ]
    client = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': Role.CLIENT})
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Заказ #{self.id} от {self.client.username}"

    @property
    def total(self):
        return sum(item.menu_item.price * item.quantity for item in self.items.all())

# Позиции в заказе
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.recipe.name}"

# Движения по складу (приход/расход)
class InventoryTransaction(models.Model):
    TYPE_CHOICES = [
        ('in', 'Приход'),
        ('out', 'Расход'),
        ('write_off', 'Списание'),
    ]
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantity = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_type_display()} {self.ingredient.name} ({self.quantity})"
