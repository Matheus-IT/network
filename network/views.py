from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post, Follower


def index(request):
    from .forms import NewPostForm

    if request.method == 'POST':
        if request.user.is_authenticated:
            newPostForm = NewPostForm(request.POST)

            if newPostForm.is_valid():
                newPostContent = newPostForm.cleaned_data['newPostContent']

                newPost = Post.objects.create(
                    poster=request.user,
                    content=newPostContent
                )
                newPost.save()

                print('New post created successfully!')
        else:
            return HttpResponse(status=403)

    allPosts = Post.objects.order_by('-timestamp').all()

    return render(request, "network/index.html", {
        'newPostForm': NewPostForm(),
        'allPosts': allPosts
    })


def checkVisitorIsFollowingThisProfile(visitor, profile):
    visitor_following_list = Follower.objects.filter(user_follower=visitor)

    for followed_by_visitor in visitor_following_list:
        if profile.id == followed_by_visitor.id:
            return True

    return False


def profilePage(request, profileId):
    try:
        profile = User.objects.get(id=profileId)
    except ObjectDoesNotExist:
        return HttpResponse(status=404)

    userPosts = Post.objects.order_by('-timestamp').filter(poster=profile)
    followers = Follower.objects.filter(user_being_followed=profileId).all()
    following = Follower.objects.filter(user_follower=profileId).all()

    if request.user.is_authenticated:
        visitor = User.objects.get(id=request.user.id)
        visitor_is_following = checkVisitorIsFollowingThisProfile(visitor, profile)
    else:
        visitor_is_following = False

    context = {
        'username': profile.username,
        'n_of_followers': len(followers),
        'n_following': len(following),
        'user_posts': userPosts,
        'visitor_is_following': visitor_is_following
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
