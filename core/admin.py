from django.contrib import admin
from .models import (
    User, Ingredient, Recipe, RecipeIngredient,
    MenuItem, Order, OrderItem, InventoryTransaction
)

admin.site.register(User)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(InventoryTransaction)
