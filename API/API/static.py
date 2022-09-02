from rest_framework import status
from rest_framework.response import Response
from client_app.models import Device, Product
import requests
import json


def send_error(errors, status_error=status.HTTP_400_BAD_REQUEST):
    return Response(status=status_error, data={'success': False, 'errors': errors})


def send_success(data=None):
    res = {'success': True}
    if data is not None:
        res['data'] = data
    return Response(res)


def send_notification(user, title, message, many=False):
    users_player_ids = Device.objects.filter(user=user) if not many else Device.objects.filter(user__in=user)
    player_ids = [str(item.player_id) for item in users_player_ids]
    if len(users_player_ids) > 0:
        header = {"Content-Type": "application/json; charset=utf-8"}
        payload = {
            "app_id": "5eb5a37e-b458-11e3-ac11-000c2940e62c",  # Mettere id corretto
            "include_player_ids": player_ids,
            "headings": {"en": title},
            "contents": {"en": message}
        }
        requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
