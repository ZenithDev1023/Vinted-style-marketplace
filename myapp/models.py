from django.db import models

# Create your models here.

# User model
class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    profile_photo = models.ImageField(upload_to="profiles/", null=True, blank=True)
    credits_balance = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    creditAccount = models.ForeignKey(CreditAccount, on_delete=models.CASCADE)

    def __str__(self):
        return f"( {self.username} | {self.email} | {self.credits_balance} | {self.created_at} )"


class Location(models.Model):
    postcode = models.CharField(max_length=20)
    city = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.city


# Credit model
class CreditAccount(models.Model):
    creditBalance = models.IntegerField()
    lastUpdated = models.DateField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f"( {self.creditBalance} | {self.lastUpdated} )"


# Product Listing model
class Listing(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    price = models.FloatField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    createdDate = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    creditAccount = models.ForeignKey(CreditAccount, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    status = models.ForeignKey(ListingStatus, on_delete=models.CASCADE)
    condition = models.ForeignKey(MaterialCondition, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)

    def __str__(self):
        return f"( {self.title} | {self.description} | {self.price} | {self.category} | {self.createdDate} )"



# Product Category
class Category(models.Model):
    name = models.CharField(max_length=100)

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)

    def __str__(self):
        return self.name



# Product Photo model
class Photo(models.Model):
    image_url = models.URLField()
    uploadedDate = models.DateTimeField(auto_now_add=True)
    isPrimary = models.BooleanField(default=True)

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f"( {self.image_url} | {self.uploadedDate} | {self.isPrimary} )"





# Transaction model
class Transaction(models.Model):
    amount = models.FloatField()
    creditUsed = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    transactionType = models.ForeignKey(ListingType, models=on_delete)
    status = models.ForeignKey(ListingStatus, models=on_delete)


    def __str__(self):
        return f"( {self.amount} | {self.creditUsed} | {self.date} )"


# User Review model
class Review(models.Model):
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)

    def __str__(self):
        return f"( {self.rating} | {self.comment} | {self.created_at} )"


# User Messaging model
class Message(models.Model):
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True) 
    read_status = models.BooleanField(default=False)

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)

    def __str__(self):
        return f"( {self.content} | {self.sent_at} | {self.read_status} )"


# Notification model
class Notification(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)

    def __str__(self):
        return f"( {self.message} )"



# Listing Status Enum
class ListingStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    PENDING = "pending", "Pending"
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