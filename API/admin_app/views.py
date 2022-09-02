from rest_framework.views import APIView
from API.static import send_success, send_error
from admin_app.permissions import AdminPermission
from admin_app.serializers import BrandSerializer, ColorSerializer, MaterialSerializer, IssueSerializer
from client_app.models import Brand, Color, Material, Product
from client_app.serializers.product import ProductSerializer
from client_app.views.product import get_product


# Classe per la aggiunta di un brand
class BrandView(APIView):
    permission_classes = [AdminPermission]

    def put(self, request):
        serializer = BrandSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return send_success(serializer.data)
        return send_error(serializer.error_messages)


# Classe per la modifica di un brand
class BrandInfo(APIView):
    permission_classes = [AdminPermission]

    def put(self, request, pk):
        try:
            brand = Brand.objects.get(pk=pk)
        except Brand.DoesNotExist:
            return send_error('Brand not found')
        serializer = BrandSerializer(data=request.data)
        if serializer.is_valid():
            serializer.update(brand, serializer.validated_data)
            return send_success(serializer.data)
        return send_error(serializer.error_messages)


# Classe per la aggiunta di un colore
class ColorView(APIView):
    permission_classes = [AdminPermission]

    def put(self, request):
        serializer = ColorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return send_success(serializer.data)
        return send_error(serializer.error_messages)


# Classe per la modifica di un colore
class ColorInfo(APIView):
    permission_classes = [AdminPermission]

    def put(self, request, pk):
        try:
            color = Color.objects.get(pk=pk)
        except Color.DoesNotExist:
            return send_error('Color not found')
        serializer = ColorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.update(color, serializer.validated_data)
            return send_success(serializer.data)
        return send_error(serializer.error_messages)


# Classe per la aggiunta di un materiale
class MaterialView(APIView):
    permission_classes = [AdminPermission]

    def put(self, request):
        serializer = MaterialSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return send_success(serializer.data)
        return send_error(serializer.error_messages)


# Classe per la modifica di un materiale
class MaterialInfo(APIView):
    permission_classes = [AdminPermission]

    def put(self, request, pk):
        try:
            material = Material.objects.get(pk=pk)
        except Material.DoesNotExist:
            return send_error('Material not found')
        serializer = MaterialSerializer(data=request.data)
        if serializer.is_valid():
            serializer.update(material, serializer.validated_data)
            return send_success(serializer.data)
        return send_error(serializer.error_messages)


class ProductView(APIView):
    permission_classes = [AdminPermission]

    def get(self, request):
        products = Product.objects.filter(status=2)
        return send_success([ProductSerializer(instance=item).serialize_data(admin=True) for item in products])


class ProductReview(APIView):
    permission_classes = [AdminPermission]

    def post(self, request, pk):
        product = get_product(pk)
        if product.status != 2:
            return send_error('Product already verified')
        serializer = IssueSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(product=product)
                return send_success()
            except ValueError as e:
                return send_error(e.args)
        return send_error(serializer.errors)
