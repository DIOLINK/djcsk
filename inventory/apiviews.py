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
