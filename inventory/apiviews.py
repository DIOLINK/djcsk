from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, Purchase
from .serializers import CategorySerializer, ProductSerializer, PurchaseSerializer
from rest_framework.permissions import IsAuthenticated

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name']
    search_fields = ['name']
    ordering_fields = ['id', 'name']

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'active', 'unit']
    search_fields = ['name', 'category__name']
    ordering_fields = ['id', 'name', 'quantity', 'price', 'min_stock', 'category__name']

class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.select_related('product', 'user').all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'user', 'date', 'store']
    search_fields = ['product__name', 'store']
    ordering_fields = ['id', 'date', 'quantity', 'price', 'product__name', 'store']

    def perform_create(self, serializer):
        purchase = serializer.save(user=self.request.user)
        purchase.product.quantity += purchase.quantity
        purchase.product.save()

    def perform_update(self, serializer):
        old_purchase = self.get_object()
        old_quantity = old_purchase.quantity
        old_product = old_purchase.product

        purchase = serializer.save()

        if old_product.pk != purchase.product.pk:
            old_product.quantity -= old_quantity
            old_product.save()
            purchase.product.quantity += purchase.quantity
            purchase.product.save()
        else:
            delta = purchase.quantity - old_quantity
            purchase.product.quantity += delta
            purchase.product.save()
