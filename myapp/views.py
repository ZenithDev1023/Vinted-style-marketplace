from django.shortcuts import render, redirect, HttpResponse
from .models import *

# Create your views here.
def home(request):
    user_id = request.session.get("user_id")
    user = None
    featured_listings = []
    
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            pass
    
    # Get featured listings (recent 6)
    featured_listings = Listing.objects.all()[:6]
    
    context = {
        'user_id': user_id,
        'user': user,
        'featured_listings': featured_listings,
    }
    
    return render(request, "home/home.html", context)
    


def products(request):
    listings = Listing.objects.all()
    listings_with_photos = []
    #It now loops through each listing and retrieves the primary photo associated with it, creating a list of dictionaries that contain both the listing and its primary photo. 
    # This allows the template to easily access and display the primary photo for each listing.
    for listing in listings:
        primary_photo = listing.photo_set.filter(isPrimary=True).first()
        listings_with_photos.append({
            "listing": listing,
            "primary_photo": primary_photo,
        })
    return render(request, "product-page/products.html", {"listings_with_photos": listings_with_photos})


def product_detail(request, listing_id):
    try:
        product = Listing.objects.get(id=listing_id)
        primary_photo = product.photo_set.filter(isPrimary=True).first()
        return render(request, "product-page/product_detail.html", {
            "product": product,
            "primary_photo": primary_photo,
        })
        
    except Listing.DoesNotExist:
        return redirect("products")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = User(username=username, password_hash=password)
        user.save()

        return redirect("login")
    
    return render(request, "login-register/register.html")


def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)

            if user.login(password):
                request.session["user_id"] = user.id 
                return redirect("home")

        except User.DoesNotExist:
            return render(request, "login-register/register.html")
    
    return render(request, "login-register/login.html")
        

def profile(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = User.objects.get(id=user_id)

    return render(request, "profile/profile.html", {"user": user})


def create_listing(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        price = request.POST.get("price")

        listing = Listing(title=title, description=description, price=price, user_id=user_id)
        listing.save()

        return redirect("products")

    return render(request, "listings/create_listing.html")




def edit_listing(request):
    if request.method == "POST":
        listing_id = request.POST.get("listing_id")
        title = request.POST.get("title")
        description = request.POST.get("description")
        price = request.POST.get("price")

        try:
            listing = Listing.objects.get(id=listing_id, user_id=request.session.get("user_id"))

            listing.title = title 
            listing.description = description 
            listing.price = price 
            listing.save()

            return redirect("products")

        except Listing.DoesNotExist:
            return render(request, "home/home.html")

    return render(request, "listings/edit_listing.html")




def my_listings(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    listings = Listing.objects.filter(user_id=user_id)

    return render(request, "listings/my_listings.html", {"listings": listings})
    


def messages(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user_messages = Message.objects.filter(user_id=user_id)

    return render(request, "profile/messages.html", {"messages": user_messages})


def transactions(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user_transactions = Transaction.objects.filter(user_id=user_id)

    return render(request, "profile/transactions.html", {"transactions": user_transactions})



def notifications(request):
    user_id = request.session.get("user_id")
    
    if not user_id:
        return redirect("login")

    user_notifications = Notification.objects.filter(user_id=user_id)

    return render(request, "profile/notifications.html", {"notifications": user_notifications})