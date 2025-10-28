from django.urls import path

from .views import (
    ReservationCancelView,
    ReservationCreateView,
    ReservationListView,
    ReservationUpdateView,
)


app_name = "reservations"


urlpatterns = [
    path("new/", ReservationCreateView.as_view(), name="create"),
    path("my/", ReservationListView.as_view(), name="list"),
    path("<int:pk>/edit/", ReservationUpdateView.as_view(), name="update"),
    path("<int:pk>/cancel/", ReservationCancelView.as_view(), name="cancel"),
]
