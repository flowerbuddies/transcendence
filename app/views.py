import json
from django.utils.translation import gettext as _
import re
from math import log
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from app.models import Lobby
from django.template.defaulttags import register
from django.core import serializers
from django.forms.models import model_to_dict


def is_power_of_two(n: int) -> bool:
    if n <= 0:
        return False
    return log(n, 2).is_integer()


def is_power_of_four(n: int) -> bool:
    if n <= 0:
        return False
    return log(n, 4).is_integer()


@register.filter
def qset_length(qset):
    return len(qset.all())


def index(request: HttpRequest):
    if request.META.get("HTTP_ACCEPT") == "application/json":
        json_lobbies = json.loads(serializers.serialize("json", Lobby.objects.all()))
        return JsonResponse(
            {"lobbies": list(map(lambda lobby: lobby["fields"]["name"], json_lobbies))}
        )

    return render(request, "app/index.django", {"lobbies": Lobby.objects.all()})


def game(request: HttpRequest):
    if request.META.get("HTTP_ACCEPT") == "application/json":
        lobby_name = request.GET.get("name")
        if lobby_name == None:
            return JsonResponse({"error": "No name specified"}, status=400)

        first_lobby = Lobby.objects.filter(name=lobby_name).first()
        if first_lobby == None:
            return JsonResponse(
                {"error": f"Lobby {lobby_name} doesn't exist"}, status=400
            )

        return JsonResponse(model_to_dict(first_lobby))

    return render(request, "app/game.django")


def join(request: HttpRequest):
    if request.method == "GET":
        return render(request, "app/join.django", {"lobbies": Lobby.objects.all()})

    fields = request.POST.dict()

    # check that the request has all the mandatory fields
    if not all(
        key in fields for key in {"lobby-name", "type", "players", "player-1-name"}
    ):
        return HttpResponseBadRequest(_("views.fields.empty"))

    # check the `lobby-name` field
    if not bool(re.compile(r"^[a-zA-Z0-9\_\-\.]{1,99}$").match(fields["lobby-name"])):
        return HttpResponseBadRequest(_("input.group_name.incorrect_characters"))

    # check the `player-1-name` field length
    if not (1 <= len(fields["player-1-name"]) <= 12):
        return HttpResponseBadRequest(_("input.player_name.length"))

    # check if the `player-1-name` field is purely whitespace
    if fields["player-1-name"] and fields["player-1-name"].isspace():
        return HttpResponseBadRequest(_("input.player_name.whitespace"))

    # check the `player-2-name` field length
    if fields["player-2-name"] and not (1 <= len(fields["player-2-name"]) <= 12):
        return HttpResponseBadRequest(_("input.player_name.length"))

    # check if the `player-2-name` field is purely whitespace
    if fields["player-2-name"] and fields["player-2-name"].isspace():
        return HttpResponseBadRequest(_("input.player_name.whitespace"))

    # check that `player-1-name` and `player-2-name` fields are not the same value
    if fields["player-1-name"] == fields["player-2-name"]:
        return HttpResponseBadRequest(_("input.player_name.same"))

    is_tournament = False
    is_match_four = False
    player_count = -1

    # check the `type` & `players` fields
    # only check them if creating a new lobby
    # we detect if a new lobby is created by checking if `players` is an integer
    # (eg: new lobby="4"; existing lobby="2/4")
    try:
        player_count = int(fields["players"])
        game_type = fields["type"]

        if game_type in ["join.type.types.game1v1", "join.type.types.game1vAI"]:
            if player_count != 2:
                return HttpResponseBadRequest(_("input.game1v1.count"))
        elif game_type in [
            "join.type.types.game1v1v1v1",
            "join.type.types.game1v1vAIvAI",
        ]:
            is_match_four = True
            if player_count != 4:
                return HttpResponseBadRequest(_("input.game1v1v1v1.count"))
        elif game_type == "join.type.types.tournament1v1":
            is_tournament = True
            if not is_power_of_two(player_count):
                return HttpResponseBadRequest(_("input.tournament1v1.count"))
        elif game_type == "join.type.types.tournament1v1v1v1":
            is_tournament = True
            is_match_four = True
            if not is_power_of_four(player_count):
                return HttpResponseBadRequest(_("input.tournament1v1v1v1.count"))
        else:
            return HttpResponseBadRequest(_("input.game_mode.invalid"))

    except ValueError:
        # if the last player of a lobby disconnects, the lobby is deleted.
        # but if a player got the join view with this lobby not full yet,
        # the request will be wrongly formatted, we account for this here and will return not doesn't exist
        if not Lobby.objects.filter(name=fields["lobby-name"]).exists():
            return HttpResponseBadRequest(_("input.lobby.nonexistent"))
        # if it's not an int, it just means the user is trying to join an existing game

    lobby, created = Lobby.objects.get_or_create(
        name=fields["lobby-name"],
        defaults={
            "name": fields["lobby-name"],
            "type": fields["type"],
            "is_tournament": is_tournament,
            "is_match_four": is_match_four,
            "max_players": player_count,
        },
    )

    # when creating a lobby with AI players, add them already
    if created:
        if game_type == "join.type.types.game1vAI":
            lobby.players.create(name="AI", is_ai=True, is_disconnected=True)
        elif game_type == "join.type.types.game1v1vAIvAI":
            lobby.players.create(name="AI 1", is_ai=True, is_disconnected=True)
            lobby.players.create(name="AI 2", is_ai=True, is_disconnected=True)

    if len(lobby.players.all()) == lobby.max_players:
        return HttpResponseBadRequest(_("input.lobby.full"))
    if fields["player-2-name"] and len(lobby.players.all()) + 1 == lobby.max_players:
        return HttpResponseBadRequest(_("input.lobby.one_spot"))
    if lobby.players.filter(name=fields["player-1-name"]).exists():
        return HttpResponseBadRequest(_("input.player_name.one_taken"))
    if (
        fields["player-2-name"]
        and lobby.players.filter(name=fields["player-2-name"]).exists()
    ):
        return HttpResponseBadRequest(_("input.player_name.two_taken"))
    lobby.players.create(name=fields["player-1-name"])
    if fields["player-2-name"]:
        lobby.players.create(name=fields["player-2-name"])

    return HttpResponse()
