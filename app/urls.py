from django.urls import path, re_path

from . import views
from . import consumers

urlpatterns = [
    path("", views.index, name="index"),
    path("join", views.join, name="join"),
]

ws_urlpatterns = [
    re_path(r"ws/game/(?P<game_name>[\w\-\.]+)/$", consumers.GameConsumer.as_asgi()),
]
