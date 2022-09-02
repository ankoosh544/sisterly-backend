from django.contrib import admin
from .models import User, Address, Media, Image, Video, Product

admin.site.register(User)
admin.site.register(Address)
admin.site.register(Media)
admin.site.register(Image)
admin.site.register(Video)
admin.site.register(Product)
