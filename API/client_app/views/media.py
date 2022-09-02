from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from API.static import send_success, send_error
from client_app.models import Media, Image, Video
from client_app.serializers.media import ImageSerializer, VideoSerializer, MediaSerializer


class MediaView(APIView):
    def get(self, request):
        medias = Media.objects.filter(user=request.user)
        return send_success(MediaSerializer(instance=medias, many=True).data)

    def put(self, request):
        if request.user is None:
            return send_error('No user found')
        new_media = Media.objects.create(user=request.user)
        return send_success({'id': str(new_media.pk)})


class MediaInfoView(APIView):
    def get(self, request, pk):
        try:
            media = Media.objects.get(pk=pk, user=request.user)
        except Media.DoesNotExist:
            return send_error('Media not found')
        images = Image.objects.filter(media=media, active=True)
        videos = Video.objects.filter(media=media, active=True)
        return send_success({
            'images': ImageSerializer(instance=images, many=True).data,
            'videos': VideoSerializer(instance=videos, many=True).data
        })


class ImageView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, pk):
        try:
            media = Media.objects.get(pk=pk)
        except Media.DoesNotExist:
            return send_error('Media not found')
        serializer = ImageSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(media=media)
                return send_success('Image saved')
            except ValueError:
                return send_error('No media passed')
        return send_error(serializer.error_messages)


class ImageDeleteView(APIView):
    def delete(self, request, pk, pk_image):
        try:
            image = Image.objects.get(pk=pk_image)
        except (Image.DoesNotExist, Media.DoesNotExist):
            return send_error('Image not found')
        image.active = False
        image.save()
        return send_success('Image was become not active')


class VideoView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, pk):
        try:
            media = Media.objects.get(pk=pk)
        except Media.DoesNotExist:
            return send_error('Media not found')
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(media=media)
                return send_success('Video saved saved')
            except ValueError:
                return send_error('No media passed')
        return send_error(serializer.error_messages)


class VideoDeleteView(APIView):
    def delete(self, request, pk, pk_video):
        try:
            video = Video.objects.get(pk=pk_video)
        except (Video.DoesNotExist, Media.DoesNotExist):
            return send_error('Video not found')
        video.active = False
        video.save()
        return send_success('Video was become not active')
