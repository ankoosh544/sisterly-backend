from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from client_app.views.address import AddressView, AddressInfo
from client_app.views.client import (
    registration,
    account_properties,
    active_account,
    send_verify_email,
    logout,
    password_reset,
    email_reset,
    email_change,
    PlayerIdView
)
from client_app.views.search import SearchUserView
from django.contrib.auth import views as auth_views
from client_app.views.media import MediaView, ImageView, VideoView, ImageDeleteView, VideoDeleteView, MediaInfoView

urlpatterns = [
    path('register', registration, name="register"),
    # Conferma email
    path('confirm_email', send_verify_email, name='send_email'),
    path('confirm_email/<uid>/<token>/', active_account, name='activate'),
    # Modifica della email
    path('email_reset', email_reset, name='send_email'),
    path('email_reset/<uid>/<token>/', email_change, name='activate'),
    # Reset della password
    path("reset_password", password_reset, name="password_reset"),
    path('reset_password/done/', auth_views.PasswordResetDoneView.as_view(template_name='client/password_reset_done.html'), name='password_reset_done'),
    path('reset_password/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="client/password_reset_confirm.html"), name='password_reset_confirm'),
    # Token per accesso
    path('token', TokenObtainPairView.as_view(), name="login"),
    path('token/refresh', TokenRefreshView.as_view(), name="login"),
    # Azioni dell'utente
    path('properties', account_properties, name='properties'),
    path('playerId', PlayerIdView.as_view(), name='player_id'),
    path('logout', logout, name='logout'),
    # Indirizzi
    path('address', AddressView.as_view(), name='address'),
    path('address/<int:pk>', AddressInfo.as_view(), name='address_info'),
    # Media
    path('media', MediaView.as_view(), name='media'),
    path('media/<int:pk>', MediaInfoView.as_view(), name='media_info'),
    path('media/<int:pk>/images', ImageView.as_view(), name='media_image'),
    path('media/<int:pk>/images/<int:pk_image>', ImageDeleteView.as_view(), name='delete_image'),
    path('media/<int:pk>/videos', VideoView.as_view(), name='media_video'),
    path('media/<int:pk>/videos/<int:pk_video>', VideoDeleteView.as_view(), name='delete_video'),
    # Ricerca
    path('search', SearchUserView.as_view(), name='user_search')
]

urlpatterns = format_suffix_patterns(urlpatterns)
