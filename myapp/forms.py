from django import forms
from .models import User

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=50)
    email = forms.EmailField()
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

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
