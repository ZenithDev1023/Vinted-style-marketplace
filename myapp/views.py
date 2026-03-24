from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from .forms import CreateListingForm, RegisterForm
from .models import (
    Category,
    CreditAccount,
    Listing,
    ListingStatus,
    Location,
    Photo,
    Transaction,
    User,
)


# Create your views here.
def home(request):
    user_id = request.session.get("user_id")
    user = None
    
    if user_id:
         user = User.objects.filter(id=user_id).first()

    featured_listings = Listing.objects.all()[:6]
    
    context = {
        "user_id": user_id,
        "user": user,
        "featured_listings": featured_listings,
    }
    
    return render(request, "home/home.html", context)
    
@login_required
def profile(request):
    user = request.user

    return render(request, "profile/profile.html", {"user": user})


def about(request):
    return render(request, "about/about.html")

def products(request):
    listings = Listing.objects.all()
    listings_with_photos = []
    #It now loops through each listing and retrieves the primary photo associated with it, creating a list of dictionaries that contain both the listing and its primary photo. 
    # This allows the template to easily access and display the primary photo for each listing.
    for listing in listings:
        primary_photo = listing.photo_set.filter(isPrimary=True).first()
    listings_with_photos.append({"listing": listing, "primary_photo": primary_photo})
    return render(request, "product-page/products.html", {"listings_with_photos": listings_with_photos})


def product_detail(request, listing_id):
    product = Listing.objects.filter(id=listing_id).first()
    if not product:
        return redirect("products")

    primary_photo = product.photo_set.filter(isPrimary=True).first()
    return render(
        request,
        "product-page/product_detail.html",
        {
            "product": product,
            "primary_photo": primary_photo,
        
       },
    )


def contact(request):
    return render(request, "sidebar/contact.html")


@login_required
def messages(request):
    user = request.user

    return render(request, "sidebar/messages.html")

@login_required 
def settings(request):
    user = request.user
    
    return render(request, "sidebar/settings.html")


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        
        if form.is_valid():
            auth_user = form.save()

            # create app profile record used by listings flow
            profile_user, _ = User.objects.get_or_create(
                username=auth_user.username,
                defaults={
                    "email": auth_user.email,
                    # kept for legacy custom model compatibility
                    "password_hash": auth_user.password,
                },
            )
            if profile_user.email != auth_user.email:
                profile_user.email = auth_user.email
                profile_user.save(update_fields=["email"])

            # Keep legacy session-based flow working
            request.session["user_id"] = profile_user.id

            return redirect("login")
    else:
        form = RegisterForm()
    
    return render(request, "login-register/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            auth_user = form.get_user()
            login(request, auth_user)

            # ensure app profile exists and put profile id in session
            profile_user, _ = User.objects.get_or_create(
                username=auth_user.username,
                defaults={
                    "email": auth_user.email,
                    "password_hash": auth_user.password,
                },
            )
            request.session["user_id"] = profile_user.id

            return redirect("home")
    else:
        form = AuthenticationForm()
    
    return render(request, "login-register/login.html", {"form": form})
        

def create_listing(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    profile_user = User.objects.filter(id=user_id).first()
    if not profile_user:
        return redirect("login")
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = profile_user
            listing.status = ListingStatus.ACTIVE

            default_category, _ = Category.objects.get_or_create(name="General")
            default_location, _ = Location.objects.get_or_create(
                user=profile_user,
                defaults={
                    "postcode": "N/A",
                    "city": "Unknown",
                    "latitude": 0,
                    "longitude": 0,
                },
            )
            credit_account, _ = CreditAccount.objects.get_or_create(
                user=profile_user,
                defaults={"creditBalance": profile_user.credits_balance},
            )

            listing.category = default_category
            listing.location = default_location
            listing.creditAccount = credit_account
            listing.save()
            image_url = request.POST.get("image_url")
            if image_url:
                Photo.objects.create(
                    image_url=image_url,
                    listing=listing,
                    category=default_category,
                    isPrimary=True,
                )

            return redirect("products")
    else:
        form = CreateListingForm()

    return render(request, "listings/create_listing.html", {"form": form})



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
    



def transactions(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    # Legacy model relation mismatch kept safe for now.
    user_transactions = Transaction.objects.none()

    return render(request, "profile/transactions.html", {"transactions": user_transactions})



def notifications(request):
    # Notification model is not implemented in this codebase.
    return render(request, "profile/notifications.html", {"notifications": []})