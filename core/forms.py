from django import forms

from .models import ContactSubmission


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ["name", "email", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Your name"}),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "your@email.com"}
            ),
            "message": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "placeholder": "How can we help you?"}
            ),
        }
