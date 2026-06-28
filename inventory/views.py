from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from .forms import ProductForm
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

    def get_queryset(self):
        return Category.objects.annotate(product_count=Count('products'))


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    fields = ["name"]
    template_name = "category_form.html"
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Categoría "{self.object.name}" creada correctamente.')
        return response


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    fields = ["name"]
    template_name = "category_form.html"
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Categoría "{self.object.name}" actualizada correctamente.')
        return response


class CategoryDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        if category.products.exists():
            messages.error(request, f'No se puede eliminar "{category.name}" porque tiene productos asociados.')
        else:
            name = category.name
            category.delete()
            messages.success(request, f'Categoría "{name}" eliminada correctamente.')
        return redirect('category_list')

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
    form_class = ProductForm
    template_name = "product_form.html"
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Producto "{self.object.name}" creado correctamente.')
        return response


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "product_form.html"
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Producto "{self.object.name}" actualizado correctamente.')
        return response


class ProductDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        name = product.name
        product.delete()
        messages.success(request, f'Producto "{name}" eliminado correctamente.')
        return redirect('product_list')

# Compra CRUD


class PurchaseListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "purchase_list.html"
    context_object_name = "products"

    def get_queryset(self):
        qs = Product.objects.filter(quantity__lte=0)
        name = self.request.GET.get("nombre")
        category = self.request.GET.get("categoria")
        if name:
            qs = qs.filter(name__icontains=name)
        if category:
            qs = qs.filter(category__id=category)
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
        response = super().form_valid(form)
        product = form.instance.product
        product.quantity += form.cleaned_data['quantity']
        product.save()
        messages.success(self.request, 'Compra registrada correctamente.')
        return response


class PurchaseUpdateView(LoginRequiredMixin, UpdateView):
    model = Purchase
    fields = ["product", "quantity", "price", "store"]
    template_name = "purchase_form.html"
    success_url = reverse_lazy('purchase_list')

    def form_valid(self, form):
        old_quantity = self.get_object().quantity
        old_product = self.get_object().product

        response = super().form_valid(form)

        new_quantity = form.instance.quantity
        new_product = form.instance.product

        if old_product.pk != new_product.pk:
            old_product.quantity -= old_quantity
            old_product.save()
            new_product.quantity += new_quantity
            new_product.save()
        else:
            delta = new_quantity - old_quantity
            new_product.quantity += delta
            new_product.save()

        messages.success(self.request, 'Compra actualizada correctamente.')
        return response
