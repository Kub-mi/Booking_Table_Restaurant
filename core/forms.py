from django import forms
from django.utils.translation import gettext_lazy as _

from .models import ContactSubmission


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ["name", "email", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": _("Ваше имя")}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": _("ваш@email.com")}
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": _("Как мы можем вам помочь?"),
                }
            ),
        }
