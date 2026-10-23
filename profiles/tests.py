from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile
from .forms import ProfileForm, RegisterForm


class ProfileFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="mahasiswa",
            password="testpassword123",
        )

        self.profile = Profile.objects.create(
            user=self.user,
        )

    def get_valid_data(self):
        return {
            "full_name": "Budi Santoso",
            "faculty": "Fasilkom",
            "student_id": "123456789",
            "phone_number": "+628123456789",
            "address": "Depok, Jawa Barat",
            "bio": "",
        }

    def test_valid_profile_form(self):
        form = ProfileForm(data=self.get_valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_student_id_must_contain_only_digits(self):
        data = self.get_valid_data()
        data["student_id"] = "123ABC"

        form = ProfileForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("student_id", form.errors)

    def test_phone_number_must_have_valid_format(self):
        data = self.get_valid_data()
        data["phone_number"] = "0812ABC"

        form = ProfileForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)

    def test_full_name_cannot_be_blank(self):
        data = self.get_valid_data()
        data["full_name"] = "   "

        form = ProfileForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("full_name", form.errors)

    def test_address_cannot_be_blank(self):
        data = self.get_valid_data()
        data["address"] = "   "

        form = ProfileForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("address", form.errors)

    def test_faculty_cannot_be_blank(self):
        data = self.get_valid_data()
        data["faculty"] = "   "

        form = ProfileForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("faculty", form.errors)


class RegisterFormTest(TestCase):
    def get_valid_data(self):
        return {
            "username": "mahasiswa",
            "email": "mahasiswa@ui.ac.id",
            "password1": "ContohPassword123!",
            "password2": "ContohPassword123!",
        }

    def test_ui_email_is_accepted(self):
        form = RegisterForm(data=self.get_valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_non_ui_email_is_rejected(self):
        data = self.get_valid_data()
        data["email"] = "mahasiswa@gmail.com"

        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)