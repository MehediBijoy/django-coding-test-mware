from django.views import generic
from django.urls import reverse_lazy
from django.db.models import Q
from django.db.models.query import QuerySet
from django.forms.models import inlineformset_factory

from product.models import Variant, Product, ProductVariant, ProductVariantPrice
from product.forms import ProductForm, ProductVariantPriceForm


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
            query_q = Q(
                product_variant_prices__product_variant_one__variant_title=product_variant) | \
                Q(product_variant_prices__product_variant_two__variant_title=product_variant) | \
                Q(product_variant_prices__product_variant_three__variant_title=product_variant)
            queryset = queryset.filter(query_q).distinct()

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


class ProductUpdateView(generic.UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/edit.html'
    success_url = reverse_lazy('product:list.product')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        formset = inlineformset_factory(
            Product, ProductVariantPrice,
            form=ProductVariantPriceForm,
            extra=1, can_delete=True
        )

        if self.request.POST:
            context['formset'] = formset(
                self.request.POST, instance=self.object)
        else:
            context['formset'] = formset(instance=self.object)

        return context

    def form_valid(self, form):
        context = self.get_context_data(form=form)
        formset = context['formset']
        if formset.is_valid():
            form.save()
            formset.save()

            for variant_form in formset:
                if not variant_form.cleaned_data.get('DELETE'):
                    color = variant_form.cleaned_data.get('color')
                    size = variant_form.cleaned_data.get('size')
                    style = variant_form.cleaned_data.get('style')
                    product = variant_form.cleaned_data.get('product')

                    self.handle_variant('Size', size, product,
                                        variant_form, 'product_variant_one')
                    self.handle_variant('Color', color, product,
                                        variant_form, 'product_variant_two')
                    self.handle_variant('Style', style, product,
                                        variant_form, 'product_variant_three')
            return super().form_valid(form)
        return self.render_to_response(context)

    def handle_variant(self, variant_title, variant_value, product, form, field_name):
        if variant_value:
            variant = Variant.objects.get(title=variant_title)
            product_variant, created = ProductVariant.objects.get_or_create(
                variant_title=variant_value, variant=variant, product=product
            )
            setattr(form.instance, field_name, product_variant)
            form.instance.save()
