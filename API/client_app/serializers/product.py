import calendar
import datetime
from rest_framework import serializers
from API.settings import PRODUCT_STATES, BAG_SIZE, BAG_YEARS, BAG_CONDITIONS, DELIVERY_TYPE, ORDER_STATUS
from admin_app.serializers import BrandSerializer, ColorSerializer, MaterialSerializer
from client_app.serializers.media import ImageSerializer, VideoSerializer
from client_app.models import Product, Media, Brand, Color, Material, Image, Video, Favorite, Address, Order
from API.static import send_notification

MAPPING_PRODUCTS = [
    ('media_pk', 'media'),
    ('brand_pk', 'brand'),
    ('color_pk', 'color'),
    ('material_pk', 'material'),
    ('delivery_kit_pk', 'delivery_kit')
]


def user_product(product_id, user):
    if user is None:
        raise ValueError('User not passed')
    if product_id is None:
        raise ValueError('Id product not passed')
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        raise ValueError('Product not found')
    return user, product


def get_data(validated_data, user):
    data = {}
    try:
        data['media'] = Media.objects.get(pk=validated_data['media_pk'])
        data['brand'] = Brand.objects.get(pk=validated_data['brand_pk'])
        data['color'] = Color.objects.get(pk=validated_data['color_pk'])
        data['material'] = Material.objects.get(pk=validated_data['material_pk'])
        data['delivery_kit'] = Address.objects.get(pk=validated_data['delivery_kit_pk'], user=user)
    except (Media.DoesNotExist, Brand.DoesNotExist, Color.DoesNotExist, Material.DoesNotExist, Address.DoesNotExist):
        raise ValueError('One (or more) of media, brand, color, material, address does not exist')
    return data


def order_submit_valid(product, date_start):
    filter_order = Order.objects.filter(product=product, date_start__lte=date_start, date_end__gte=date_start, state=4)
    return len(filter_order) == 0


class AddProductSerializer(serializers.ModelSerializer):
    media_pk = serializers.IntegerField(min_value=1)
    brand_pk = serializers.IntegerField(min_value=1)
    color_pk = serializers.IntegerField(min_value=1)
    material_pk = serializers.IntegerField(min_value=1)
    delivery_kit_pk = serializers.IntegerField(min_value=1)

    class Meta:
        model = Product
        fields = ['id', 'model', 'media_pk', 'brand_pk', 'color_pk', 'material_pk', 'conditions', 'year', 'size', 'description', 'price_retail', 'price_offer', 'delivery_type']
        extra_kwargs = {
            'id': {'required': False},
            'description': {'required': False},
            'price_retail': {'required': True, 'min_value': 0},
            'price_offer': {'required': True, 'min_value': 0},
            'delivery_type': {'required': True, 'min_value': 1},
        }

    def save(self, **kwargs):
        user = kwargs.get('user')
        if user is None:
            raise ValueError('User not passed')
        objects_data = get_data(self.validated_data, user)
        for item in MAPPING_PRODUCTS:
            self.validated_data.pop(item[0])
            self.validated_data[item[1]] = objects_data[item[1]]
        return Product.objects.create(**self.validated_data, owner=user)

    def update(self, instance, validated_data):
        objects_data = get_data(validated_data)
        instance.media = objects_data['media']
        instance.brand = objects_data['brand']
        instance.color = objects_data['color']
        instance.material = objects_data['material']
        instance.price_retail = validated_data['price_retail']
        instance.save()
        return instance


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'model', 'media', 'brand', 'color', 'material', 'conditions', 'year', 'size', 'description', 'price_retail', 'price_offer', 'delivery_type', 'status']
        extra_kwargs = {
            'id': {'required': False},
        }

    def serialize_data(self, admin=False):
        if not self.instance:
            return {}
        images = Image.objects.filter(media=self.instance.media, active=True)
        videos = Video.objects.filter(media=self.instance.media, active=True)
        data = {
            'id': self.instance.pk,
            'model': self.instance.model,
            'media': {
                'images': ImageSerializer(instance=images, many=True).data,
                'videos': VideoSerializer(instance=videos, many=True).data
            },
            'brand': BrandSerializer(instance=self.instance.brand).data,
            'color': ColorSerializer(instance=self.instance.color).data,
            'material': MaterialSerializer(instance=self.instance.material).data,
            'conditions': BAG_CONDITIONS[self.instance.conditions - 1],
            'year': BAG_YEARS[self.instance.year - 1],
            'size': BAG_SIZE[self.instance.size - 1],
            'price_retail': self.instance.price_retail,
            'price_offer': self.instance.proce_offer,
            'status': PRODUCT_STATES[self.instance.status - 1],
            'delivery_type': DELIVERY_TYPE[self.instance.delivery_type - 1 if self.instance.delivery_type != 12 else 2]
        }
        if admin:
            data['media_verify'] = VideoSerializer(instance=self.instance.media_verify).data
        return data


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['product', 'state', 'price', 'date_start', 'date_end', 'delivery_mode']

    def serialize_data(self):
        if not self.instance:
            return {}
        return {
            'product': ProductSerializer(instance=self.instance.product).serialize_data(),
            'state': ORDER_STATUS[self.instance.status - 1],
            'price': self.instance.price,
            'date_start': self.instance.date_start,
            'date_end': self.instance.date_end,
            'delivery_mode': DELIVERY_TYPE[self.instance.delivery_type - 1]
        }


class FavoriteProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)

    class Meta:
        fields = ['product_id']

    def save(self, **kwargs):
        user, product = user_product(self.product_id, kwargs.get('user'))
        if product.status != 4 and product.owner != user:
            raise ValueError('Product status not valid')
        try:
            favorite = Favorite.objects.get(user=user)
        except Favorite.DoesNotExist:
            favorite = Favorite.objects.create(user=user)
        if len(favorite.products.filter(pk=product.pk)) != 0:
            raise ValueError('Product already in your favorites')
        favorite.products.add(product)
        send_notification(product.owner, 'Prodotto aggiunto nei preferiti', 'Un tuo prodotto è stato aggiunto nei preferiti')

    def remove(self, **kwargs):
        user, product = user_product(self.product_id, kwargs.get('user'))
        try:
            favorite = Favorite.objects.get(user=user, products__pk=product.pk)
        except Favorite.DoesNotExist:
            raise ValueError('This user doesn\'t have this product on his favorites')
        favorite.delete()


class SubmitOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['date_start', 'date_end', 'delivery_mode', 'product_id']

    def save(self, **kwargs):
        user = kwargs.get('user')
        product = kwargs.get('product')
        if not order_submit_valid(product, self.validated_data['date_start']):
            raise ValueError('Data start not valid')
        if self.validated_data['delivery_mode'] not in [1, 2]:
            raise ValueError('Delivery mode not vaid')
        self.validated_data['product'] = product
        self.validated_data['user'] = user
        send_notification(product.owner, "Nuova offerta", "Hai ricevuto una offerta per una borsa")
        return Order.objects.create(**self.validated_data)


class AvailabilityDatesSerializer(serializers.ModelSerializer):
    month = serializers.IntegerField(min_value=1, max_value=12, default=datetime.datetime.now().month)
    year = serializers.IntegerField(min_value=2021, default=datetime.datetime.now().year)

    class Meta:
        fields = ['month', 'year']

    def serialize(self, product):
        num_days = calendar.monthrange(self.validated_data['year'], self.validated_data['month'])
        date_start = datetime.datetime(self.validated_data['year'], self.validated_data['month'], 1)
        date_end = datetime.datetime(self.validated_data['year'], self.validated_data['month'], num_days)
        filters = Order.objects.filter(product=product, date_start__gte=date_start, date_start__lte=date_end).order_by('date_start')
        available_dates = [i for i in range(1, num_days)]
        for item in filters:
            day = item.date_start.day
            end_day = item.date_end.day if item.date_start.month == date_end.month else num_days
            while day != end_day:
                available_dates.remove(day)
                day += 1
        return {'month': self.validated_data['month'], 'year': self.validated_data['year'], 'days_valid': available_dates}


class ResponseOfferSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(min_value=0)
    result = serializers.BooleanField()

    class Meta:
        fields = ['result', 'order_id']

    def save(self, **kwargs):
        product = kwargs.get('product')
        user = kwargs.get('user')
        try:
            order = Order.objects.get(product__owner=user, product=product)
        except Order.DoesNotExist:
            raise ValueError('Order not found')
        if order.status != 1:
            raise ValueError('Order already accepted')
        if self.validated_data['result']:
            order.status = 2
            order.save()
            # Rimuove tutte le offerta con data di inizio compresa tra le due date
            filters = Order.objects.filter(product=product, date_start__range=[order.date_start, order.date_end])
            users = []
            for item in filters:
                item.delete()
                users.append(item.user)
            send_notification(users, 'Risultato dell\'offerta', 'La tua offerta è stata rifiutata', many=True)
        else:
            order.delete()
        send_notification(order.user, 'Risultato dell\'offerta', 'La tua offerta è stata ' + 'accettata' if self.validated_data['result'] else 'rifiutata')


class CheckoutSerializer(serializers.ModelSerializer):
    procede = serializers.BooleanField(required=False)
    delete_order = serializers.BooleanField(required=False)

    class Meta:
        fields = ['procede', 'delete_order']

    def execute_action(self, **kwargs):
        procede = self.validated_data.get('procede')
        delete = self.validated_data.get('delete')
        if procede is None and delete is None:
            raise ValueError('No parameters found. Procede or delete required')
        self.save(**kwargs) if procede else self.delete(**kwargs)

    def save(self, **kwargs):
        order = kwargs.get('order')
        user = kwargs.get('user')

    def delete(self, **kwargs):
        order = kwargs.get('order')
        user = kwargs.get('user')
