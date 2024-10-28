from django.urls import path
from . import views
from .views import filter_nomenclature
from . import admin
urlpatterns = [
    # Другие URL-обработчики вашего приложения
    # URL для получения технологических узлов
    path('api/technological-links/', views.get_technological_links, name='get_technological_links'),
    path('api/productcomposition/filter_nomenclature/', filter_nomenclature, name='filter_nomenclature'),    # URL для получения технологических операций
    path('api/technological-operations/', views.get_technological_operations, name='get_technological_operations'),
    path('api/nomenclature/', views.get_nomenclature, name='get_nomenclature'),
    path('api/parameters_product/', views.get_parameters_product, name='get_parameters_product'),
    path('api/get_nomenclature_price/', views.get_nomenclature_price, name='get_nomenclature_price'),
    path('api/update_parameters/', views.update_parameters_product, name='update_parameters_product'),
    path('api/update_selected_operations/', views.update_selected_operations, name='update_selected_operations'),
    path('api/update_selected_nomenclature/', views.update_selected_nomenclature, name='update_selected_nomenclature'),
    path('edit-default-parameters/', views.edit_default_parameters, name='edit-default-parameters'),
    path('check-folder-type/', views.check_folder_type, name='check_folder_type'),
    path('load-initial-folders/', views.load_initial_folders, name='load_initial_folders'),
    # path('api/bitrix/<str:api_method>/', views.BitrixProxy.as_view(), name='bitrix-proxy'),
    path('api/bitrix/', views.get_current_user, name='bitrix'),
    ]
