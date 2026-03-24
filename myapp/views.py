from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from .forms import CreateListingForm, ListingReviewForm, RegisterForm
from .models import (
    Category,
    CreditAccount,
    Listing,
    ListingReview,
    ListingStatus,
    Location,
    Photo,
    Transaction,
    User,
)


def _get_profile_user(request):
    user_id = request.session.get("user_id")
    profile_user = None

    if user_id:
        profile_user = User.objects.filter(id=user_id).first()


    if not profile_user and request.user.is_authenticated:
        profile_user = User.objects.filter(username=request.user.username).first()
        if profile_user:
            request.session["user_id"] = profile_user.id

    return profile_user

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
    profile_user = _get_profile_user(request)
    user_listings = Listing.objects.none()

    if profile_user:
        user_listings = Listing.objects.filter(user=profile_user).order_by("-createdDate")

    context = {
        "user": request.user,
        "user_id": request.session.get("user_id"),
        "profile_user": profile_user,
        "user_listings": user_listings,
    }
    return render(request, "profile/profile.html", context)


def about(request):
    return render(request, "about/about.html")


def products(request):
    listings = Listing.objects.all()
    listings_with_photos = []

    for listing in listings:
        primary_photo = listing.photo_set.filter(isPrimary=True).first()
        listings_with_photos.append({"listing": listing, "primary_photo": primary_photo})

    return render(request, "product-page/products.html", {"listings_with_photos": listings_with_photos})


def product_detail(request, listing_id):
    user_id = request.session.get("user_id")
    product = Listing.objects.filter(id=listing_id).first()
    if not product:
        return redirect("products")

    primary_photo = product.photo_set.filter(isPrimary=True).first()
    reviews = ListingReview.objects.filter(listing=product).order_by("-created_at")

    context = {
        "product": product,
        "primary_photo": primary_photo,
        "reviews": reviews,
        "review_form": ListingReviewForm(),
        "user_id": user_id,
    }
    return render(request, "product-page/product_detail.html", context)


@login_required
def add_review(request, listing_id):
    reviewer = _get_profile_user(request)
    if not reviewer:
        return redirect("login")

    listing = Listing.objects.filter(id=listing_id).first()
    if not listing:
        return redirect("products")

    if request.method == "POST":
        form = ListingReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.listing = listing
            review.reviewer = reviewer
            review.save()

    return redirect("product_details", listing_id=listing_id)


def contact(request):
    return render(request, "sidebar/contact.html")


@login_required
def messages(request):

    return render(request, "sidebar/messages.html")

@login_required
def settings(request):
    
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
        

def logout_view(request):
    logout(request)
    request.session.pop("user_id", None)
    return redirect("home")

def create_listing(request):
    profile_user = _get_profile_user(request)
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

            # Credit reward: free listings earn 1 credit.
            if listing.price <= 0:
                profile_user.credits_balance += 1
                profile_user.save(update_fields=["credits_balance"])
                credit_account.creditBalance += 1
                credit_account.save(update_fields=["creditBalance"])

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


@login_required
def delete_listing(request, listing_id):
    profile_user = _get_profile_user(request)
    if not profile_user:
        return redirect("login")

    listing = Listing.objects.filter(id=listing_id, user=profile_user).first()
    if listing and request.method in {"POST", "GET"}:
        listing.delete()

    return redirect("profile")


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
    return render(request, "profile/notifications.html", {"notifications": []})