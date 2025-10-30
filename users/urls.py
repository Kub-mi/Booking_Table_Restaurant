from django.urls import path

from .views import CustomLoginView, ProfileView, RegisterView


app_name = "users"


urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
