from rest_framework import viewsets
from .models import Category, Product, Purchase
from .serializers import CategorySerializer, ProductSerializer, PurchaseSerializer
from rest_framework.permissions import IsAuthenticated

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.select_related('product', 'user').all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]
