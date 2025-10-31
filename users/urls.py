from django.urls import path
from django.contrib.auth import views as auth_views
from .views import ProfileView, RegisterView
from .forms import BootstrapAuthenticationForm
from . import views


app_name = "users"


urlpatterns = [
    path("login/", auth_views.LoginView.as_view(
        template_name="registration/login.html",
        authentication_form=BootstrapAuthenticationForm
    ), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
