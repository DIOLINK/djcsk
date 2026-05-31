from django.contrib import admin
from .models import Category, Product, Purchase

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity', 'min_stock', 'active')
    list_filter = ('category', 'active')
    search_fields = ('name',)

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'date', 'price', 'store')
    list_filter = ('product', 'user', 'store')
    search_fields = ('product__name', 'store', 'user__username')
