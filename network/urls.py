from django.urls import path

from . import views

urlpatterns = [
    # ------------------------ API URLS ------------------------
    path('getPostsProfilePage/<int:filterUserId>/<int:pageNumber>', views.getPostsPage, name='getPostsPageGivenUserId'),
    path('getPostsPage/<str:templatePageName>/<int:pageNumber>', views.getPostsPage, name='getPostsPageGivenTemplate'),

    path('handleLikeDislike/<int:postId>', views.handleLikeDislike, name='handleLikeDislike'),
    path('handleSaveNewPostContent/<int:postId>', views.handleSaveNewPostContent, name='handleSaveNewPostContent'),

    # ------------------------ NORMAL URLS ------------------------
    path("", views.index, name="index"),

    path("profile/<int:profileId>", views.ProfilePage.as_view(), name="profilePage"),
    path('following/', views.followingPage, name='followingPage'),

    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
