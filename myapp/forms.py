from django import forms
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from .models import DirectMessage, User, Listing, ListingReview


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=50)
    email = forms.EmailField()
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)
    postcode = forms.CharField(max_length=8, help_text="Used to show an approximate listing location.") 

    def clean_postcode(self):
        import re
        postcode = self.cleaned_data.get("postcode", "").strip().upper()
        pattern = r'^[A-Z]{1,2}[0-9]{1,2}[A-Z]?\s?[0-9][A-Z]{2}$'
        if postcode and not re.match(pattern, postcode):
            raise forms.ValidationError("Invalid postcode format.")
        return postcode

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        if User.objects.filter(username=cleaned_data.get("username")).exists():
            raise forms.ValidationError("Username already taken.")
        if User.objects.filter(email=cleaned_data.get("email")).exists():
            raise forms.ValidationError("Email already registered.")
        return cleaned_data

    def save(self):
        data = self.cleaned_data
        user = User(
            username=data["username"],
            email=data["email"],
            password_hash=data["password1"],
        )
        user.save()
        return user


class CreateListingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = self.fields["category"].queryset.order_by("name")

    class Meta:
        model = Listing
        fields = ["title", "description", "price", "condition", "category"]


class ListingReviewForm(forms.ModelForm):
    class Meta:
        model = ListingReview
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "comment": forms.Textarea(attrs={"rows": 3}),
        }
class DirectMessageForm(forms.ModelForm):
    class Meta:
        model = DirectMessage
        fields = ["content", "image"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 3, "placeholder": "Write your message..."}),
             }
        
    def clean(self):
        cleaned_data = super().clean()
        content = (cleaned_data.get("content") or "").strip()
        image = cleaned_data.get("image")

        if not content and not image:
            raise forms.ValidationError("Please enter a message or attach an image.")

        cleaned_data["content"] = content
        return cleaned_data

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "profile_photo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].max_length = 50
        self.fields["profile_photo"].required = False

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        duplicate = User.objects.filter(username=username).exclude(pk=self.instance.pk).exists()
        if duplicate:
            raise forms.ValidationError("Username already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        duplicate = User.objects.filter(email=email).exclude(pk=self.instance.pk).exists()
        if duplicate:
            raise forms.ValidationError("Email already registered.")
        return email

    def clean_profile_photo(self):
        uploaded_photo = self.cleaned_data.get("profile_photo")
        if not uploaded_photo:
            return uploaded_photo

        image = Image.open(uploaded_photo)
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
        elif image.mode == "L":
            image = image.convert("RGB")

        resized_image = image.resize((128, 128))
        image_bytes = BytesIO()
        resized_image.save(image_bytes, format="JPEG", quality=90)
        image_bytes.seek(0)

        return InMemoryUploadedFile(
            file=image_bytes,
            field_name="profile_photo",
            name=f"{uploaded_photo.name.rsplit('.', 1)[0]}_128.jpg",
            content_type="image/jpeg",
            size=image_bytes.getbuffer().nbytes,
            charset=None,
        )