from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Subquery
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import Post,User,UserFollowing
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def index(request):
    if request.method =="GET":
        posts=Post.objects.all().order_by("-timestamp").all()
        paginator = Paginator(posts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, "network/index.html",{
            "page_obj":page_obj,
        })
    else:
        body=request.POST["body"]
        post= Post.objects.create(created_by=request.user, body=body)
        return HttpResponseRedirect(reverse("index"))

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

def profile(request,user_id):
    if request.method == "GET":
        user_profile = User.objects.get(id=user_id)
        followers=user_profile.followers.all().count()
        following=user_profile.following.all().count()
        is_following=True
        try:
            UserFollowing.objects.get(user_id=request.user,following_user_id=user_profile)
        except UserFollowing.DoesNotExist:
            is_following=False
        if user_profile==request.user:
            is_user = True
        else:
            is_user = False
        posts = Post.objects.filter(created_by=user_profile).order_by("-timestamp").all()
        return render(request, "network/profile.html",{
            "user_profile": user_profile,
            "followers": followers,
            "following": following,
            "posts": posts,
            "is_user":is_user,
            "is_following":is_following
        })
    else:
        user_profile = User.objects.get(id=user_id)
        try:
            following=UserFollowing.objects.get(user_id=request.user,following_user_id=user_profile)
            following.delete()
        except UserFollowing.DoesNotExist:
            following=UserFollowing.objects.create(user_id=request.user,following_user_id=user_profile)
        return HttpResponseRedirect(reverse("profile" , kwargs={'user_id':user_profile.id} ))   

@login_required
def following(request):
    user_prof= User.objects.get(pk=request.user.pk)
    following=[]
    for a in request.user.following.all():
        following.append(a.following_user_id)
    posts = Post.objects.filter(created_by__in=following).order_by("-timestamp")
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/following.html",{
    "page_obj":page_obj,
    })

@login_required
def edit(request,post_id):
    post= Post.objects.get(id=post_id)
    if request.method == "GET":
        if post.created_by==request.user:
            return render(request, "network/edit.html",{"post":post})
        else:
            return render(request,"network/apology.html",{"message":"Sorry, you can't edit this post."})
    else:
        post.body = request.POST['body']
        post.save(update_fields=["body"])
        return HttpResponseRedirect(reverse("index"))

@csrf_exempt
@login_required
def like(request, post_id):
    post = Post.objects.get(id=post_id)
    user = User.objects.get(username=request.user.username)
    if request.method == "POST":
        post.liked_users.add(user)
        likes=post.likes
        post.likes=likes+1
        post.save()
        return JsonResponse({"likes":likes+1})
    else:
        post.liked_users.remove(user)
        likes=post.likes
        post.likes=likes-1
        post.save()
        return JsonResponse({"likes":likes-1})

