from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from django.views import View

from .models import User, Post, Follower, Like
from . import utils


# ------------------------ API VIEWS ------------------------
def getPostsPage(request, templatePageName=None, pageNumber=1, filterUserId=None):
    from django.core.paginator import Paginator, EmptyPage

    if filterUserId:
        # try to filter the posts given the user id
        try:
            filtered_user = User.objects.get(id=filterUserId)
        except ObjectDoesNotExist:
            return JsonResponse({'msg': 'This user doesn\'t exist'}, status=404)

        posts = Post.objects.order_by('-timestamp').filter(poster=filtered_user)
    elif templatePageName == 'following':
        # filter the posts by the profiles the current user follows
        current_user = request.user
        # get a list of users being followed by the current user
        followed_by_current_user = [follower.user_being_followed for follower in current_user.users_being_followed.all()]
        # get a list of posts made by the users that the current user follow
        posts = [post for post in Post.objects.order_by('-timestamp').all() if post.poster in followed_by_current_user]
    else:
        posts = Post.objects.order_by('-timestamp').all()

    POSTS_PER_PAGE = 10
    paginator = Paginator(posts, POSTS_PER_PAGE)

    try:
        page = paginator.page(pageNumber)
    except EmptyPage:
        return JsonResponse({'msg': 'This page doesn\'t exist'}, status=404)
    
    current_page_posts = [post.serialize() for post in page.object_list]
    
    for post in current_page_posts:
        post['does_current_visitor_like_this_post'] = utils.doesThisUserLikeThisPost(request.user, post)

    posts_page = {
        'hasNext': page.has_next(),
        'hasPrevious': page.has_previous(),
        'currentPagePosts': current_page_posts
    }
    return JsonResponse(posts_page)


def handleLikeDislike(request, postId):
    import json
    
    try:
        post = Post.objects.get(id=postId)
    except ObjectDoesNotExist:
        return JsonResponse({'msg': 'No post found with this id'}, status=404)
    
    data = json.loads(request.body)
    visitor = request.user

    if data['does_current_visitor_like_this_post']:
        try:
            # verify if the user is trying to like for the second time
            like = post.likes.get(liker=visitor)
            if like:
                return JsonResponse({'msg': 'Error: You can\'t like the same post two times'}, status=400)
        except ObjectDoesNotExist:
            like = Like.objects.create(liker=visitor, post=post)
            like.save()
            return JsonResponse(post.serialize(), status=200)
    else:
        # dislike
        try:
            like = post.likes.get(liker=visitor)
            like.delete()
            return JsonResponse(post.serialize(), status=200)
        except ObjectDoesNotExist:
            return JsonResponse({'msg': 'Error: You tried to dislike someone you don\'t like'}, status=400)

# ------------------------ NORMAL VIEWS ------------------------
def index(request):
    from .forms import NewPostForm
    from django.core.paginator import Paginator

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
        else:
            return HttpResponse(status=403)

    allPosts = Post.objects.order_by('-timestamp').all()
    paginator = Paginator(allPosts, 10)

    return render(request, "network/index.html", {
        'new_post_form': NewPostForm(),
        'page_range': paginator.page_range
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
        from django.core.paginator import Paginator
        
        try:
            profile = User.objects.get(id=profileId)
        except ObjectDoesNotExist:
            return HttpResponse(status=404)

        profile_posts = Post.objects.order_by('-timestamp').filter(poster=profile)
        # get a list of profile followers from each Follower that is related to this profile
        profile_followers = [profile_follower.user_follower for profile_follower in profile.followers.all()]
        profile_following = profile.users_being_followed.all()

        visitor_is_following = self._checkVisitorIsFollowingThisProfile(request, profile_followers)

        paginator = Paginator(profile_posts, 10)
        
        context = {
            'profile_id': profile.id,
            'username': profile.username,
            'n_of_followers': len(profile_followers),
            'n_following': len(profile_following),
            'profile_posts': profile_posts,
            'visitor_is_following': visitor_is_following,
            'page_range': paginator.page_range
        }

        return render(request, self.template_name, context)

    def _getFollowerObject(self, profile, visitor):
        return Follower.objects.get(
            user_follower = visitor,
            user_being_followed = profile
        )

    def _createFollowerObject(self, profile, visitor):
        return Follower.objects.create(
            user_follower = visitor,
            user_being_followed = profile
        )

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
                self._getFollowerObject(profile, visitor)
            except ObjectDoesNotExist:
                # create Follower, making the visitor follow this profile
                follower = self._createFollowerObject(profile, visitor)
                follower.save()
                return JsonResponse({'msg': 'Success! Now the visitor is following this profile'}, status=200)
            else:
                return JsonResponse({'msg': 'This visitor is already following this profile!'}, status=400)
        else:
            # delete Follower
            try:
                follower = self._getFollowerObject(profile, visitor)
                follower.delete()
                return JsonResponse({'msg': 'Success! Now the visitor is no longer following this profile'}, status=200)
            except ObjectDoesNotExist:
                return JsonResponse({'msg': 'Error: the object does not exist'}, status=400)


@login_required
def followingPage(request):
    from django.core.paginator import Paginator
    
    current_user = request.user

    # get a list of users being followed by the current user
    followed_by_current_user = [follower.user_being_followed for follower in current_user.users_being_followed.all()]
    # get a list of posts made by the users that the current user follow
    posts_from_users_followed = [post for post in Post.objects.order_by('-timestamp').all() if post.poster in followed_by_current_user]
    print(posts_from_users_followed)
    paginator = Paginator(posts_from_users_followed, 10)

    return render(request, 'network/followingPage.html', {
        'posts_from_users_followed': posts_from_users_followed,
        'page_range': paginator.page_range
    })


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
