from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Products
    path('products/', views.product_list_view, name='product_list'),
    path('products/<int:pk>/', views.product_detail_view, name='product_detail'),
    path('products/create/', views.product_create_view, name='product_create'),
    path('products/<int:pk>/update/', views.product_update_view, name='product_update'),
    path('products/<int:pk>/delete/', views.product_delete_view, name='product_delete'),
    
    # Customers
    path('customers/', views.customer_list_view, name='customer_list'),
    path('customers/create/', views.customer_create_view, name='customer_create'),
    path('customers/<int:pk>/update/', views.customer_update_view, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete_view, name='customer_delete'),
    
    # Sales
    path('sales/', views.sale_list_view, name='sale_list'),
    path('sales/create/', views.sale_create_view, name='sale_create'),
    path('sales/<int:pk>/update/', views.sale_update_view, name='sale_update'),
    path('sales/<int:pk>/delete/', views.sale_delete_view, name='sale_delete'),

    path('category/add/', views.category_create_view, name='category_create'),

    path('brand/add/', views.brand_create_view, name='brand_create'),
    path('sales/manage/<int:pk>/<str:action>/', views.manage_sale_status, name='manage_sale_status'),
]