from rest_framework import serializers
from .models import Category, Product, Purchase

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.StringRelatedField(source='category', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'category_name', 'unit',
                  'quantity', 'min_stock', 'price', 'active']

class PurchaseSerializer(serializers.ModelSerializer):
    product_name = serializers.StringRelatedField(source='product', read_only=True)
    user_name = serializers.StringRelatedField(source='user', read_only=True)

    class Meta:
        model = Purchase
        fields = ['id', 'product', 'product_name', 'user', 'user_name',
                  'date', 'quantity', 'price', 'store']
        read_only_fields = ['user', 'date']
