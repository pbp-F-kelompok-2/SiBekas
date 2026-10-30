from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.urls import reverse
from order.models import Order
import uuid

from .models import Profile, Favorite
from .forms import ProfileForm, RegisterForm
from product.models import Product


class ProfileFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="mahasiswa",
            password="testpassword123",
        )
        self.profile = Profile.objects.create(user=self.user)

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


    def test_student_id_is_stripped(self):
        data = self.get_valid_data()
        data["student_id"] = " 123456789 "

        form = ProfileForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["student_id"], "123456789")

    def test_phone_number_must_have_8_to_15_digits(self):
        for phone in ["1234567", "1234567890123456"]:
            data = self.get_valid_data()
            data["phone_number"] = phone

            form = ProfileForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn("phone_number", form.errors)

    def test_full_name_must_contain_letters(self):
        data = self.get_valid_data()
        data["full_name"] = "123456"

        form = ProfileForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("full_name", form.errors)

    def test_optional_bio_can_be_blank(self):
        data = self.get_valid_data()
        data["bio"] = ""

        form = ProfileForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_full_name_with_only_symbols_is_rejected(self):
        data = self.get_valid_data()
        data["full_name"] = "12345"

        form = ProfileForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("full_name", form.errors)


    def test_address_with_only_whitespace_is_rejected(self):
        data = self.get_valid_data()
        data["address"] = "   "

        form = ProfileForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("address", form.errors)


    def test_faculty_with_only_whitespace_is_rejected(self):
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

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(
            username="existinguser",
            email="existing@ui.ac.id",
            password="Password123!",
        )

        data = self.get_valid_data()
        data["email"] = "existing@ui.ac.id"
        data["username"] = "newuser"

        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="mahasiswa",
            password="testpassword123",
        )

    def test_profile_is_connected_to_user(self):
        profile = Profile.objects.create(user=self.user)

        self.assertEqual(profile.user, self.user)
        self.assertEqual(self.user.profile, profile)

    def test_profile_string_representation(self):
        profile = Profile.objects.create(user=self.user)

        self.assertEqual(str(profile), "Profil mahasiswa")


class FavoriteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="mahasiswa",
            password="testpassword123",
        )

        self.product = Product.objects.create(
            seller=self.user,
            name="Buku Test",
            description="Buku bekas untuk pengujian",
            price=50000,
            stock=1,
        )

    def test_favorite_can_be_created(self):
        favorite = Favorite.objects.create(
            user=self.user,
            product=self.product,
        )

        self.assertEqual(favorite.user, self.user)
        self.assertEqual(favorite.product, self.product)

    def test_same_product_cannot_be_favorited_twice(self):
        Favorite.objects.create(
            user=self.user,
            product=self.product,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Favorite.objects.create(
                    user=self.user,
                    product=self.product,
                )

    def test_favorite_string_representation(self):
        favorite = Favorite.objects.create(
            user=self.user,
            product=self.product,
        )

        self.assertEqual(
            str(favorite),
            "mahasiswa - Buku Test",
        )


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="mahasiswa",
            email="mahasiswa@ui.ac.id",
            password="TestPassword123!",
        )
        self.profile = Profile.objects.create(user=self.user)

    def test_profile_page_requires_login(self):
        response = self.client.get(reverse("profile:index"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/profile/login/", response.url)

    def test_logged_in_user_can_access_profile_page(self):
        self.client.login(
            username="mahasiswa",
            password="TestPassword123!",
        )

        response = self.client.get(reverse("profile:index"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["profile"], self.profile)

    def test_edit_profile_requires_login(self):
        response = self.client.get(reverse("profile:edit"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/profile/login/", response.url)

    def test_logged_in_user_can_update_profile(self):
        self.client.login(
            username="mahasiswa",
            password="TestPassword123!",
        )

        response = self.client.post(
            reverse("profile:edit"),
            {
                "full_name": "Budi Santoso",
                "faculty": "Fasilkom",
                "student_id": "123456789",
                "phone_number": "+628123456789",
                "address": "Depok, Jawa Barat",
                "bio": "Mahasiswa UI",
            },
        )

        self.assertRedirects(response, reverse("profile:index"))

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.full_name, "Budi Santoso")
        self.assertEqual(self.profile.bio, "Mahasiswa UI")

    def test_invalid_profile_data_is_not_saved(self):
        self.client.login(
            username="mahasiswa",
            password="TestPassword123!",
        )

        response = self.client.post(
            reverse("profile:edit"),
            {
                "full_name": "   ",
                "faculty": "Fasilkom",
                "student_id": "123456789",
                "phone_number": "+628123456789",
                "address": "Depok, Jawa Barat",
                "bio": "",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.full_name, "")

    def test_user_cannot_edit_another_users_profile(self):
        other_user = User.objects.create_user(
            username="otheruser",
            email="other@ui.ac.id",
            password="Password123!",
        )
        other_profile = Profile.objects.create(
            user=other_user,
            full_name="Profil Orang Lain",
            faculty="Fasilkom",
            student_id="1234567890",
            phone_number="081234567890",
            address="Depok",
        )

        self.client.force_login(self.user)

        self.client.post(
            reverse("profile:edit"),
            {
                "full_name": "Profil Diubah",
                "faculty": "Fasilkom",
                "student_id": "123456789",
                "phone_number": "+628123456789",
                "address": "Depok",
                "bio": "",
            },
        )

        other_profile.refresh_from_db()
        self.assertEqual(other_profile.full_name, "Profil Orang Lain")

    def test_register_success(self):
        response = self.client.post(
            reverse("profile:register"),
            {
                "username": "newstudent",
                "email": "newstudent@ui.ac.id",
                "password1": "StrongPassword123!",
                "password2": "StrongPassword123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            User.objects.filter(email="newstudent@ui.ac.id").exists()
        )

    def test_get_edit_profile_redirects_to_profile_index(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("profile:edit"))

        self.assertRedirects(response, reverse("profile:index"))


class ProfileActionViewTest(TestCase):
    # Login behavior
    def test_login_with_unknown_email_fails(self):
        response = self.client.post(
            reverse("profile:login"),
            {
                "email": "unknown@ui.ac.id",
                "password": "TestPassword123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_with_valid_next_url_redirects_there(self):
        response = self.client.post(
            reverse("profile:login"),
            {
                "email": self.user.email,
                "password": "TestPassword123!",
                "next": "/product/",
            },
        )

        self.assertRedirects(
            response,
            "/product/",
            fetch_redirect_response=False,
        )

    def test_login_get_displays_login_page(self):
        response = self.client.get(reverse("profile:login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/login.html")

    def setUp(self):
        self.user = User.objects.create_user(
            username="mahasiswa",
            email="mahasiswa@ui.ac.id",
            password="TestPassword123!",
        )

        self.product = Product.objects.create(
            seller=self.user,
            name="Buku Test",
            description="Buku bekas untuk pengujian",
            price=50000,
            stock=1,
        )

    def test_toggle_favorite_requires_post(self):
        self.client.login(
            username="mahasiswa",
            password="TestPassword123!",
        )

        response = self.client.get(
            reverse(
                "profile:toggle_favorite",
                kwargs={"slug": self.product.slug},
            )
        )

        self.assertEqual(response.status_code, 405)

    def test_toggle_favorite_requires_login(self):
        response = self.client.post(
            reverse(
                "profile:toggle_favorite",
                kwargs={"slug": self.product.slug},
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f"/profile/login/?next=/profile/favorite/{self.product.slug}/",
        )
        self.assertFalse(
            Favorite.objects.filter(
                user=self.user,
                product=self.product,
            ).exists()
        )

    def test_user_can_add_favorite(self):
        self.client.login(
            username="mahasiswa",
            password="TestPassword123!",
        )

        response = self.client.post(
            reverse(
                "profile:toggle_favorite",
                kwargs={"slug": self.product.slug},
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Favorite.objects.filter(
                user=self.user,
                product=self.product,
            ).exists()
        )

    def test_user_can_remove_favorite(self):
        Favorite.objects.create(
            user=self.user,
            product=self.product,
        )

        self.client.login(
            username="mahasiswa",
            password="TestPassword123!",
        )

        self.client.post(
            reverse(
                "profile:toggle_favorite",
                kwargs={"slug": self.product.slug},
            )
        )

        self.assertFalse(
            Favorite.objects.filter(
                user=self.user,
                product=self.product,
            ).exists()
        )

    def test_delete_account_requires_post(self):
        self.client.login(
            username="mahasiswa",
            password="TestPassword123!",
        )

        response = self.client.get(reverse("profile:delete_account"))

        self.assertEqual(response.status_code, 405)

    def test_user_can_delete_account_without_protected_orders(self):
        self.client.login(
            username="mahasiswa",
            password="TestPassword123!",
        )

        response = self.client.post(reverse("profile:delete_account"))

        self.assertRedirects(response, reverse("product:index"))
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    def test_login_rejects_external_next_url(self):
        response = self.client.post(
            reverse("profile:login"),
            {
                "email": self.user.email,
                "password": "TestPassword123!",
                "next": "https://evil.example.com",
            },
        )

        self.assertRedirects(
            response,
            reverse("profile:index"),
            fetch_redirect_response=False,
        )

    def test_logout_ends_user_session(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("profile:logout"))

        self.assertRedirects(
            response,
            reverse("profile:login"),
            fetch_redirect_response=False,
        )
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_with_wrong_password_fails(self):
        response = self.client.post(
            reverse("profile:login"),
            {
                "email": self.user.email,
                "password": "WrongPassword123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)


class ProfileSecurityTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="mahasiswa",
            email="mahasiswa@ui.ac.id",
            password="TestPassword123!",
        )

    def test_account_with_order_history_cannot_be_deleted(self):
        order = Order.objects.create(
            checkout_key=uuid.uuid4(),
            buyer=self.user,
            recipient_name="Budi Santoso",
            phone_number="081234567890",
            address="Depok, Jawa Barat",
            delivery_method=Order.DeliveryMethod.PICKUP,
            shipping_service="Pickup",
            shipping_cost=0,
            subtotal=50000,
            total=50000,
            weight_grams=500,
            payment_method=Order.PaymentMethod.COD,
        )

        self.client.login(
            username="mahasiswa",
            password="TestPassword123!",
        )

        response = self.client.post(
            reverse("profile:delete_account")
        )

        self.assertRedirects(
            response,
            reverse("profile:index"),
        )
        self.assertTrue(
            User.objects.filter(pk=self.user.pk).exists()
        )
        self.assertTrue(
            Order.objects.filter(pk=order.pk).exists()
        )

