import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from dashboard.forms import ProductCreateForm, ShowCreateForm
from product.models import Product, ProductImage
from show.models import Show, ShowError, ShowStatus


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

    def get_success_url(self):
        return reverse('seller:product')

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        product = form.save(commit=False)
        product.seller = self.request.user.seller
        product.save()
        self.object = product
        return super().form_valid(form)


class ProductUpdateView(SellerAuthMixin, UpdateView):
    model = Product
    form_class = ProductCreateForm
    template_name = 'dashboard/product/update.html'
    context_object_name = 'product'

    def get_success_url(self):
        url = reverse_lazy('seller:product_update', args=[self.kwargs['product_id']])
        return str(url)

    def get_object(self, queryset=None):
        product = get_object_or_404(Product, id=self.kwargs['product_id'])
        return product


class ProductAjaxView(SellerAuthMixin, View):
    def get(self, request):
        product_qs = Product.objects.select_related('thumbnail').filter(seller__user=request.user)
        query = None if request.GET.get('query', '') == '' else request.GET.get('query')
        if query:
            try:
                u = uuid.UUID(query, version=4)
            except:
                product_qs = product_qs.filter(
                    Q(name__icontains=query)
                )
            else:
                product_qs = product_qs.filter(id=u)
        response_data = {"result": True, "data": [
            {
                'id': str(product.id), 'name': product.name, 'thumbnail': product.thumbnail.file.url,
                "original_price": product.original_price, "sale_price": product.sale_price
            } for product in product_qs
        ]}
        return JsonResponse(response_data)


class ProductImageView(SellerAuthMixin, View):

    def get(self, request):
        product_image_id = request.GET.get('imageId')
        product_image = ProductImage.objects.get(id=product_image_id, seller__user=request.user)
        data = {"id": str(product_image.id), "url": product_image.file.url}
        return JsonResponse({"result": True, "data": data}, safe=False)

    def post(self, request):
        file = request.FILES['productImage']
        product_image = ProductImage.objects.create(
            file=file, seller=request.user.seller
        )
        data = {"id": str(product_image.id), "url": product_image.file.url}
        return JsonResponse({"result": True, "data": data}, safe=False)


class ShowListView(SellerAuthMixin, ListView):
    model = Show
    template_name = 'dashboard/show/list.html'
    paginate_by = 15

    def get_queryset(self):
        return Show.objects.select_related('product').exclude(status=ShowStatus.DELETE).filter(
            product__seller__user=self.request.user)

    def render_to_response(self, context, **response_kwargs):
        messages.success(self.request, 'test')
        return super(ShowListView, self).render_to_response(context, **response_kwargs)


class ShowCreateView(SellerAuthMixin, CreateView):
    model = Show
    form_class = ShowCreateForm
    template_name = 'dashboard/show/create.html'

    def get_success_url(self):
        return reverse('seller:show')


class ShowUpdateView(SellerAuthMixin, UpdateView):
    model = Show
    form_class = ShowCreateForm
    template_name = 'dashboard/show/update.html'
    context_object_name = 'show'

    def get_success_url(self):
        url = reverse_lazy('seller:show_update', args=[self.kwargs['show_id']])
        return str(url)

    def get_object(self, queryset=None):
        product = get_object_or_404(Show, Q(id=self.kwargs['show_id']) & Q(status=ShowStatus.PENDING))
        return product


class ShowDeleteView(SellerAuthMixin, View):
    def post(self, request, show_id):
        try:
            show = Show.objects.get(id=show_id, product__seller__user=self.request.user)
            show.delete_show(request.user)
            response_data = {"result": True, "data": None}
        except Show.DoesNotExist:
            response_data = {"result": False, "msg": "존재하지 않는 SHOW 입니다."}
        except ShowError as e:
            response_data = {"result": False, "msg": e.msg}
        return JsonResponse(response_data)


class ShowView(SellerAuthMixin, View):
    def get(self, request, show_id):
        show = Show.objects.select_related('product').prefetch_related('chat_set').get(
            id=show_id, status=ShowStatus.ONAIR, product__seller__user=request.user
        )
        last_chat_id = show.chat_set.last().id
        return render(request, 'dashboard/show/show.html', context={"show": show, "last_chat_id": last_chat_id})
