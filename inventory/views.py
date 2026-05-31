from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from .models import Category, Product, Purchase


class CustomLoginView(LoginView):
    template_name = "registration/login.html"


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

# Categoría CRUD


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = "category_list.html"
    context_object_name = "categories"


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    fields = ["name"]
    template_name = "category_form.html"
    success_url = reverse_lazy('category_list')


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    fields = ["name"]
    template_name = "category_form.html"
    success_url = reverse_lazy('category_list')

# Producto CRUD


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        qs = super().get_queryset()
        name = self.request.GET.get("nombre")
        category = self.request.GET.get("categoria")
        min_stock = self.request.GET.get("min_stock")
        max_stock = self.request.GET.get("max_stock")
        if name:
            qs = qs.filter(name__icontains=name)
        if category:
            qs = qs.filter(category__id=category)
        if min_stock:
            qs = qs.filter(quantity__gte=min_stock)
        if max_stock:
            qs = qs.filter(quantity__lte=max_stock)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.all()
        # para mostrar los parámetros en el template
        ctx["filtros"] = self.request.GET
        return ctx


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    fields = ["name", "category", "unit", "quantity", "min_stock", "active"]
    template_name = "product_form.html"
    success_url = reverse_lazy('product_list')


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    fields = ["name", "category", "unit", "quantity", "min_stock", "active"]
    template_name = "product_form.html"
    success_url = reverse_lazy('product_list')

# Compra CRUD


class PurchaseListView(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = "purchase_list.html"
    context_object_name = "purchases"
    ordering = ['-date']

    def get(self, request, *args, **kwargs):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        # Paso 1: Encuentra productos con stock=0
        faltantes = Product.objects.filter(quantity=0)
        for prod in faltantes:
            existe = Purchase.objects.filter(product=prod, quantity=0).exists()
            if not existe:
                user = User.objects.filter(is_superuser=True).first() or User.objects.first()
                if user is not None:
                    Purchase.objects.create(product=prod, quantity=0, price=0, store="", user=user)
                else:
                    print("No hay usuario para asignar a la compra automática")
        # Paso 3: Continúa con el ListView estándar (usará get_queryset)
        return super().get(request, *args, **kwargs)


    def get_queryset(self):
        qs = Purchase.objects.filter(product__quantity=0)
        name = self.request.GET.get("nombre")
        category = self.request.GET.get("categoria")
        quantity = self.request.GET.get("cantidad")
        if name:
            qs = qs.filter(product__name__icontains=name)
        if category:
            qs = qs.filter(product__category__id=category)
        if quantity:
            qs = qs.filter(quantity=quantity)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.all()
        ctx["filtros"] = self.request.GET
        return ctx


class PurchaseCreateView(LoginRequiredMixin, CreateView):
    model = Purchase
    fields = ["product", "quantity", "price", "store"]
    template_name = "purchase_form.html"
    success_url = reverse_lazy('purchase_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class PurchaseUpdateView(LoginRequiredMixin, UpdateView):
    model = Purchase
    fields = ["product", "quantity", "price", "store"]
    template_name = "purchase_form.html"
    success_url = reverse_lazy('purchase_list')
