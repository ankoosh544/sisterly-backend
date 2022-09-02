from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from client_app.views.product import (
    ProductView,
    ProductInfoView,
    MyProductView,
    UserProductsView,
    SendVerificationProductView,
    FavoriteView,
    get_favorites,
    AvailabilityDatesView,
    make_offer,
    OfferView,
    get_cart,
    CheckoutView
)
from client_app.views.search import SearchProductView


urlpatterns = [
    path('', ProductView.as_view(), name='product'),
    path('search/', SearchProductView.as_view(), name='search_product'),
    # User product
    path('my/', MyProductView.as_view(), name='my_products'),
    path('<int:pk>/sentToVerification/', SendVerificationProductView.as_view(), name='product_sent_to_preview'),
    path('byUser/<int:pk>/', UserProductsView.as_view(), name='user_products'),
    # Favorites
    path('favorite/', get_favorites, name='favorite_products'),
    path('favorite/change/', FavoriteView.as_view(), name='favorite_products'),
    # Product offer
    path('<int:pk>/', ProductInfoView.as_view(), name='product_info'),
    path('<int:pk>/validDates/', AvailabilityDatesView.as_view(), name='product_info_date'),
    path('<int:pk>/offer/', OfferView.as_view(), name='offer'),
    path('<int:pk>/offer/make/', make_offer, name='offer'),
    # Checkout paths
    path('cart', get_cart, name='get_cart'),
    path('<int:pk>/checkout', CheckoutView.as_view(), name='checkout'),
]
urlpatterns = format_suffix_patterns(urlpatterns)
