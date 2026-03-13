from django.shortcuts import render, redirect, HttpResponse
from .models import *

# Create your views here.
def home(request):
    return render(request, "home.html")


def products(request):
    listings = Listing.objects.all()
    return render(request, "products.html", {"listings": listings})


def product_detail(request, listing_id):
    try:
        product = Listing.objects.get(id=listing_id)
        return render(request, "product_detail.html", {"product": product})
        
    except Listing.DoesNotExist:
        return redirect("products")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = User(username=username, password_hash=password)
        user.save()

        return redirect("login")
    
    return render(request, "register.html")


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
            return render(request, "register.html")
    
    return render(request, "login.html")
        

def profile(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user = User.objects.get(id=user_id)

    return render(request, "profile.html", {"user": user})


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

    return render(request, "create_listing.html")




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
            return render(request, "home.html")

    return render(request, "edit_listing.html")




def my_listings(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    listings = Listing.objects.filter(user_id=user_id)

    return render(request, "my_listings.html", {"listings": listings})
    


def messages(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user_messages = Message.objects.filter(user_id=user_id)

    return render(request, "messages.html", {"messages": user_messages})


def transactions(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    user_transactions = Transaction.objects.filter(user_id=user_id)

    return render(request, "transactions.html", {"transactions": user_transactions})



def notifications(request):
    user_id = request.session.get("user_id")
    
    if not user_id:
        return redirect("login")

    user_notifications = Notification.objects.filter(user_id=user_id)

    return render(request, "notifications.html", {"notifications": user_notifications})