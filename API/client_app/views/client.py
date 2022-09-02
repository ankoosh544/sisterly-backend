import datetime
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from client_app.forms import EmailResetForm
from client_app.serializers.client import RegistrationSerializer, PlayerIdSerializer
from client_app.models import User, Device
from client_app.tokens import account_activation_token, email_change_token
from API.static import send_error, send_success


@api_view(['POST'])
def logout(request):
    refresh_token = request.data.get('refresh')
    player_id = request.data.get('player_id')
    if refresh_token is not None and player_id is not None:
        try:
            refresh = RefreshToken(refresh_token)
            refresh.access_token.set_exp(lifetime=datetime.timedelta(seconds=0))
            refresh.blacklist()
            try:
                device = Device.objects.get(user=request.user, player_id=player_id)
                device.delete()
            except Device.DoesNotExist:
                pass
            return send_error('Successfully logout', status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return send_error('Token not valid')
    else:
        return send_error('Token not found' if player_id is None else 'Player id not found')


@api_view(['POST'])
@permission_classes([AllowAny])
def registration(request):
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = account_activation_token.make_token(user)
        send_email(request, user, token, 'client/account_activation_email.html')
        refresh = RefreshToken.for_user(user)
        return send_success({'email': user.email, 'refresh': str(refresh), 'access': str(refresh.access_token)})
    else:
        return send_error(serializer.errors)


@api_view(['POST'])
def send_verify_email(request):
    try:
        user = User.objects.get(pk=request.user.pk)
    except User.DoesNotExist:
        return send_error('No user found', status.HTTP_401_UNAUTHORIZED)
    if not user.email_confirmed:
        token = account_activation_token.make_token(user)
        send_email(request, user, token, 'client/account_activation_email.html')
        return send_success('Successfully send email')
    else:
        return send_error('Email already verified')


@api_view(['POST'])
def email_reset(request):
    try:
        user = User.objects.get(pk=request.user.pk)
    except User.DoesNotExist:
        return send_error('No user found', status.HTTP_401_UNAUTHORIZED)
    send_email(request, user, email_change_token.make_token(user), 'client/email_reset_request.html')
    return send_success('Successfully send email')


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def password_reset(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            try:
                user = User.objects.get(email=password_reset_form.cleaned_data['email'])
                if user.email_confirmed:
                    send_email(request, user, default_token_generator.make_token(user),
                               'client/password_reset_email.html', False)
                    return redirect("reset_password/done/")
                else:
                    return render(request, template_name='error.html',
                                  context={'error': 'Email not confirmed', 'back': '/client/reset_password'})
            except User.DoesNotExist:
                return render(request, template_name='error.html',
                              context={'error': 'Email not exist', 'back': '/client/reset_password'})
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="client/password_reset.html",
                  context={"password_reset_form": password_reset_form})


def send_email(request, user, token, template, uid=True):
    current_site = get_current_site(request)
    subject = 'Activate Your MySite Account'
    message = render_to_string(template, {
        'user': user,
        'domain': current_site.domain,
        'uid' if uid else 'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token,
    })
    email = EmailMessage(
        subject, message, to=[user.email]
    )
    email.send()


@api_view(['GET'])
@permission_classes([AllowAny])
def active_account(request, uid, token):
    try:
        uid_decode = force_text(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid_decode)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        account = None
    if user is not None and account_activation_token.check_token(user, token):
        user.email_confirmed = True
        user.save()
        return render(request, template_name='success.html',
                      context={'success_message': 'Thank you for your email confirmation.',
                               'back': None})
    return render(request, template_name='error.html',
                  context={'error': 'The confirmation link was invalid, possibly because it has already been used',
                           'back': None})


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def email_change(request, uid, token):
    # Controlla che i dati siano corretti
    try:
        uid_decode = force_text(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid_decode)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is None or not email_change_token.check_token(user, token):
        return render(request, template_name='error.html',
                      context={'error': 'The confirmation link was invalid', 'back': None})
    # In base al metodo ritorna i dati
    if request.method == 'POST':
        email_form = EmailResetForm(request.data)
        if email_form.is_valid():
            back_url = '/client/email_reset/' + str(uid) + '/' + str(token)
            if user.email == email_form.cleaned_data['email']:
                return render(request, template_name='error.html',
                              context={
                                  'error': 'L\'email inserita corrisponde a quella attualmente in uso',
                                  'back': back_url})
            try:
                User.objects.get(email=email_form.cleaned_data['email'])
                exist = True
            except User.DoesNotExist:
                exist = False
            if not exist:
                # Resetta la email e la rende non confermata
                user.email = email_form.cleaned_data['email']
                user.email_confirmed = False
                user.save()
                # Invia una nuova email di conferma
                token = account_activation_token.make_token(user)
                send_email(request, user, token, 'client/account_activation_email.html')
                return render(request, template_name='success.html',
                              context={'success_message': 'Thank you for your email confirmation.',
                                       'back': None})
            return render(request, template_name='error.html',
                          context={'error': 'L\'email inserita esiste già', 'back': back_url})
    return render(request, template_name='client/email_reset.html', context={'form': EmailResetForm()})


@api_view(['GET'])
def account_properties(request):
    try:
        user = User.objects.get(pk=request.user.pk)
    except User.DoesNotExist:
        return send_error('User not valid', status.HTTP_401_UNAUTHORIZED)
    return send_success({'email_confirmed': user.email_confirmed, 'email': user.email, 'username': user.username})


class PlayerIdView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PlayerIdSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return send_success('Player id updated')
        return send_error(serializer.errors)
