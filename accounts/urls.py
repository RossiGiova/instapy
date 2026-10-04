from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("accounts/signup/", views.SignUpView.as_view(), name="signup"),
    path("accounts/login/", views.LoginView.as_view(), name="login"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("accounts/me/", views.MeView.as_view(), name="me"),
    path("accounts/settings/", views.ProfileUpdateView.as_view(), name="settings"),
    path("accounts/delete/", views.AccountDeleteView.as_view(), name="delete"),
    path("search/", views.UserSearchView.as_view(), name="search"),
    path("u/<str:username>/", views.ProfileView.as_view(), name="profile"),
    path("u/<str:username>/follow/", views.follow_toggle, name="follow"),
]
