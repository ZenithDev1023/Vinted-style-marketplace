from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User as AuthUser

from .models import Listing, ListingStatus, MaterialCondition


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = AuthUser
        fields = ["username", "email", "password1", "password2"]


class CreateListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "price", "condition"]

    condition = forms.ChoiceField(choices=MaterialCondition.choices)

    def save(self, commit=True):
        listing = super().save(commit=False)
        if not listing.status:
            listing.status = ListingStatus.ACTIVE
        if commit:
            listing.save()
        return listing