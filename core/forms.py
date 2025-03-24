from django import forms
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from .models import User, Recipe, RecipeIngredient
from django.forms import inlineformset_factory
from .models import MenuItem, InventoryTransaction, Ingredient

# Форма для редактирования пользователя
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'is_active']

# Форма для создания нового пользователя
class UserCreationForm(DjangoUserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'is_active', 'password1', 'password2']

# Форма для рецепта
class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'description', 'output_weight']

# Форма для ингредиента
class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'unit', 'quantity']

# Форма для меню
class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['recipe', 'price', 'date_available']

# Форма для инвентарных транзакций
class InventoryTransactionForm(forms.ModelForm):
    class Meta:
        model = InventoryTransaction
        fields = ['ingredient', 'type', 'quantity', 'comment']

# Формсет для ингредиентов
RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    fields=('ingredient', 'quantity'),
    extra=1,  # Добавляем одно пустое поле
    can_delete=True
)

class ClientRegisterForm(DjangoUserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']