from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from admin_app.views import (
    BrandView, BrandInfo,
    ColorView, ColorInfo,
    MaterialView, MaterialInfo,
    ProductView
)

urlpatterns = [
    # Gestione dei brands
    path('brand', BrandView.as_view(), name="brand"),
    path('brand/<int:pk>', BrandInfo.as_view(), name="brand_info"),
    # Gestione dei colori
    path('color', ColorView.as_view(), name="brand"),
    path('color/<int:pk>', ColorInfo.as_view(), name="brand_info"),
    # Gestione dei materiali
    path('material', MaterialView.as_view(), name="brand"),
    path('material/<int:pk>', MaterialInfo.as_view(), name="brand_info"),
    # Gestione dei products
    path('product/', ProductView.as_view(), name='products')
]

urlpatterns = format_suffix_patterns(urlpatterns)
