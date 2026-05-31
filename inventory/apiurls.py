from rest_framework import routers
from .apiviews import CategoryViewSet, ProductViewSet, PurchaseViewSet

router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'purchases', PurchaseViewSet)

urlpatterns = router.urls
