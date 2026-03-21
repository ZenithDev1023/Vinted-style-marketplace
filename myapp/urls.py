from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("products/", views.products, name="products"),
    path("products/<int:listing_id>/", views.product_detail, name='product_details'),
    path("contact/", views.contact, name="contact"),
    path("messages/", views.messages, name="messages"),
    path("settings/", views.settings, name="settings"),

    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("profile/", views.profile, name="profile"),
    path("createListing/", views.create_listing, name="create_listing"),
    path("editListing/", views.edit_listing, name="edit_listing"),
    path("myListings/", views.my_listings, name="my_listings"),
    path('transactions/', views.transactions, name="transactions"),
    path("notifications/", views.notifications, name="notifications"),
]