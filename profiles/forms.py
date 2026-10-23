from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email UI",
        help_text="Gunakan email dengan domain @ui.ac.id.",
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data["email"].lower()

        if not email.endswith("@ui.ac.id"):
            raise forms.ValidationError(
                "Gunakan email dengan domain @ui.ac.id."
            )

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Email tersebut sudah terdaftar."
            )

        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "full_name",
            "faculty",
            "student_id",
            "phone_number",
            "address",
            "bio",
        ]

        labels = {
            "full_name": "Nama Lengkap",
            "faculty": "Fakultas",
            "student_id": "NPM",
            "phone_number": "Nomor Telepon",
            "address": "Alamat",
            "bio": "Tentang Saya",
        }

        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "bio": forms.Textarea(attrs={"rows": 3}),
        }
