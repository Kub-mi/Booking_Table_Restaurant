from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CustomUser


class StyledAuthenticationForm(AuthenticationForm):
    """Authentication form with Bootstrap styling for the login page."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Имя пользователя"
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Имя пользователя"}
        )
        self.fields["password"].label = "Пароль"
        self.fields["password"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Пароль"}
        )


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Имя пользователя"
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Имя пользователя"}
        )
        self.fields["email"].label = "Электронная почта"
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "ivanov@example.com"}
        )
        self.fields["password1"].label = "Пароль"
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Пароль"}
        )
        self.fields["password2"].label = "Подтверждение пароля"
        self.fields["password2"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Повторите пароль",
            }
        )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("first_name", "last_name", "email")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }
        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "email": "Электронная почта",
        }
