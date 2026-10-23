from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    full_name = models.CharField(max_length=150, blank=True)
    faculty = models.CharField(max_length=100, blank=True)
    student_id = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Profil {self.user.username}"