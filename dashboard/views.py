from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView

from dashboard.forms import ProductCreateForm
from product.models import Product, ProductImage


class SellerAuthMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy('ota:affiliate_login')

    def handle_no_permission(self):
        return redirect('seller:login')

    def test_func(self):
        is_seller = self.request.user.is_seller
        if is_seller:
            self.seller = self.request.user.seller
        else:
            self.seller = None
        return is_seller

    def dispatch(self, request, *args, **kwargs):
        self.seller = None
        return super(SellerAuthMixin, self).dispatch(request, *args, **kwargs)


class SellerLoginView(LoginView):
    template_name = 'dashboard/auth/login.html'

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_redirect_url(self):
        url = reverse_lazy('seller:index')
        return url


class SellerLogoutView(SellerAuthMixin, LogoutView):

    def get_next_page(self):
        url = reverse_lazy('seller:login')
        return url


class IndexView(SellerAuthMixin, View):
    def get(self, request):
        return render(request, 'dashboard/base.html')


class ProductListView(SellerAuthMixin, ListView):
    model = Product
    template_name = 'dashboard/product/list.html'
    paginate_by = 15

    def get_queryset(self):
        return Product.objects.filter(seller__user=self.request.user)


class ProductCreateView(SellerAuthMixin, CreateView):
    model = Product
    form_class = ProductCreateForm
    template_name = 'dashboard/product/create.html'


class ProductImageView(SellerAuthMixin, View):
    model = ProductImage
    paginate_by = 15

    def get(self, request):
        product_image_queryset = ProductImage.objects.filter(seller__user=request.user)
        product_image_list = [
            {"id": str(product_image.id), "url": product_image.file.url} for product_image in product_image_queryset
        ]
        return JsonResponse({"result": True, "data": product_image_list}, safe=False)
