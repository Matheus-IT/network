from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View

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


class ProfilePage(View):
    template_name = 'network/profilePage.html'

    def _checkVisitorIsFollowingThisProfile(self, request, profile_followers):
        """ In case of a visitor authenticated, this should tell if the visitor
            of this page is following this profile """
        from django.contrib.auth.models import AnonymousUser

        if isinstance(request.user, AnonymousUser):
            return False

        visitor = User.objects.get(id=request.user.id)

        if visitor.id in map(lambda profile_follower: profile_follower.id, profile_followers):
            return True
        return False

    def get(self, request, profileId):
        try:
            profile = User.objects.get(id=profileId)
        except ObjectDoesNotExist:
            return HttpResponse(status=404)

        profile_posts = Post.objects.order_by('-timestamp').filter(poster=profile)
        # get a list of profile followers from each Follower that is related to this profile
        profile_followers = [profile_follower.user_follower for profile_follower in profile.followers.all()]
        profile_following = profile.users_being_followed.all()

        visitor_is_following = self._checkVisitorIsFollowingThisProfile(request, profile_followers)

        context = {
            'username': profile.username,
            'n_of_followers': len(profile_followers),
            'n_following': len(profile_following),
            'profile_posts': profile_posts,
            'visitor_is_following': visitor_is_following
        }

        return render(request, self.template_name, context)

    def put(self, request, profileId):
        import json

        try:
            profile = User.objects.get(id=profileId)
        except ObjectDoesNotExist:
            return HttpResponse(status=404)

        data = json.loads(request.body)
        visitor = request.user

        if data['visitor_is_following']:
            try:
                follower = Follower.objects.get(
                    user_follower = visitor,
                    user_being_followed = profile
                )
            except ObjectDoesNotExist:
                # create Follower, making the visitor follow this profile
                follower = Follower.objects.create(
                    user_follower = visitor,
                    user_being_followed = profile
                )
                follower.save()
                return JsonResponse({'msg': 'Success! Now the visitor is following this profile'}, status=204)
            else:
                return JsonResponse({'msg': 'This visitor is already following this profile!'}, status=400)
        else:
            # delete Follower
            try:
                follower = Follower.objects.get(
                    user_follower = visitor,
                    user_being_followed = profile
                )
                follower.delete()
                return JsonResponse({'msg': 'Success! Now the visitor is no longer following this profile'}, status=204)
            except ObjectDoesNotExist:
                return JsonResponse({'msg': 'Error: the object does not exist'}, status=400)




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
