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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        required_fields = [
            "full_name",
            "faculty",
            "student_id",
            "phone_number",
            "address",
        ]

        for field_name in required_fields:
            self.fields[field_name].required = True

        self.fields["bio"].required = False

    def clean_student_id(self):
        student_id = self.cleaned_data["student_id"].strip()

        if not student_id.isdigit():
            raise forms.ValidationError("NPM hanya boleh berisi angka.")

        return student_id

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"].strip()
        allowed_chars = set("0123456789+- ")

        if not all(char in allowed_chars for char in phone_number):
            raise forms.ValidationError(
                "Nomor telepon hanya boleh berisi angka, +, - , atau spasi."
            )

        digits = [char for char in phone_number if char.isdigit()]

        if len(digits) < 8 or len(digits) > 15:
            raise forms.ValidationError(
                "Nomor telepon harus terdiri dari 8–15 digit."
            )

        return phone_number

    def clean_full_name(self):
        full_name = self.cleaned_data["full_name"].strip()

        if not full_name:
            raise forms.ValidationError(
                "Nama lengkap tidak boleh kosong."
            )

        if not any(char.isalpha() for char in full_name):
            raise forms.ValidationError(
                "Nama lengkap harus mengandung huruf."
            )

        return full_name

    def clean_address(self):
        address = self.cleaned_data["address"].strip()

        if not address:
            raise forms.ValidationError(
                "Alamat tidak boleh kosong."
            )

        return address

    def clean_faculty(self):
        faculty = self.cleaned_data["faculty"].strip()

        if not faculty:
            raise forms.ValidationError(
                "Fakultas tidak boleh kosong."
            )

        return faculty

    