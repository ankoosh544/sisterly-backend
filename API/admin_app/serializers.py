from rest_framework import serializers
from client_app.models import Brand, Color, Material, Issue, IssueMessage
from API.static import send_notification


def get_brand(pk):
    try:
        return Brand.objects.get(pk=pk)
    except Brand.DoesNotExist:
        return None


def get_color(pk):
    try:
        return Color.objects.get(pk=pk)
    except Color.DoesNotExist:
        return None


def get_material(pk):
    try:
        return Material.objects.get(pk=pk)
    except Material.DoesNotExist:
        return None


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name']
        extra_kwargs = {
            'name': {'required': False}
        }


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'color']
        extra_kwargs = {
            'color': {'required': False}
        }

    def get_object(self):
        if not self.is_valid():
            return None
        try:
            return Color.objects.get(pk=self.validated_data['id'])
        except Brand.DoesNotExist:
            return None


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'material']
        extra_kwargs = {
            'material': {'required': False}
        }

    def get_object(self):
        if not self.is_valid():
            return None
        try:
            return Material.objects.get(pk=self.validated_data['id'])
        except Brand.DoesNotExist:
            return None


class IssueSerializer(serializers.ModelSerializer):
    valid = serializers.BooleanField()
    note = serializers.CharField(max_length=1000)

    class Meta:
        fields = ['note', 'valid']
        extra_kwargs = {
            'note': {'required': False}
        }

    def save(self, **kwargs):
        product = kwargs.get('product')
        if product is None:
            raise ValueError('No product passed')
        try:
            issue_open = Issue.objects.get(product=product)
        except Issue.DoesNotExist:
            issue_open = None
        if self.validated_data['valid']:
            if issue_open is not None:
                issue_open.open = False
                issue_open.save()
            # Indica che è stato accettato
            product.status = 4
            product.save()
            message = 'Your product has been accepted'
        else:
            if issue_open is None:
                issue_open = Issue.objects.create(product=product)
            note = self.data.get('note')
            if note is None:
                raise ValueError('Note not found')
            IssueMessage.objects.create(issue=issue_open, note=note)
            # Indica che è stato rifiutato
            product.status = 3
            product.save()
            message = 'Your product has not been accepted, for more details see app'
        send_notification(product.owner, 'Result validation', message)
