from django.urls import path

from . import views
from . import consumers

urlpatterns = [
    path("", views.index, name="index"),
]

ws_urlpatterns = [
    path("ws/game/", consumers.GameConsumer.as_asgi()),
]
