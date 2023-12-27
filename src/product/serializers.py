from rest_framework import serializers

from product.models import Product, ProductVariantPrice, ProductVariant, Variant


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = '__all__'


class ProductVariantPriceSerializer(serializers.ModelSerializer):
    variants = serializers.JSONField(write_only=True)

    class Meta:
        model = ProductVariantPrice
        exclude = ['product']

    def create(self, validated_data):
        del validated_data['variants']
        return super().create(validated_data)


class ProductSerializer(serializers.ModelSerializer):
    product_variant_prices = ProductVariantPriceSerializer(
        many=True, required=True)

    class Meta:
        model = Product
        fields = ('title', 'description', 'sku', 'product_variant_prices')

    def validate(self, data):
        product_variant_prices = data.get('product_variant_prices', [])
        if not product_variant_prices:
            raise serializers.ValidationError(
                {'product_variant_prices': "product variant prices is required."})
        return data

    def create(self, validated_data):
        product_prices_data = validated_data.pop('product_variant_prices', [])
        product = super().create(validated_data)

        for product_variant in product_prices_data:
            variants_data = product_variant.get('variants', {})

            variant_one = self.prepare_product_variant(
                'size', variants_data.get('size'), product)
            variant_two = self.prepare_product_variant(
                'color', variants_data.get('color'), product)
            variant_three = self.prepare_product_variant(
                'style', variants_data.get('style'), product)

            product_variant_serializer = ProductVariantPriceSerializer(
                data=product_variant)
            product_variant_serializer.is_valid(raise_exception=True)
            product_variant_serializer.save(
                product=product,
                product_variant_one=variant_one,
                product_variant_two=variant_two,
                product_variant_three=variant_three
            )
        return product

    def prepare_product_variant(self, key, value, product):
        if key and value:
            variant = Variant.objects.get(title__iexact=key)
            variant_serializer = ProductVariantSerializer(data={
                'variant_title': value, 'product': product.id, 'variant': variant.id
            })
            variant_serializer.is_valid(raise_exception=True)
            return variant_serializer.save()
