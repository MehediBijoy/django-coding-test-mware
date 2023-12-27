from django import forms

from product.models import Product, Variant, ProductVariantPrice, ProductVariant


class VariantForm(forms.ModelForm):
    class Meta:
        model = Variant
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'active'})
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class ProductVariantPriceForm(forms.ModelForm):
    color = forms.CharField(label='Color', max_length=20)
    size = forms.CharField(label='Size', max_length=20)
    style = forms.CharField(label='Style', max_length=20, required=False)

    class Meta:
        model = ProductVariantPrice
        fields = ['color', 'size', 'style', 'price', 'stock']

    def __init__(self, *args, **kwargs):
        super(ProductVariantPriceForm, self).__init__(*args, **kwargs)

        self.fields['size'].initial = self.get_product_variant('one')
        self.fields['color'].initial = self.get_product_variant('two')
        self.fields['style'].initial = self.get_product_variant('three')

    def get_product_variant(self, variant_title):
        try:
            return ProductVariant.objects.get(
                id=getattr(self.instance,
                           f'product_variant_{variant_title}_id')
            ).variant_title
        except ProductVariant.DoesNotExist:
            return None
