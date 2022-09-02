from rest_framework.decorators import api_view
from rest_framework.views import APIView
from API.static import send_success, send_error
from client_app.permissions import SPIDPermission
from client_app.models import Product, Media, User, Favorite, Order
from client_app.permissions import ProductPermission
from client_app.serializers.media import VideoSerializer
from client_app.serializers.product import (
    AddProductSerializer,
    ProductSerializer,
    OrderSerializer,
    FavoriteProductSerializer,
    SubmitOfferSerializer,
    AvailabilityDatesSerializer,
    ResponseOfferSerializer
)


def save_product(data, instance=None, status=-1, user=None):
    serializer = AddProductSerializer(data=data)
    if serializer.is_valid():
        try:
            if instance is None:
                if user is None:
                    raise ValueError('User not found')
                product = serializer.save(user=user)
            else:
                product = serializer.update(instance, serializer.validated_data)
            if status != -1:
                instance.status = status
                instance.save()
            return send_success(get_product(product.pk, get_data=True))
        except ValueError as e:
            return send_error(e.args)
    return send_error(serializer.errors)


def get_product(pk, get_data=False):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return None
    return product if not get_data else ProductSerializer(instance=product).serialize_data()


class ProductView(APIView):
    permission_classes = [ProductPermission]

    def get(self, request):
        limit = request.data.get('limit')
        start = request.data.get('start')
        if limit is None:
            limit = 50
        if start is None:
            start = 0
        list_products = Product.objects.all().order_by('-id').filter(status=4)
        if len(list_products) >= start >= 0:
            return send_success(
                [ProductSerializer(instance=item).serialize_data() for item in list_products[start:limit]])
        return send_error('Start greater than maximum length')

    def put(self, request):
        return save_product(request.data, user=request.user)


class ProductInfoView(APIView):
    def get(self, request, pk):
        data = get_product(pk, get_data=True)
        if data is None:
            return send_error('Product not found')
        return send_success(data)

    def post(self, request, pk):
        # Manca il controllo per l'accesso con SPID
        product = get_product(pk)
        if product is None:
            return send_error('Product not found')
        if product.owner != request.user:
            return send_error('You\'re not the owner of this product')
        if product.status == 1:
            # In PREPARATION
            return save_product(request.data, product)
        elif product.status == 2:
            # In REVIEW
            return send_error('You cannot edit the product because it\'s under review')
        elif product.status == 3:
            # REJECT
            return save_product(request.data, product, 1)
        return send_error('You can\'t modify your product')


class MyProductView(APIView):
    def get(self, request):
        products = Product.objects.filter(owner=request.user, status__lt=5)
        return send_success([ProductSerializer(instance=item).serialize_data() for item in products])


class UserProductsView(APIView):
    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return send_error('User not found')
        products = Product.objects.filter(user=user, status=4)
        return send_success([ProductSerializer(instance=item).serialize_data() for item in products])


class SendVerificationProductView(APIView):
    permission_classes = [SPIDPermission]

    def post(self, request, pk):
        product = get_product(pk)
        if product is None:
            return send_error('Product not found')
        if product.owner != request.user:
            return send_error('You are not the owner of product')
        if product.status == 2:
            return send_error('Product already under review')
        if product.status != 1:
            return send_error('Product are not in preparation status')
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            media = Media.objects.get(pk=product.media)
            serializer.save(media=media)
            product.status = 2
            product.save()
            return send_success('Product under review')
        return send_error(serializer.errors)


@api_view(['GET'])
def get_favorites(request, format=None):
    try:
        products = Favorite.objects.get(user=request.user).products
    except Favorite.DoesNotExist:
        return send_success([])
    return send_success([ProductSerializer(item).serialize_data() for item in products])


class FavoriteView(APIView):
    permission_classes = [SPIDPermission]

    def post(self, request):
        return self.action_favorite(request.data, request.user)

    def delete(self, request):
        return self.action_favorite(request.data, request.user, delete=True)

    def action_favorite(self, data, user, delete=False):
        serializer = FavoriteProductSerializer(data=data)
        if serializer.is_valid():
            try:
                if not delete:
                    serializer.save(user=user)
                else:
                    serializer.remove(user=user)
                return send_success('Product ' + 'add' if not delete else 'remove')
            except ValueError as e:
                return send_error(e.args)
        return send_error(serializer.errors)


class AvailabilityDatesView(APIView):
    def get(self, request, pk):
        product = get_product(pk)
        if product is None:
            return send_error('Product not found')
        serializer = AvailabilityDatesSerializer(data=request.data)
        if serializer.is_valid():
            return send_success(serializer.serialize(product))
        return send_error(serializer.errors)


@api_view(['PUT'])
def make_offer(request, pk, format=None):
    product = get_product(pk)
    if product is None:
        return send_error('Product not found')
    serializer = SubmitOfferSerializer(data=request.data)
    if serializer.is_valid():
        try:
            serializer.save()
            return send_success('Order submitted')
        except ValueError as e:
            return send_error(e.args)
    return send_error(serializer.errors)


class OfferView(APIView):
    permission_classes = [SPIDPermission]

    def get(self, request, pk):
        product = get_product(pk)
        if product is None:
            return send_error('Product not found')
        orders = Order.objects.filter(product=product, product__owner=request.user, status=1)
        data = []
        for item in orders:
            data.append({
                'product': ProductSerializer(instance=product).serialize_data(),
                'date_start': item.date_start,
                'date_end': item.date_end,
                'price': item.price,
            })
        return send_success(data)

    def post(self, request, pk):
        product = get_product(pk)
        if product is None:
            return send_error('Product not found')
        serializer = ResponseOfferSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(product=product, user=request.user)
                return send_success('Order accepted')
            except ValueError as e:
                return send_error(e.args)
        return send_error(serializer.errors)


@api_view(['GET'])
def get_cart(request, format=None):
    orders = Order.objects.get(user=request.user, state=2)
    return send_success([OrderSerializer(item).serialize_data() for item in orders])


class CheckoutView(APIView):
    permission_classes = [SPIDPermission]
