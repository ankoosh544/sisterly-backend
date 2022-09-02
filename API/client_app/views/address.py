from rest_framework.response import Response
from rest_framework.views import APIView
from client_app.models import Address
from client_app.serializers.address import AddressSerializer
from API.static import send_error, send_success


class AddressView(APIView):
    # Inserisce un nuovo indirizzo
    def put(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(user=request.user)
                return send_success(serializer.data)
            except ValueError as e:
                return send_error(e.args)
        return send_error(serializer.error_messages)

    # Ottiene la lista di tutti gli indirizzi di un utente
    def get(self, request):
        user = request.user
        if user is None:
            return send_error('User not found')
        serializer = AddressSerializer(instance=Address.objects.filter(user=user), many=True)
        return send_success(serializer.data)


class AddressInfo(APIView):
    # Ottiene le informazioni di un indirizzo
    def get(self, request, pk):
        try:
            address = Address.objects.get(user=request.user, pk=pk)
            return send_success(AddressSerializer(instance=address).data)
        except Address.DoesNotExist:
            return send_error('Address not found')

    # Aggiorna un indirizzo
    def put(self, request, pk):
        try:
            address = Address.objects.get(user=request.user, pk=pk)
        except (Address.DoesNotExist, ValueError):
            return send_error('Address not found')
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.update(address, serializer.validated_data)
                return send_success(serializer.data)
            except ValueError as e:
                return send_error(e.args)
        return send_error(serializer.error_messages)
