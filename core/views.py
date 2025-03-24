# core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import User
from .forms import UserForm
from .models import Recipe
from .forms import RecipeForm, RecipeIngredientFormSet
from .models import MenuItem
from .forms import MenuItemForm
from .models import Ingredient, InventoryTransaction
from .forms import InventoryTransactionForm
from .models import MenuItem, Order, OrderItem
from django.utils import timezone
import uuid
from django.urls import reverse
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import Order, OrderItem, Ingredient
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
import openpyxl
from openpyxl.styles import Font
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import UserCreationForm 
from .models import User
from .forms import IngredientForm
from .models import Ingredient
from .models import Recipe
from .forms import RecipeForm, RecipeIngredientFormSet
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .forms import ClientRegisterForm
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import date

#  Редирект на панель в зависимости от роли

# ✅ Проверка роли "админ"
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == 'admin')(view_func)
    
@login_required
def checkout(request):
    user = request.user
    order = Order.objects.filter(client=user, paid=False).first()
    if not order:
        return redirect('client_dashboard')

    if request.method == 'POST':
        order.paid = True
        order.save()
        return redirect('checkout_success')

    return render(request, 'client/checkout.html', {'order': order})

@login_required
def checkout_success(request):
    return render(request, 'client/checkout_success.html')
@login_required
def checkout_success(request):
    return render(request, 'client/checkout_success.html')

@login_required
def checkout(request):
    user = request.user
    cart = request.session.get('cart', {})

    if request.method == 'POST':
        if not cart:
            return redirect('client_menu')

        with transaction.atomic():
            order = Order.objects.create(client=user, paid=True, status='new')
            for item_id, quantity in cart.items():
                menu_item = MenuItem.objects.get(id=item_id)
                OrderItem.objects.create(order=order, menu_item=menu_item, quantity=quantity)
        
        request.session['cart'] = {}
        return redirect('checkout_success')

    items = []
    total = 0
    for item_id, quantity in cart.items():
        item = MenuItem.objects.get(id=item_id)
        items.append({'item': item, 'quantity': quantity, 'total': item.price * quantity})
        total += item.price * quantity

    return render(request, 'client/checkout.html', {'items': items, 'total': total})


@login_required
def dashboard_redirect(request):
    user = request.user
    if user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'cook':
        return redirect('cook_dashboard')
    elif user.role == 'stockman':
        return redirect('stockman_dashboard')
    elif user.role == 'client':
        return redirect('client_dashboard')
    return redirect('logout')

#  Проверка роли "админ"
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == 'admin')(view_func)

# 🧑 Панель администратора
@login_required
@admin_required
def admin_dashboard(request):
    stats = {
        'total_users': User.objects.count(),
        'admins': User.objects.filter(role='admin').count(),
        'cooks': User.objects.filter(role='cook').count(),
        'stockmen': User.objects.filter(role='stockman').count(),
        'clients': User.objects.filter(role='client').count(),
        'total_orders': Order.objects.count(),
        'today_orders': Order.objects.filter(created_at__date=date.today()).count(),
        'total_income': Order.objects.filter(paid=True).aggregate(
            total=Sum('orderitem__menu_item__price')
        )['total'] or 0,
    }

    # Последние заказы и операции
    latest_orders = Order.objects.order_by('-created_at')[:5]
    latest_transactions = InventoryTransaction.objects.order_by('-created_at')[:5]

    # 📊 Диаграмма по ролям
    roles = ['admin', 'cook', 'stockman', 'client']
    counts = [User.objects.filter(role=role).count() for role in roles]

    plt.figure(figsize=(6, 4))
    plt.bar(roles, counts, color='skyblue')
    plt.title('Пользователи по ролям')
    plt.xlabel('Роль')
    plt.ylabel('Количество')
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    chart_base64 = base64.b64encode(image_png).decode('utf-8')

    return render(request, 'admin/dashboard.html', {
        'stats': stats,
        'latest_orders': latest_orders,
        'latest_transactions': latest_transactions,
        'chart_base64': chart_base64,
    })

#  Панель повара
@login_required
def cook_dashboard(request):
    return render(request, 'cook/dashboard.html')

#  Панель кладовщика
@login_required
def stockman_dashboard(request):
    return render(request, 'stockman/dashboard.html')

#  Панель клиента
@login_required
def client_dashboard(request):
    return render(request, 'client/dashboard.html')

#  Список пользователей
@admin_required
def admin_user_list(request):
    users = User.objects.all()
    return render(request, 'admin/users/list.html', {'users': users})

