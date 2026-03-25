from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("products/", views.products, name="products"),
    path("products/<int:listing_id>/", views.product_detail, name='product_details'),
    path("products/<int:listing_id>/reviews/add/", views.add_review, name="add_review"),
    path("profile/", views.profile, name="profile"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("messages/", views.messages, name="messages"),
    path("settings/", views.settings, name="settings"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("createListing/", views.create_listing, name="create_listing"),
    path("editListing/", views.edit_listing, name="edit_listing"),
    path("deleteListing/<int:listing_id>/", views.delete_listing, name="delete_listing"),
    path("myListings/", views.my_listings, name="my_listings"),
    path('transactions/', views.transactions, name="transactions"),
    path("notifications/", views.notifications, name="notifications"),
]