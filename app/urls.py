from django.urls import path, re_path

from . import views
from . import consumers

urlpatterns = [
    path("", views.index, name="index"),
    path("join", views.join, name="join"),
    path("game", views.game, name="game"),
]

ws_urlpatterns = [
    re_path(r"ws/lobby/(?P<lobby_name>[\w\-\.]+)/$", consumers.LobbyConsumer.as_asgi()),
]
