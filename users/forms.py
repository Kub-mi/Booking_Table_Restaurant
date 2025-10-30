from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CustomUser


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{classes} form-control".strip()
        self.fields["username"].help_text = (
            "Обязательное поле. Не более 150 символов: буквы, цифры и символы @/./+/-/_."
        )
        self.fields["username"].label = "Имя пользователя"
        self.fields["email"].label = "Электронная почта"
        self.fields["password1"].label = "Пароль"
        self.fields["password1"].help_text = (
            "Пароль не должен быть похож на имя пользователя, состоять только из цифр "
            "или быть короче 8 символов."
        )
        self.fields["password2"].label = "Подтверждение пароля"
        self.fields["password2"].help_text = "Введите пароль ещё раз для подтверждения."


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ["username", "password"]:
            classes = self.fields[name].widget.attrs.get("class", "")
            self.fields[name].widget.attrs["class"] = f"{classes} form-control".strip()
        self.fields["username"].label = "Имя пользователя"
        self.fields["password"].label = "Пароль"


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
