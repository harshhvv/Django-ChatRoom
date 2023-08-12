from django.http import HttpResponse  # for testing
from django.shortcuts import render, redirect
from .models import Room, Topic
from .forms import RoomForm
from django.db.models import Q  # for search
from django.contrib.auth.models import User  # for login and logout
from django.contrib import messages  # §
from django.contrib.auth import authenticate, login, logout  # for login and logout
from django.contrib.auth.decorators import (
    login_required,
)  # decorator to require login for certain pages
from django.contrib.auth.forms import UserCreationForm  # for registration

# Create your views here.

# rooms = [
#     {"id": 1, "name": "Lets talk about Django"},
#     {"id": 2, "name": "Lets talk about Python"},
#     {"id": 3, "name": "Lets talk about JS"},
#     {"id": 4, "name": "Lets talk about React"},
# ]


def loginPage(request):
    page = "login"
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Username or password is incorrect")
    context = {"page": page}
    return render(request, "base/login_register.html", context)


def logoutUser(request):
    logout(request)
    return redirect("login")


def registerPage(request):
    # page = "register"
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # form.save()
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "An error has occurred during registration")

    context = {"form": form}
    return render(request, "base/login_register.html", context)


def home(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)
    )
    room_count = rooms.count()
    topics = Topic.objects.all()
    context = {"rooms": rooms, "topics": topics, "room_count": room_count}
    return render(request, "base/home.html", context)


def room(request, id):
    room = Room.objects.get(id=id)
    roomMessages = room.message_set.all().order_by("-created")
    context = {"room": room, "roomMessages": roomMessages}
    return render(request, "base/room.html", context)


@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()
    # if request is POST, then save the form
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")  # redirect to home page
    context = {"form": form}
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def updateRoom(request, id):
    room = Room.objects.get(id=id)
    form = RoomForm(instance=room)
    if request.user != room.host:
        return HttpResponse("<h1>You are not allowed to edit this room.</h1>")
    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect("home")
    context = {"form": form}
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def deleteRoom(request, id):
    room = Room.objects.get(id=id)
    if request.user != room.host:
        return HttpResponse("<h1>You are not allowed to edit this room.</h1>")
    if request.method == "POST":
        room.delete()
        return redirect("home")
    context = {"object": room}
    return render(request, "base/delete.html", context)
