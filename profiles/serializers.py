from rest_framework import serializers

from .forms import ProfileForm
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    is_staff = serializers.BooleanField(source="user.is_staff", read_only=True)

    class Meta:
        model = Profile
        fields = ["username", "email", "is_staff", "full_name", "faculty", "student_id",
                  "phone_number", "address", "bio"]

    def validate(self, attrs):
        # Reuse the existing website rules, including partial profile updates.
        fields = ProfileForm.Meta.fields
        values = {name: attrs.get(name, getattr(self.instance, name, "")) for name in fields}
        form = ProfileForm(values, instance=self.instance)
        if not form.is_valid():
            raise serializers.ValidationError(dict(form.errors))
        return {key: form.cleaned_data[key] for key in attrs}
