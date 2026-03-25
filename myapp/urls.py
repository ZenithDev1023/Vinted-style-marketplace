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
    path("messages/start/<int:listing_id>/", views.start_conversation, name="start_conversation"),
    path("settings/", views.settings, name="settings"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("createListing/", views.create_listing, name="create_listing"),
    path("editListing/<int:listing_id>/", views.edit_listing, name="edit_listing"),
    path("deleteListing/<int:listing_id>/", views.delete_listing, name="delete_listing"),
    path("myListings/", views.my_listings, name="my_listings"),
    path('transactions/', views.transactions, name="transactions"),
    path("notifications/", views.notifications, name="notifications"),
    path("chatbot/", views.chatbot_response, name="chatbot"),
    path("chatbot/page/", views.chatbot_page, name="chatbot_page"),

     # About TradeX
    path("about-us/", views.about_us, name="about_us"),
    path("careers/", views.careers, name="careers"),
    path("blog/", views.blog, name="blog"),
    path("press/", views.press, name="press"),
    
    # Help & Contact
    path("help-center/", views.help_center, name="help_center"),
    path("safety-tips/", views.safety_tips, name="safety_tips"),
    path("scam-alerts/", views.scam_alerts, name="scam_alerts"),
    
    # Policies
    path("privacy-notice/", views.privacy_notice, name="privacy_notice"),
     path("terms-of-service/", views.terms_of_service, name="terms_of_service"),
    path("cookie-policy/", views.cookie_policy, name="cookie_policy"),
    path("community-guidelines/", views.community_guidelines, name="community_guidelines"),
    
    # For Tradespeople
    path("advertising/", views.advertising, name="advertising"),
]