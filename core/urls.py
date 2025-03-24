from django.urls import path
from . import views

urlpatterns = [
    # Главный вход и редирект по ролям
    path('', views.dashboard_redirect, name='dashboard'),

    # Панели для ролей
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('cook/dashboard/', views.cook_dashboard, name='cook_dashboard'),
    path('stockman/dashboard/', views.stockman_dashboard, name='stockman_dashboard'),
    path('client/dashboard/', views.client_dashboard, name='client_dashboard'),

    # CRUD пользователей (для администратора)
    path('admin/users/', views.admin_user_list, name='admin_user_list'),
    path('admin/users/create/', views.admin_user_create, name='admin_user_create'),
    path('admin/users/<int:user_id>/edit/', views.admin_user_update, name='admin_user_update'),
    path('admin/users/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),

    # Меню
    path('admin/menu/', views.admin_menu_list, name='admin_menu_list'),
    path('admin/menu/create/', views.admin_menu_create, name='admin_menu_create'),
    path('admin/menu/<int:item_id>/edit/', views.admin_menu_update, name='admin_menu_update'),
    path('admin/menu/<int:item_id>/delete/', views.admin_menu_delete, name='admin_menu_delete'),

    # Создание ингредиента (вы забыли запятую в предыдущем коде)
    path('admin/ingredients/create/', views.add_ingredient, name='add_ingredient'),

    # Повара
    path('cook/menu/', views.cook_menu_list, name='cook_menu_list'),
    path('cook/recipes/', views.cook_recipe_list, name='cook_recipe_list'),

    # Кладовщики
    path('stockman/dashboard/', views.stockman_dashboard, name='stockman_dashboard'),
    path('stockman/ingredients/', views.stockman_ingredients, name='stockman_ingredients'),
    path('stockman/ingredients/create/', views.add_ingredient, name='add_ingredient'),
    path('stockman/transactions/', views.stockman_transactions, name='stockman_transactions'),
    path('stockman/transactions/add/', views.stockman_add_transaction, name='stockman_add_transaction'),
    path('stockman/ingredients/add/', views.stockman_add_ingredient, name='stockman_add_ingredient'),


    # Клиенты
    path('client/menu/', views.client_menu, name='client_menu'),
    path('client/cart/', views.view_cart, name='view_cart'),
    path('client/cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('client/checkout/', views.checkout, name='checkout'),
    path('client/orders/', views.client_order_history, name='client_order_history'),

    # Административные отчеты
    path('admin/reports/', views.admin_reports, name='admin_reports'),
    path('admin/reports/pdf/', views.admin_report_pdf, name='admin_report_pdf'),
    path('admin/reports/excel/', views.admin_stock_excel, name='admin_stock_excel'),
    path('admin/recipes/', views.admin_recipe_list, name='admin_recipe_list'),
    path('admin/recipes/create/', views.admin_recipe_create, name='admin_recipe_create'),
    path('admin/recipes/<int:recipe_id>/edit/', views.admin_recipe_update, name='admin_recipe_update'),
    path('admin/recipes/<int:recipe_id>/delete/', views.admin_recipe_delete, name='admin_recipe_delete'),
    path('client/checkout/success/', views.checkout_success, name='checkout_success'),

    path('client/checkout/', views.checkout, name='checkout'),
    path('client/checkout/success/', views.checkout_success, name='checkout_success'),

    path('register/', views.register_client, name='register_client'),
    # Авторизация и выход
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('client/order/<int:order_id>/pay/', views.order_payment, name='order_payment'),
    




]
