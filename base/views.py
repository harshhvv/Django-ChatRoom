from django.http import HttpResponse
from django.shortcuts import render
from .models import Room
from .forms import RoomForm


# Create your views here.

rooms = [
    {"id": 1, "name": "Lets talk about Django"},
    {"id": 2, "name": "Lets talk about Python"},
    {"id": 3, "name": "Lets talk about JS"},
    {"id": 4, "name": "Lets talk about React"},
]


def home(request):
    rooms = Room.objects.all()
    context = {"rooms": rooms}
    return render(request, "base/home.html", context)


def room(request, id):
    room = Room.objects.get(id=id)
    context = {"room": room}
    return render(request, "base/room.html", context)


def createRoom(request):
    form = RoomForm()
    context = {"form": form}
    return render(request, "base/create_room.html", context)