#  Создание пользователя
@admin_required
def admin_user_create(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_user_list')
    else:
        form = UserCreationForm()
    return render(request, 'admin/users/create.html', {'form': form})

#  Редактирование пользователя
@admin_required
def admin_user_update(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    form = UserForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        return redirect('admin_user_list')
    return render(request, 'admin/users/update.html', {'form': form})

def admin_dashboard(request):
    from datetime import date

    # 📊 Сбор статистики
    stats = {
        'total_users': User.objects.count(),
        'admins': User.objects.filter(role='admin').count(),
        'cooks': User.objects.filter(role='cook').count(),
        'stockmen': User.objects.filter(role='stockman').count(),
        'clients': User.objects.filter(role='client').count(),
        'total_orders': Order.objects.count(),
        'today_orders': Order.objects.filter(created_at__date=date.today()).count(),
        'total_income': Order.objects.filter(paid=True).aggregate(
            total=Sum('items__menu_item__price')
        )['total'] or 0,
    }

    # 🔁 Последние заказы и операции
    latest_orders = Order.objects.order_by('-created_at')[:5]
    latest_transactions = InventoryTransaction.objects.order_by('-created_at')[:5]

    # 📈 Генерация диаграммы по ролям
    role_counts = [
        stats['admins'],
        stats['cooks'],
        stats['stockmen'],
        stats['clients'],
    ]
    roles = ['Админы', 'Повара', 'Кладовщики', 'Клиенты']

    fig, ax = plt.subplots()
    ax.pie(role_counts, labels=roles, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    return render(request, 'admin/dashboard.html', {
        'stats': stats,
        'latest_orders': latest_orders,
        'latest_transactions': latest_transactions,
        'chart_base64': chart_base64,
    })
#  Удаление пользователя
@admin_required
def admin_user_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.delete()
    return redirect('admin_user_list')

@admin_required
def admin_recipe_list(request):
    recipes = Recipe.objects.all()
    return render(request, 'admin/recipes/list.html', {'recipes': recipes})

@admin_required
def admin_recipe_create(request):
    recipe = Recipe()
    if request.method == 'POST':
        form = RecipeForm(request.POST, instance=recipe)
        formset = RecipeIngredientFormSet(request.POST, instance=recipe)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('admin_recipe_list')
    else:
        form = RecipeForm()
        formset = RecipeIngredientFormSet(instance=recipe)
    return render(request, 'admin/recipes/create.html', {
        'form': form,
        'formset': formset
    })

@admin_required
def admin_recipe_update(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    form = RecipeForm(request.POST or None, instance=recipe)
    formset = RecipeIngredientFormSet(request.POST or None, instance=recipe)
    if form.is_valid() and formset.is_valid():
        form.save()
        formset.save()
        return redirect('admin_recipe_list')
    return render(request, 'admin/recipes/update.html', {
        'form': form,
        'formset': formset
    })

@admin_required
def admin_recipe_delete(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    recipe.delete()
    return redirect('admin_recipe_list')

@admin_required
def admin_menu_list(request):
    menu_items = MenuItem.objects.order_by('-date_available')
    return render(request, 'admin/menu/list.html', {'menu_items': menu_items})

@admin_required
def admin_menu_create(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_menu_list')
    else:
        form = MenuItemForm()
    return render(request, 'admin/menu/create.html', {'form': form})

@admin_required
def admin_menu_update(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    form = MenuItemForm(request.POST or None, instance=item)
    if form.is_valid():
        form.save()
        return redirect('admin_menu_list')
    return render(request, 'admin/menu/update.html', {'form': form})

@admin_required
def admin_menu_delete(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    item.delete()
    return redirect('admin_menu_list')

@user_passes_test(lambda u: u.is_authenticated and u.role == 'cook')
def cook_menu_list(request):
    menu_items = MenuItem.objects.order_by('-date_available')
    return render(request, 'cook/menu_list.html', {'menu_items': menu_items})

@user_passes_test(lambda u: u.is_authenticated and u.role == 'cook')
def cook_recipe_list(request):
    recipes = Recipe.objects.all()
    return render(request, 'cook/recipe_list.html', {'recipes': recipes})

@user_passes_test(lambda u: u.is_authenticated and u.role == 'stockman')
def stockman_dashboard(request):
    return render(request, 'stockman/dashboard.html')

@user_passes_test(lambda u: u.is_authenticated and u.role == 'stockman')
def stockman_add_ingredient(request):
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('stockman_ingredients')
    else:
        form = IngredientForm()
    return render(request, 'stockman/ingredient_add.html', {'form': form})


@user_passes_test(lambda u: u.is_authenticated and u.role == 'stockman')
def stockman_ingredients(request):
    ingredients = Ingredient.objects.all()
    return render(request, 'stockman/ingredients.html', {'ingredients': ingredients})

@user_passes_test(lambda u: u.is_authenticated and u.role == 'stockman')
def stockman_transactions(request):
    transactions = InventoryTransaction.objects.order_by('-created_at')
    return render(request, 'stockman/transactions.html', {'transactions': transactions})

@user_passes_test(lambda u: u.is_authenticated and u.role == 'stockman')
def stockman_add_transaction(request):
    if request.method == 'POST':
        form = InventoryTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save()
            # Обновим склад
            if transaction.type == 'in':
                transaction.ingredient.quantity += transaction.quantity
            else:
                transaction.ingredient.quantity -= transaction.quantity
            transaction.ingredient.save()
            return redirect('stockman_transactions')
    else:
        form = InventoryTransactionForm()
    return render(request, 'stockman/add_transaction.html', {'form': form})

@user_passes_test(lambda u: u.is_authenticated and u.role == 'stockman')
def add_ingredient(request):
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('stockman_ingredients')
    else:
        form = IngredientForm()
    return render(request, 'stockman/ingredient_create.html', {'form': form})


@user_passes_test(lambda u: u.is_authenticated and u.role == 'client')
def client_menu(request):
    today = timezone.now().date()
    menu_items = MenuItem.objects.filter(date_available=today)
    return render(request, 'client/menu.html', {'menu_items': menu_items})

@user_passes_test(lambda u: u.is_authenticated and u.role == 'client')
def add_to_cart(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))

    cart = request.session.get('cart', [])
    cart.append({
        'item_id': item.id,
        'recipe_name': item.recipe.name,
        'price': float(item.price),
        'quantity': quantity,
        'total': float(item.price) * quantity
    })
    request.session['cart'] = cart
    return redirect('client_menu')

@user_passes_test(lambda u: u.is_authenticated and u.role == 'client')
def view_cart(request):
    cart = request.session.get('cart', [])
    total = sum(item['total'] for item in cart)
    return render(request, 'client/cart.html', {'cart': cart, 'total': total})

@user_passes_test(lambda u: u.is_authenticated and u.role == 'client')
def checkout(request):
    cart = request.session.get('cart', [])
    if not cart:
        return redirect('view_cart')

    order = Order.objects.create(client=request.user, status='new', paid=False)

    for item in cart:
        menu_item = get_object_or_404(MenuItem, id=item['item_id'])
        OrderItem.objects.create(
            order=order,
            menu_item=menu_item,
            quantity=item['quantity']
        )

    # Очистим корзину
    request.session['cart'] = []

    # Считаем общую сумму
    total = sum(item['total'] for item in cart)

    # Подготовим redirect на форму ЮKassa
    # (здесь просто подставим ссылку, в реальности можно генерировать динамически через API)

    payment_url = f"https://yookassa.ru/demo/pay?order_id={order.id}&amount={int(total)}"

    return render(request, 'client/order_success.html', {
        'payment_url': payment_url
    })

@user_passes_test(lambda u: u.is_authenticated and u.role == 'client')
def client_order_history(request):
    orders = Order.objects.filter(client=request.user).order_by('-created_at')
    return render(request, 'client/order_history.html', {'orders': orders})

@admin_required
def admin_reports(request):
    period = request.GET.get('period', 'day')
    now = timezone.now()

    if period == 'day':
        start_date = now - timedelta(days=1)
    elif period == 'week':
        start_date = now - timedelta(days=7)
    elif period == 'month':
        start_date = now - timedelta(days=30)
    elif period == 'year':
        start_date = now - timedelta(days=365)
    else:
        start_date = now - timedelta(days=1)

    orders = Order.objects.filter(paid=True, created_at__gte=start_date)
    total_income = sum(o.total for o in orders)

    # Самые популярные блюда
    item_stats = (
        OrderItem.objects
        .filter(order__in=orders)
        .values('menu_item__recipe__name')
        .annotate(count=Sum('quantity'))
        .order_by('-count')[:10]
    )
    popular_items = [{'name': i['menu_item__recipe__name'], 'count': i['count']} for i in item_stats]

    # Остатки на складе
    ingredients = Ingredient.objects.all()

    return render(request, 'admin/reports.html', {
        'period': period,
        'total_income': total_income,
        'popular_items': popular_items,
        'ingredients': ingredients,
    })

@admin_required
def admin_report_pdf(request):
    from datetime import timedelta
    from django.utils import timezone

    now = timezone.now()
    period = request.GET.get('period', 'day')
    period_verbose = {
        'day': 'День',
        'week': 'Неделя',
        'month': 'Месяц',
        'year': 'Год'
    }.get(period, 'День')

    delta = {
        'day': timedelta(days=1),
        'week': timedelta(days=7),
        'month': timedelta(days=30),
        'year': timedelta(days=365)
    }.get(period, timedelta(days=1))

    start_date = now - delta
    orders = Order.objects.filter(paid=True, created_at__gte=start_date)
    total_income = sum(o.total for o in orders)

    item_stats = (
        OrderItem.objects
        .filter(order__in=orders)
        .values('menu_item__recipe__name')
        .annotate(count=Sum('quantity'))
        .order_by('-count')[:10]
    )

    popular_items = [{'name': i['menu_item__recipe__name'], 'count': i['count']} for i in item_stats]

    context = {
        'total_income': total_income,
        'popular_items': popular_items,
        'timestamp': now.strftime('%d.%m.%Y %H:%M'),
        'period_verbose': period_verbose
    }

    template = get_template('admin/pdf_report.html')
    html = template.render(context)
    result = BytesIO()
    pisa.CreatePDF(BytesIO(html.encode("utf-8")), dest=result)
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{period}.pdf"'
    return response

@admin_required
def admin_stock_excel(request):
    ingredients = Ingredient.objects.all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Склад'

    # Заголовки
    headers = ['Название', 'Количество', 'Ед. изм.']
    ws.append(headers)

    # Стиль заголовков
    for col in range(1, len(headers) + 1):
        ws.cell(row=1, column=col).font = Font(bold=True)

    # Данные
    for ing in ingredients:
        ws.append([ing.name, ing.quantity, ing.unit])

    # Отправляем файл
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="stock_report.xlsx"'
    wb.save(response)
    return response

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('dashboard')

    return render(request, 'registration/login.html', {'form': form})

def custom_logout(request):
    logout(request)
    return render(request, 'registration/logged_out.html')

@admin_required
def admin_recipe_list(request):
    recipes = Recipe.objects.all()
    return render(request, 'admin/recipes/list.html', {'recipes': recipes})

def add_ingredient(request):
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            form.save()  # Сохраняем новый ингредиент в базе данных
            return redirect('ingredients_list')  # Перенаправление на список ингредиентов или другую страницу
    else:
        form = IngredientForm()
    return render(request, 'admin/ingredient_create.html', {'form': form})

def recipe_ingredient_add(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.method == 'POST':
        formset = RecipeIngredientFormSet(request.POST, instance=recipe)
        if formset.is_valid():
            formset.save()
            return redirect('some_success_url')  # Здесь должно быть успешное перенаправление
    else:
        formset = RecipeIngredientFormSet(instance=recipe)
    return render(request, 'recipe_ingredient_form.html', {'formset': formset})

def admin_recipe_delete(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    if request.method == 'POST':
        recipe.delete()
        return redirect('admin_recipe_list')  # Перенаправление на страницу списка рецептов
    
    return render(request, 'admin/recipes/confirm_delete.html', {'recipe': recipe})

@admin_required
def admin_user_list(request):
    query = request.GET.get('q', '')
    users = User.objects.all()
    if query:
        users = users.filter(username__icontains=query)
    return render(request, 'admin/users/list.html', {'users': users, 'query': query})

@admin_required
def admin_menu_list(request):
    date_filter = request.GET.get('date')
    query = request.GET.get('q', '')

    menu_items = MenuItem.objects.all()

    if date_filter:
        menu_items = menu_items.filter(date_available=date_filter)
    if query:
        menu_items = menu_items.filter(
            Q(recipe__name__icontains=query)
        )

    return render(request, 'admin/menu/list.html', {
        'menu_items': menu_items,
        'date_filter': date_filter,
        'query': query
    })


@admin_required
def admin_recipe_list(request):
    query = request.GET.get('q', '')
    recipes = Recipe.objects.all()

    if query:
        recipes = recipes.filter(name__icontains=query)

    return render(request, 'admin/recipes/list.html', {
        'recipes': recipes,
        'query': query
    })

def register_client(request):
    if request.method == 'POST':
        form = ClientRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'client'  # 👈 Назначаем роль клиента
            user.save()
            login(request, user)
            return redirect('client_dashboard')
    else:
        form = ClientRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

@user_passes_test(lambda u: u.is_authenticated and u.role == 'client')
def checkout(request):
    cart = request.session.get('cart', [])
    if not cart:
        return redirect('view_cart')

    order = Order.objects.create(client=request.user, status='new', paid=False)

    for item in cart:
        menu_item = get_object_or_404(MenuItem, id=item['item_id'])
        OrderItem.objects.create(
            order=order,
            menu_item=menu_item,
            quantity=item['quantity']
        )

    request.session['cart'] = []

    return redirect('order_payment', order_id=order.id)

@user_passes_test(lambda u: u.is_authenticated and u.role == 'client')
def order_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, client=request.user)
    total = sum(item.menu_item.price * item.quantity for item in order.items.all())

    if request.method == 'POST':
        order.paid = True
        order.status = 'paid'  # Если хочешь менять статус
        order.save()
        return redirect('checkout_success')

    return render(request, 'client/order_success.html', {
        'order': order,
        'total': total
    })
