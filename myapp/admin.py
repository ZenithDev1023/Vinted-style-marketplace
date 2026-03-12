from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Location)
admin.site.register(CreditAccount)
admin.site.register(Listing)
admin.site.register(Category)
admin.site.register(Photo)
admin.site.register(Transaction)
admin.site.register(Review)
admin.site.register(Message)
admin.site.register(Notification)
