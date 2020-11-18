
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('getPosts/', views.getPosts, name='getPosts'),
    path('getPosts/<int:pageNumber>', views.getPosts, name='getPosts'),
    path("profile/<int:profileId>", views.ProfilePage.as_view(), name="profilePage"),
    path('following/', views.followingPage, name='followingPage'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
