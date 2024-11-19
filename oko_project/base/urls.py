from django.urls import path
from . import views
from .views import filter_nomenclature
from . import admin
urlpatterns = [
    path('', views.home, name='home'),
    path('get-item-types/<int:product_id>/', views.get_item_types, name='get_item_types'),
    path('api/parameters_product_bitrix/', views.get_parameters_product_bitrix, name='get_parameters_product_bitrix'),
    path('api/update_parameters_product_bitrix/', views.update_parameters_product_bitrix, name='update_parameters_product_bitrix'),
    path('filter-item/', views.filter_item, name='filter_item'),
    path('calculation_list', views.calculation_list, name='calculation_list'),
    path('calculation_preview', views.calculation_preview, name='calculation_preview'),
    path('calculation_previews', views.calculation_previews, name='calculation_previews'),
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
    # path('api/bitrix/', views.get_current_user, name='bitrix'),
    path("api/bitrix/user/", views.get_bitrix_user, name="bitrix_user"),
    path('api/bitrix/proxy/', views.bitrix_proxy, name='bitrix_proxy'),
    path('api/bitrix/bind/', views.bind_application, name='bind_application'),
    path('api/bitrix/get_available_placements/', views.get_available_placements, name='get_available_placements'),
    path('install/', views.install, name='bitrix_install'),
    path('get_nomenklatura_by_folder/<int:folder_id>/', views.get_nomenklatura_by_folder, name='get_nomenklatura_by_folder'),
    path('get_production_operation_by_folder/<int:folder_id>/', views.get_production_operation_by_folder, name='get_production_operation_by_folder'),
    path('get_add_nomenklature_by_folder/<int:folder_id>/', views.get_add_nomenklature_by_folder, name='get_add_nomenklature_by_folder'),
    path('get_technical_operations_by_folder/<int:folder_id>/', views.get_technical_operations_by_folder, name='get_technical_operations_by_folder'),
    path('api/get_filtered_fields/', views.get_filtered_fields, name='get_filtered_fields'),
    path('api/get_technology_of_product/', views.get_technology_of_product, name='get_technology_of_product'),
    path('api/get_technology_of_goods/', views.get_technology_of_goods, name='get_technology_of_goods'),
    path('api/get_nomenclature_by_techoperation/', views.get_nomenclature_by_techoperation, name='get_nomenclature_by_techoperation'),
    path('api/get_folder_name_by_technology/', views.get_folder_name_by_technology, name='get_folder_name_by_technology'),
    path('create-deal/', views.create_deal, name='create_deal'),
    ]

    
