from django.urls import path
from . import views

app_name = 'pos'  
urlpatterns = [
    path('', views.index, name='index'),
    path('dash', views.dash, name='dash'), 
    path('add_stock/', views.dash, name='add_stock'),

    # Inventory CRUD
    path('inventory/', views.inventory, name='inventory'),
    path('inventory/add/', views.stock_create, name='stock_create'),
    path('inventory/<int:pk>/edit/', views.stock_update, name='stock_update'),
    path('inventory/<int:pk>/delete/', views.stock_delete, name='stock_delete'),
    path('inventory/export/pdf/', views.inventory_export_pdf, name='inventory_export_pdf'),

    path('expenses/', views.expense_list, name='expenses'),
    path('expenses/add/', views.expense_create, name='expense_add'),
    path('expenses/<int:pk>/edit/', views.expense_update, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),

    path('injections/', views.injection_list, name='injections'),
    path('injections/add/', views.injection_create, name='injection_add'),
    path('injections/<int:pk>/edit/', views.injection_update, name='injection_edit'),
    path('injections/<int:pk>/delete/', views.injection_delete, name='injection_delete'),

    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]