from django.urls import path
from . import views
urlpatterns = [
path('calculation_list', views.calculation_list, name='calculation_list'),
path('calculation_add', views.calculation_add, name='calculation_add'),
path('authoritation', views.authoritation, name='authoritation'),
path('callback/', views.bitrix_callback, name='bitrix_callback'),
path('api/create-calculation/', views.create_calculation, name='create_calculation'),
path('api/update-calculation/<int:calculation_id>', views.update_calculation, name='update_calculation'),
path('delete-calculation/<int:pk>/', views.delete_calculation, name='delete_calculation'),
]