from django.urls import path
from . import views
urlpatterns = [
path('calculation_list', views.calculation_list, name='calculation_list'),
path('calculation_add', views.calculation_add, name='calculation_add'),
path('get_clients', views.get_clients, name='get_clients'),  # Настройте URL для получения клиентов
]