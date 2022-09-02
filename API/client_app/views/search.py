from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from client_app.serializers.search import SearchProductSerializer, SearchUserSerializer
from client_app.serializers.product import ProductSerializer
from client_app.serializers.client import UserSerializer
from API.static import send_success, send_error


class SearchProductView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SearchProductSerializer(data=request.data)
        if serializer.is_valid():
            products = serializer.get_filters()
            return send_success([ProductSerializer(instance=item).serialize_data() for item in products])
        return send_error(serializer.errors)


class SearchUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SearchUserSerializer(data=request.data)
        if serializer.is_valid():
            users = serializer.get_filters()
            return send_success(UserSerializer(instance=users, many=True).data)
        return send_error(serializer.errors)
