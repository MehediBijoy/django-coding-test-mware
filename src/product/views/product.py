from django.views import generic
from django.db.models.query import QuerySet

from product.models import Variant, Product, ProductVariant


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context


class ProductListView(generic.ListView):
    model = Product
    paginate_by = 5

    template_name = 'products/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        variants = dict()
        for instance in Variant.objects.filter(active=True):
            variants[instance.title] = ProductVariant.objects.filter(
                variant=instance).values('variant_title').distinct()
        context['variants'] = variants
        context['form_values'] = self.request.GET
        return context

    def get_queryset(self) -> QuerySet[Product]:
        queryset = super().get_queryset()

        product_title = self.request.GET.get('title')
        product_variant = self.request.GET.get('variant')
        product_price_from = self.request.GET.get('price_from')
        product_price_to = self.request.GET.get('price_to')
        product_date = self.request.GET.get('date')

        if product_title:
            queryset = queryset.filter(title__icontains=product_title)

        if product_variant:
            queryset = queryset.filter(
                productvariant__variant_title=product_variant
            )

        # Here is the ambiguity from django
        # by default django handle distinct but here not work
        # That's why I use distinct method here.
        if product_price_from:
            queryset = queryset.filter(
                product_variant_prices__price__gte=product_price_from
            ).distinct()

        if product_price_to:
            queryset = queryset.filter(
                product_variant_prices__price__lte=product_price_to
            ).distinct()

        if product_date:
            queryset = queryset.filter(created_at__gte=product_date)

        return queryset
