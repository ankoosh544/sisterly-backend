from rest_framework import serializers
from client_app.models import User, Device


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'write_only': True}
        }

    def save(self, **kwargs):
        return User.objects.create_user(**self.validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']


class PlayerIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['player_id']

    def save(self, **kwargs):
        user = kwargs.get('user')
        if user is None:
            raise ValueError('User not passed')
        try:
            device = Device.objects.get(player_id=self.validated_data['player_id'])
        except Device.DoesNotExist:
            device = None
        if device is None:
            return Device.objects.create(user=user, player_id=self.validated_data['player_id'])
        else:
            device.user = user
            device.save()
            return device
