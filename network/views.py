from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post, Follower


def index(request):
    from .forms import NewPostForm

    if request.method == 'POST' and request.user.is_authenticated:
        newPostForm = NewPostForm(request.POST)

        if newPostForm.is_valid():
            newPostContent = newPostForm.cleaned_data['newPostContent']

            newPost = Post.objects.create(
                poster=request.user,
                content=newPostContent
            )
            newPost.save()

            print('New post created successfully!')

    allPosts = Post.objects.order_by('-timestamp').all()

    return render(request, "network/index.html", {
        'newPostForm': NewPostForm(),
        'allPosts': allPosts
    })


def profilePage(request, profileId):
    profile = User.objects.get(id=profileId)

    followers = Follower.objects.filter(user_being_followed=profileId).all()
    following = Follower.objects.filter(user_follower=profileId).all()

    context = {
        'username': profile.username,
        'n_of_followers': len(followers),
        'n_following': len(following)
    }
    return render(request, 'network/profilePage.html', context)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
