from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.authtoken.models import Token
from django_countries.fields import CountryField

from API import settings
from client_app.managers import CustomUserManager


def upload_img(instance, filename):
    return "images/%s/%s" % (instance.pk, filename)


def upload_video(instance, filename):
    return "video/%s/%s" % (instance.pk, filename)


class User(AbstractUser):
    email = models.EmailField('email address', unique=True)
    username = None
    email_confirmed = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    deposit = models.FloatField('Deposito', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    # set the manager authentication
    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    player_id = models.CharField(max_length=50, unique=True)
    socket_id = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField("name address", max_length=100)
    address1 = models.CharField("Indirizzo 1", max_length=100)
    address2 = models.CharField("Indirizzo 2", max_length=100, null=True, blank=True)

    country = CountryField("Paese", multiple=False)
    province = models.CharField("Provincia", max_length=100)
    city = models.CharField("Città", max_length=100)
    zip = models.CharField("CAP", max_length=100)
    note = models.TextField("Note Aggiuntive", max_length=500, blank=True, null=True)

    # default address for users
    default = models.BooleanField("Imposta Come Predefinito", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Color(models.Model):
    color = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.color


class Material(models.Model):
    material = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.material


class Media(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.pk)


class Image(models.Model):
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_img)
    active = models.BooleanField(default=True)
    order = models.IntegerField('Ordine di apparizione', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.image.name


class Video(models.Model):
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    video = models.FileField(upload_to=upload_video, validators=[FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])])
    order = models.IntegerField('Ordine di apparizione', default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.video.name


class Product(models.Model):
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    media = models.ForeignKey(Media, on_delete=models.DO_NOTHING, null=True)
    model = models.CharField('Modello della borsa', max_length=100)
    brand = models.ForeignKey(Brand, on_delete=models.DO_NOTHING)
    color = models.ForeignKey(Color, on_delete=models.DO_NOTHING)
    material = models.ForeignKey(Material, on_delete=models.DO_NOTHING)
    conditions = models.PositiveSmallIntegerField('Condizioni della borsa', choices=settings.BAG_CONDITIONS)
    year = models.PositiveSmallIntegerField('Anni della borsa', choices=settings.BAG_YEARS)
    size = models.PositiveSmallIntegerField('Dimensioni della borsa', choices=settings.BAG_SIZE)
    description = models.CharField('Descrizione della borsa', max_length=2000, null=True)
    price_retail = models.FloatField('Prezzo', default=0)
    price_offer = models.FloatField('Prezzo offerta', default=0)
    status = models.PositiveSmallIntegerField(choices=settings.PRODUCT_STATES, default=1)
    delivery_type = models.PositiveSmallIntegerField(choices=settings.DELIVERY_TYPE)

    # Info per il kit
    delivery_kit = models.ForeignKey(Address, on_delete=models.DO_NOTHING)
    kit_payed = models.BooleanField('Indica se è stato pagato il kit', default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.pk)


class Issue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.pk)


class IssueMessage(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    note = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.note


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    products = models.ManyToManyField(Product)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)


class Order(models.Model):
    product = models.ManyToManyField(Product)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    state = models.PositiveSmallIntegerField(choices=settings.ORDER_STATUS, default=1)
    price = models.IntegerField('Prezzo proposto', default=0)
    date_start = models.DateTimeField('Data di inizio del prestito')
    date_end = models.DateTimeField('Data di fine del prestito')
    date_begin_order = models.DateTimeField('Data di conferma dell\'inizio dell\'ordine', null=True)
    date_end_order = models.DateTimeField('Data di conferma della fine dell\'ordine', null=True)
    delivery_mode = models.PositiveSmallIntegerField(choices=settings.DELIVERY_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.pk)


class Complaint(models.Model):
    owner = models.ManyToManyField(User)
    product = models.ManyToManyField(Product)
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    description = models.CharField('Descrizione', max_length=3000, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.pk)
