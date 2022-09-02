from rest_framework import serializers
from django.http import QueryDict
from client_app.models import User, Product
from admin_app.serializers import get_brand, get_color, get_material


class SearchProductSerializer(serializers.ModelSerializer):
    id_brand = serializers.IntegerField(min_value=1, required=False)
    id_color = serializers.IntegerField(min_value=1, required=False)
    id_material = serializers.IntegerField(min_value=1, required=False)
    start = serializers.IntegerField(min_value=0)
    limit = serializers.IntegerField(min_value=0)

    class Meta:
        model = Product
        fields = ['id_brand', 'id_color', 'id_material', 'model', 'start', 'limit']
        extra_kwargs = {
            'model': {'required': False},
        }

    def get_filters(self):
        filters = None
        no_data = False
        start = self.validated_data['start']
        limit = self.validated_data['limit']
        # Filtro per brand
        if self.data.get('id_brand') is not None:
            brand = get_brand(self.validated_data['id_brand'])
            if brand is not None:
                filters = Product.objects.filter(brand=brand)
            else:
                no_data = True
        # Filtro per color
        if self.data.get('id_color') is not None and not no_data:
            color = get_color(self.validated_data['id_color'])
            if color is not None:
                filters = Product.objects.filter(color=color) if filters is None else filters.filter(color=color)
            else:
                no_data = True
        # Filtro per material
        if self.data.get('id_material') is not None and not no_data:
            material = get_material(self.validated_data['id_material'])
            if material is not None:
                filters = Product.objects.filter(material=material) if filters is None else filters.filter(material=material)
            else:
                no_data = True
        # Filtro per model
        if self.data.get('model') is not None and not no_data:
            filters = Product.objects.filter(model__contains=self.validated_data['model']) if filters is None else filters.filter(model__contains=self.validated_data['model'])
        return [] if no_data else filters[start:(start + limit)] if filters is not None else Product.objects.all()[start:(start + limit)]


class SearchUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=50, required=False)
    last_name = serializers.CharField(max_length=50, required=False)
    start = serializers.IntegerField(min_value=0)
    limit = serializers.IntegerField(min_value=0)

    class Meta:
        fields = ['first_name', 'last_name', 'start', 'limit']

    def get_filters(self):
        is_first_name = self.data.get('first_name') is not None
        is_last_name = self.data.get('last_name') is not None
        filters = None
        start = self.validated_data['start']
        limit = self.validated_data['limit']
        if is_first_name:
            if is_last_name:
                filters = User.objects.filter(last_name__contains=self.validated_data['last_name'], first_name__contains=self.validated_data['first_name'])
            else:
                filters = User.objects.filter(first_name__contains=self.validated_data['first_name'])
        elif is_last_name:
            filters = User.objects.filter(last_name__contains=self.validated_data['last_name'])
        return [] if filters is None else filters[start:(start + limit)]








