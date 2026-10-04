from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


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