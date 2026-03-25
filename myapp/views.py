import json
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.db.models import Case, Count, IntegerField, Q, When
from django.template.defaultfilters import slugify

from .forms import CreateListingForm, DirectMessageForm, ListingReviewForm, RegisterForm
from .models import (
    Category,
    CreditAccount,
    DirectMessage,
    Listing,
    ListingReview,
    ListingStatus,
    Location,
    Photo,
    Transaction,
    User,
)

DISCOVER_CATEGORY_NAMES = [
    "Hand Tools",
    "Power Tools",
    "Equipment",
    "Safety Gear",
    "Materials",
    "Trade Vehicles",
]


def _discover_categories_queryset(with_counts=False):
    for category_name in DISCOVER_CATEGORY_NAMES:
        Category.objects.get_or_create(name=category_name)

    custom_order = Case(
        *[When(name=name, then=position) for position, name in enumerate(DISCOVER_CATEGORY_NAMES)],
        output_field=IntegerField(),
    )
    queryset = Category.objects.filter(name__in=DISCOVER_CATEGORY_NAMES).annotate(sort_order=custom_order)
    if with_counts:
        queryset = queryset.annotate(listing_count=Count("listing"))
    return queryset.order_by("sort_order")


def _geocode_postcode(postcode):
    """Return an approximate (city, lat, lon) tuple for a postcode."""
    if not postcode:
        return ("Unknown", 0.0, 0.0)

    query = quote_plus(postcode.strip())
    url = f"https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=gb,us,ca,au&q={query}"
    request = Request(url, headers={"User-Agent": "TradeXMarketplace/1.0"})

    try:
        with urlopen(request, timeout=4) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if payload:
            result = payload[0]
            city = result.get("display_name", "Unknown").split(",")[0]
            return (
                city or "Unknown",
                float(result.get("lat", 0.0)),
                float(result.get("lon", 0.0)),
            )
    except Exception:
        pass

    return ("Unknown", 0.0, 0.0)



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
    discovered_categories = _discover_categories_queryset(with_counts=True)
    counts_by_slug = {
        slugify(category.name.strip()): category.listing_count for category in discovered_categories
    }
    return render(request, "home/home.html", {
        "user_id": user_id,
        "user": user,
        "featured_listings": featured_listings,
        "hand_tools_count": counts_by_slug.get("hand-tools", 0),
        "power_tools_count": counts_by_slug.get("power-tools", 0),
        "equipment_count": counts_by_slug.get("equipment", 0),
        "safety_count": counts_by_slug.get("safety-gear", 0),
        "materials_count": counts_by_slug.get("materials", 0),
        "vehicles_count": counts_by_slug.get("vehicles", 0) + counts_by_slug.get("trade-vehicles", 0),
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
    discover_categories = _discover_categories_queryset(with_counts=True)
    listings = Listing.objects.all()
    category_filter = request.GET.get("category", "").strip()
    if category_filter:
        category_aliases = {
            "hand-tools": ["hand tools"],
            "power-tools": ["power tools"],
            "equipment": ["equipment"],
            "safety-gear": ["safety gear"],
            "materials": ["materials"],
            "vehicles": ["vehicles", "trade vehicles"],
            "trade-vehicles": ["trade vehicles", "vehicles"],
        }
        normalized_filter = category_filter.lower()
        names_to_match = category_aliases.get(normalized_filter, [category_filter.replace("-", " ")])
        category_query = Q()
        for name in names_to_match:
            category_query |= Q(category__name__iexact=name)
        listings = listings.filter(category_query)
    listings_with_photos = []
    for listing in listings:
        primary_photo = listing.photo_set.filter(isPrimary=True).first()
        listings_with_photos.append({"listing": listing, "primary_photo": primary_photo})
    discovered_categories = (
        Category.objects.annotate(listing_count=Count("listing"))
        .order_by("-listing_count", "name")
    )
    return render(request, "product-page/products.html", {
        **get_nav_context(request),
        "listings_with_photos": listings_with_photos,
        "discovered_categories": discover_categories,
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
        "can_message_seller": bool(request.session.get("user_id")) and request.session.get("user_id") != product.user_id,
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

def _build_message_threads(profile_user):
    message_qs = (
        DirectMessage.objects.filter(Q(sender=profile_user) | Q(recipient=profile_user))
        .select_related("sender", "recipient", "listing")
        .order_by("-sent_at")
    )

    threads = {}
    for message in message_qs:
        partner = message.recipient if message.sender_id == profile_user.id else message.sender
        key = (partner.id, message.listing_id or 0)
        if key not in threads:
            threads[key] = {"partner": partner, "listing": message.listing, "listing_id": message.listing_id, "latest": message}
    return list(threads.values())


def messages(request):
    profile_user = _get_profile_user(request)
    if not profile_user:
        return redirect("login")

    selected_partner = None
    selected_listing = None
    chat_messages = DirectMessage.objects.none()

    recipient_id = request.GET.get("recipient")
    listing_id = request.GET.get("listing")
    if recipient_id:
        selected_partner = User.objects.filter(id=recipient_id).first()
        if selected_partner and selected_partner.id == profile_user.id:
            selected_partner = None

    if listing_id and listing_id.isdigit():
        selected_listing = Listing.objects.filter(id=listing_id).first()

    if request.method == "POST" and selected_partner:
        form = DirectMessageForm(request.POST)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.sender = profile_user
            new_message.recipient = selected_partner
            new_message.listing = selected_listing
            new_message.save()
            return redirect(f"{request.path}?recipient={selected_partner.id}&listing={selected_listing.id if selected_listing else ''}")
    else:
        form = DirectMessageForm()

    if selected_partner:
        filters = Q(sender=profile_user, recipient=selected_partner) | Q(sender=selected_partner, recipient=profile_user)
        if selected_listing:
            filters &= Q(listing=selected_listing)
        chat_messages = DirectMessage.objects.filter(filters).select_related("sender", "recipient").order_by("sent_at")
        chat_messages.filter(recipient=profile_user, read_status=False).update(read_status=True)

    context = {
        **get_nav_context(request),
        "threads": _build_message_threads(profile_user),
        "selected_partner": selected_partner,
        "selected_listing": selected_listing,
        "selected_partner_id": selected_partner.id if selected_partner else None,
        "selected_listing_id": selected_listing.id if selected_listing else None,
        "chat_messages": chat_messages,
        "message_form": form,
    }
    return render(request, "sidebar/messages.html", context)


def start_conversation(request, listing_id):
    profile_user = _get_profile_user(request)
    if not profile_user:
        return redirect("login")

    listing = Listing.objects.filter(id=listing_id).select_related("user").first()
    if not listing:
        return redirect("products")

    if listing.user_id == profile_user.id:
        return redirect("messages")

    return redirect(f"/messages/?recipient={listing.user_id}&listing={listing.id}")


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
            postcode = form.cleaned_data.get("postcode", "").strip()
            city, lat, lon = _geocode_postcode(postcode)
            Location.objects.update_or_create(
                user=user,
                defaults={"postcode": postcode, "city": city, "latitude": lat, "longitude": lon},
            )
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
    discover_categories = _discover_categories_queryset()
    profile_user = _get_profile_user(request)
    if not profile_user:
        return redirect("login")
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        form.fields["category"].queryset = discover_categories
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = profile_user
            listing.status = ListingStatus.ACTIVE
            default_location, _ = Location.objects.get_or_create(
                user=profile_user,
                defaults={"postcode": "N/A", "city": "Unknown", "latitude": 0, "longitude": 0},
            )
            if default_location.postcode and default_location.latitude == 0 and default_location.longitude == 0:
                city, lat, lon = _geocode_postcode(default_location.postcode)
                if lat or lon:
                    default_location.city = city
                    default_location.latitude = lat
                    default_location.longitude = lon
                    default_location.save(update_fields=["city", "latitude", "longitude"])
            credit_account, _ = CreditAccount.objects.get_or_create(
                user=profile_user, defaults={"creditBalance": profile_user.credits_balance},
            )
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
                    category=listing.category, isPrimary=True,
                )
            return redirect("products")
    else:
        form = CreateListingForm()
        form.fields["category"].queryset = discover_categories
    return render(request, "listings/create_listing.html", {**get_nav_context(request), "form": form})


def edit_listing(request, listing_id):
    discover_categories = _discover_categories_queryset()
    profile_user = _get_profile_user(request)
    if not profile_user:
        return redirect("login")

    listing = Listing.objects.filter(id=listing_id, user=profile_user).first()
    if not listing:
        return redirect("profile")

    if request.method == "POST":
        form = CreateListingForm(request.POST, instance=listing)
        form.fields["category"].queryset = discover_categories
        if form.is_valid():
            updated_listing = form.save()
            image_url = request.POST.get("image_url", "").strip()
            if image_url:
                primary_photo = updated_listing.photo_set.filter(isPrimary=True).first()
                if primary_photo:
                    primary_photo.image_url = image_url
                    primary_photo.category = updated_listing.category
                    primary_photo.save(update_fields=["image_url", "category"])
                else:
                    Photo.objects.create(
                        image_url=image_url,
                        listing=updated_listing,
                        category=updated_listing.category,
                        isPrimary=True,
                    )
            return redirect("profile")
    else:
        form = CreateListingForm(instance=listing)
        form.fields["category"].queryset = discover_categories

    primary_photo = listing.photo_set.filter(isPrimary=True).first()
    return render(
        request,
        "listings/edit_listing.html",
        {
            **get_nav_context(request),
            "form": form,
            "listing": listing,
            "image_url": primary_photo.image_url if primary_photo else "",
        },
    )


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
