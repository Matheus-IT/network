
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),

    path('getPostsPage/', views.getPostsPage, name='getPostsPage'),
    path('getPostsPage/<int:pageNumber>', views.getPostsPage, name='getPostsPage'),
    path('getPostsPage/<int:pageNumber>/<int:filterUserId>', views.getPostsPage, name='getPostsPage'),

    path('handleLikeDislike/<int:postId>', views.handleLikeDislike, name='handleLikeDislike'),

    path("profile/<int:profileId>", views.ProfilePage.as_view(), name="profilePage"),
    path('following/', views.followingPage, name='followingPage'),

    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
