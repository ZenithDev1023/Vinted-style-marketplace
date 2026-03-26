from django.db import models

# Create your models here.

# Listing Status Enum
class ListingStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    PENDING = "pending", "Pending"
    SOLD = "sold", "Sold"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


# Material Condition Enum
class MaterialCondition(models.TextChoices):
    NEW = "new", "New"
    GOOD = "good", "Good"
    USED = "used", "Used"
    DAMAGED = "damaged", "Damaged"


# Listing Type Enum
class ListingType(models.TextChoices):
    SALE = "sale", "Sale"
    TRADE = "trade", "Trade"
    FREE = "free", "Free"


# User model
class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    profile_photo = models.ImageField(upload_to="profiles/", null=True, blank=True)
    credits_balance = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def register(self):
        self.save()

    def login(self, password):
        return self.password_hash == password

    def updateprofile(self, username=None, email=None):
        if username:
            self.username = username
        if email:
            self.email = email 
        self.save()
    
    def getListings(self):
        return self.listing_set.all()

    def __str__(self):
        return f"( {self.username} | {self.email} | {self.credits_balance} | {self.created_at} )"


class Location(models.Model):
    postcode = models.CharField(max_length=20)
    city = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.city}"


# Credit model
class CreditAccount(models.Model):
    creditBalance = models.IntegerField()
    lastUpdated = models.DateField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def addCredits(self, amount):
        self.creditBalance += amount
        self.save()

    def deductCredits(self, amount):
        self.creditBalance -= amount
        self.save()

    def __str__(self):
        return f"( {self.creditBalance} | {self.lastUpdated} )"


# Product Listing model
class Listing(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    createdDate = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    creditAccount = models.ForeignKey(CreditAccount, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)

    condition = models.CharField(max_length=10, choices=MaterialCondition.choices)
    status = models.CharField(max_length=10, choices=ListingStatus.choices)
    credit_awarded_on_sale = models.BooleanField(default=False)

    def createListing(self):
        self.save()

    def editListing(self, title=None, description=None, price=None, category=None):
        if title:
            self.title = title 
        if description:
            self.description = description 
        if price:
            self.price = price 
        if category:
            self.category = category
        self.save()

    def deleteListing(self):
        self.delete()

    def markAsCompleted(self):
        self.status = ListingStatus.COMPLETED
        self.save()

    def __str__(self):
        return f"( {self.title} | {self.description} | {self.price} | {self.category} | {self.createdDate} )"



# Product Category
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"



# Product Photo model
class Photo(models.Model):
    image_url = models.URLField()
    uploadedDate = models.DateTimeField(auto_now_add=True)
    isPrimary = models.BooleanField(default=True)

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def uploadPhoto(self, image_url):
        self.image_url = image_url
        self.save()

    def deletePhoto(self):
        self.delete()

    def setAsPrimary(self):
        self.isPrimary = True
        self.save()

    def __str__(self):
        return f"( {self.image_url} | {self.uploadedDate} | {self.isPrimary} )"


# Transaction model
class Transaction(models.Model):
    amount = models.FloatField()
    creditUsed = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    transactionType = models.CharField(max_length=10, choices=ListingType.choices)
    status = models.CharField(max_length=10, choices=ListingStatus.choices)

    def completeTransaction(self):
        self.status = ListingStatus.COMPLETED
        self.save()

    def cancelTransaction(self):
        self.status = ListingStatus.CANCELLED
        self.save()

    def getReceipt(self):
        return f"Receipt: {self.amount} | {self.creditUsed} | {self.date} "


    def __str__(self):
        return f"{self.creditUsed}"


# User Review model
class Review(models.Model):
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)

    def leaveReview(self, rating=None, comment=None, created_at=None):
        if rating:
            self.rating = rating
        if comment:
            self.comment = comment
        if created_at:
            self.created_at = created_at
        self.save()

    def __str__(self):
        return f"( {self.rating} | {self.comment} | {self.created_at} )"

class ListingReview(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.listing.title} - {self.rating}/5"

# User Messaging model
class Message(models.Model):
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True) 
    read_status = models.BooleanField(default=False)

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)

    def sendMessage(self):
        return self.content

    def deleteMessage(self):
        self.delete()

    def __str__(self):
        return f"( {self.content} | {self.sent_at} | {self.read_status} )"




# Notification model
class Notification(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)

    def sendNotification(self):
        return self.message

    def __str__(self):
        return f"( {self.message} | {self.created_at} | {self.is_read} )"

class DirectMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    listing = models.ForeignKey(Listing, on_delete=models.SET_NULL, null=True, blank=True, related_name="direct_messages")
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to="messages/", null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    read_status = models.BooleanField(default=False)

    class Meta:
        ordering = ["sent_at"]

    def __str__(self):
        listing_title = self.listing.title if self.listing else "General"
        return f"{self.sender.username} -> {self.recipient.username} ({listing_title})"