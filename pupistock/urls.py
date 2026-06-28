from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from inventory import views as inv_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', inv_views.CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', inv_views.CustomLogoutView.as_view(), name='logout'),
    path('', inv_views.DashboardView.as_view(), name='dashboard'),
    path('categorias/', inv_views.CategoryListView.as_view(), name='category_list'),
    path('categorias/nueva/', inv_views.CategoryCreateView.as_view(), name='category_create'),
    path('categorias/<int:pk>/editar/', inv_views.CategoryUpdateView.as_view(), name='category_update'),
    path('categorias/<int:pk>/eliminar/', inv_views.CategoryDeleteView.as_view(), name='category_delete'),
    path('productos/', inv_views.ProductListView.as_view(), name='product_list'),
    path('productos/nuevo/', inv_views.ProductCreateView.as_view(), name='product_create'),
    path('productos/<int:pk>/editar/', inv_views.ProductUpdateView.as_view(), name='product_update'),
    path('productos/<int:pk>/eliminar/', inv_views.ProductDeleteView.as_view(), name='product_delete'),
    path('compras/', inv_views.PurchaseListView.as_view(), name='purchase_list'),
    path('compras/nueva/', inv_views.PurchaseCreateView.as_view(), name='purchase_create'),
    path('compras/<int:pk>/editar/', inv_views.PurchaseUpdateView.as_view(), name='purchase_update'),
    path('api/v1/', include('inventory.apiurls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
