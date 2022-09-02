from rest_framework import serializers

from client_app.models import Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'name', 'address1', 'address2', 'country', 'province', 'zip', 'note', 'default', 'city']
        extra_kwargs = {
            'id': {'required': False},
            'address2': {'required': False},
            'note': {'required': False},
            'default': {'required': False}
        }

    def save(self, **kwargs):
        user = kwargs.get('user')
        if user is None:
            raise ValueError('User not found')
        addresses_user = Address.objects.filter(user=user)
        if len(addresses_user) > 0:
            if len(addresses_user.filter(name=self.validated_data['name'])) > 0:
                raise ValueError('Name already in use')
            default = self.data.get('default')
            if len(addresses_user.filter(default=True)) > 0 and default is not None and default:
                raise ValueError('You are already using another default address')
        Address.objects.create(**self.validated_data, user=user)

    def update(self, instance, validated_data):
        addresses_user = Address.objects.filter(user=instance.user)
        if instance.name != self.validated_data['name'] and len(addresses_user.filter(name=self.validated_data['name'])):
            raise ValueError('Name already in use')
        set_default = self.data.get('default') is not None and self.data.get('default')
        if not instance.default and set_default and len(addresses_user.filter(default=True) > 0):
            raise ValueError('You are already using another default address')
        instance.name = self.validated_data['name']
        instance.address1 = self.validated_data['address1']
        instance.country = self.validated_data['country']
        instance.province = self.validated_data['province']
        instance.zip = self.validated_data['zip']
        instance.city = self.validated_data['city']
        if self.data.get('address2') is not None:
            instance.address2 = self.validated_data['address2']
        if self.data.get('note') is not None:
            instance.note = self.validated_data['note']
        if self.data.get('default') is not None:
            instance.default = self.validated_data['default']
        instance.save()