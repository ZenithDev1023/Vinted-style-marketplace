from django.contrib.auth import login, logout
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


def get_nav_context(request):
    user_id = request.session.get("user_id")
    user = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            pass
    return {"user_id": user_id, "user": user}


def home(request):
    user_id = request.session.get("user_id")
    user = None
    if user_id:
        user = User.objects.filter(id=user_id).first()
    featured_listings = Listing.objects.all()[:6]
    return render(request, "home/home.html", {
        "user_id": user_id, "user": user, "featured_listings": featured_listings,
    })


def profile(request):
    profile_user = _get_profile_user(request)
    user_listings = Listing.objects.none()
    if profile_user:
     user_listings = Listing.objects.filter(user=profile_user).order_by("-createdDate")
    return render(request, "profile/profile.html", {
        **get_nav_context(request),
        "profile_user": profile_user,
        "user_listings": user_listings,
    })


def about(request):
    return render(request, "about/about.html", get_nav_context(request))


def products(request):
    listings = Listing.objects.all()
    listings_with_photos = []
    for listing in listings:
        primary_photo = listing.photo_set.filter(isPrimary=True).first()
        listings_with_photos.append({"listing": listing, "primary_photo": primary_photo})
    return render(request, "product-page/products.html", {
        **get_nav_context(request), "listings_with_photos": listings_with_photos,
    })


def product_detail(request, listing_id):
    product = Listing.objects.filter(id=listing_id).first()
    if not product:
        return redirect("products")
    primary_photo = product.photo_set.filter(isPrimary=True).first()
    reviews = ListingReview.objects.filter(listing=product).order_by("-created_at")
    other_listings = Listing.objects.exclude(id=listing_id)
    listings_with_photos = []
    for listing in other_listings:
        photo = listing.photo_set.filter(isPrimary=True).first()
        listings_with_photos.append({"listing": listing, "primary_photo": photo})
    return render(request, "product-page/product_detail.html", {
        **get_nav_context(request),
        "product": product,
        "primary_photo": primary_photo,
        "reviews": reviews,
        "review_form": ListingReviewForm(),
        "listings_with_photos": listings_with_photos,
    })


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
    return render(request, "sidebar/contact.html", get_nav_context(request))


def messages(request):
    return render(request, "sidebar/messages.html", get_nav_context(request))


def settings(request):
    return render(request, "sidebar/settings.html", get_nav_context(request))


def logout_view(request):
    logout(request)
    request.session.pop("user_id", None)
    return redirect("home")


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            request.session["user_id"] = user.id
            return redirect("login")
    else:
        form = RegisterForm()
    context = get_nav_context(request)
    context["form"] = form
    return render(request, "login-register/register.html", context)


def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            user = User.objects.get(username=username)
            if user.login(password):
                request.session["user_id"] = user.id
                return redirect("home")
            else:
                error = "Invalid password."
        except User.DoesNotExist:
            error = "No account found with that username."
    context = get_nav_context(request)
    context["error"] = error
    return render(request, "login-register/login.html", context)


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
                defaults={"postcode": "N/A", "city": "Unknown", "latitude": 0, "longitude": 0},
            )
            credit_account, _ = CreditAccount.objects.get_or_create(
                user=profile_user, defaults={"creditBalance": profile_user.credits_balance},
            )
            listing.category = default_category
            listing.location = default_location
            listing.creditAccount = credit_account
            listing.save()
            if listing.price <= 0:
                profile_user.credits_balance += 1
                profile_user.save(update_fields=["credits_balance"])
                credit_account.creditBalance += 1
                credit_account.save(update_fields=["creditBalance"])
            image_url = request.POST.get("image_url")
            if image_url:
                Photo.objects.create(
                    image_url=image_url, listing=listing,
                    category=default_category, isPrimary=True,
                )
            return redirect("products")
    else:
        form = CreateListingForm()
    return render(request, "listings/create_listing.html", {**get_nav_context(request), "form": form})


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
    return render(request, "listings/edit_listing.html", get_nav_context(request))


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
    return render(request, "listings/my_listings.html", {**get_nav_context(request), "listings": listings})


def transactions(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")
    user_transactions = Transaction.objects.none()
    return render(request, "profile/transactions.html", {**get_nav_context(request), "transactions": user_transactions})


def notifications(request):
    return render(request, "profile/notifications.html", {**get_nav_context(request), "notifications": []})
