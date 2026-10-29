from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]

    def clean_rating(self):
        rating = self.cleaned_data.get("rating")
        if rating is None or rating < 1 or rating > 5:
            raise forms.ValidationError("Rating harus antara 1 sampai 5.")
        return rating

    def clean_comment(self):
        comment = self.cleaned_data.get("comment", "").strip()
        if not comment:
            raise forms.ValidationError("Komentar ulasan tidak boleh kosong.")
        if len(comment) > 500:
            raise forms.ValidationError("Komentar tidak boleh melebihi 500 karakter.")
        return comment
