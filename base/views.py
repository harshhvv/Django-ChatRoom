from django.http import HttpResponse  # for testing
from django.shortcuts import render, redirect
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
from django.db.models import Q  # for search
from django.contrib.auth.models import User  # for login and logout
from django.contrib import messages  # §
from django.contrib.auth import authenticate, login, logout  # for login and logout
from django.contrib.auth.decorators import (
    login_required,
)  # decorator to require login for certain pages
from django.contrib.auth.forms import UserCreationForm  # for registration


# Create your views here.
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
    return redirect("home")


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
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {
        "rooms": rooms,
        "topics": topics,
        "room_count": room_count,
        "room_messages": room_messages,
    }
    return render(request, "base/home.html", context)


def room(request, id):
    room = Room.objects.get(id=id)
    roomMessages = room.message_set.all().order_by("-created")
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user=request.user, room=room, body=request.POST.get("body")
        )
        room.participants.add(request.user)
        return redirect("room", id=room.id)
    context = {"room": room, "roomMessages": roomMessages, "participants": participants}
    return render(request, "base/room.html", context)


def userProfile(request, id):
    user = User.objects.get(id=id)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        "user": user,
        "rooms": rooms,
        "room_messages": room_messages,
        "topics": topics,
    }
    return render(request, "base/profile.html", context)


@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    # if request is POST, then save the form
    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        form = RoomForm(request.POST)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
        )
        return redirect("home")  # redirect to home page
    context = {"form": form, "topics": topics}
    return render(request, "base/room_form.html", context)


@login_required(login_url="login")
def updateRoom(request, id):
    room = Room.objects.get(id=id)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse("<h1>You are not allowed to edit this room.</h1>")
    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get("name")
        room.description = request.POST.get("description")
        room.topic = topic
        room.save()
        return redirect("home")
    context = {"form": form, "topics": topics}
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


@login_required(login_url="login")
def deleteMessage(request, id):
    message = Message.objects.get(id=id)
    if request.user != message.user:
        return HttpResponse("<h1>You are not allowed to edit this room.</h1>")
    if request.method == "POST":
        message.delete()
        return redirect("home")
    context = {"object": message}
    return render(request, "base/delete.html", context)


@login_required(login_url="login")
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user-profile", id=user.id)
    context = {"form": form}
    return render(request, "base/update-user.html", context)



def topicsPage(request):
    q = request.GET.get("q") if request.GET.get("q") != None else ""
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, "base/topics.html", {"topics": topics})

def activityPage(request):
    room_messages = Message.objects.all().order_by("-created")
    return render(request, "base/activity.html", {"room_messages": room_messages})