from rest_framework import serializers
from client_app.models import Image, Video, Media


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image', 'order']
        extra_kwargs = {
            'id': {'required': False},
            'order': {'required': True},
        }

    def save(self, **kwargs):
        media = kwargs.get('media')
        if media is None:
            raise ValueError('Media not found')
        instance = Image.objects.create(media=media, order=self.validated_data['order'])
        instance.image = self.validated_data['image']
        instance.save()
        return instance


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'video', 'order']
        extra_kwargs = {
            'id': {'required': False},
            'order': {'required': True},
        }

    def save(self, **kwargs):
        media = kwargs.get('media')
        if media is None:
            raise ValueError('Media not found')
        instance = Video.objects.create(media=media, order=self.validated_data['order'])
        instance.video = self.validated_data['video']
        instance.save()
        return instance
