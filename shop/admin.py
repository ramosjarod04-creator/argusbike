from django.contrib import admin
from .models import Category, Brand, BikeProduct, Customer, Sale, StockHistory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(BikeProduct)
class BikeProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'brand', 'category', 'price', 'stock_quantity', 'status', 'is_active']
    list_filter = ['status', 'category', 'brand', 'condition', 'is_featured', 'is_active']
    search_fields = ['sku', 'name', 'description']
    readonly_fields = ['status', 'created_by', 'created_at', 'updated_at']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'email', 'phone', 'city', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    list_filter = ['city']


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['sale_id', 'customer', 'product', 'quantity', 'final_amount', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['sale_id', 'customer__first_name', 'customer__last_name']
    readonly_fields = ['sale_id', 'unit_price', 'total_amount', 'final_amount', 'created_by']


@admin.register(StockHistory)
class StockHistoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'action', 'quantity_change', 'new_quantity', 'created_by', 'created_at']
    list_filter = ['action', 'created_at']
    search_fields = ['product__sku', 'product__name']
    readonly_fields = ['created_at', 'created_by']