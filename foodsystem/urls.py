from django.contrib import admin
from django.urls import path, include
from core import views as core_views  # ✅ Импортируем вьюхи

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', include('core.urls')),  # Все маршруты из core
    
    # ✅ Добавь эти две строки:
    path('login/', core_views.custom_login, name='login'),
    path('logout/', core_views.custom_logout, name='logout'),
]
