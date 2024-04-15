from django.utils.translation import gettext as _
import re
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from app.models import Lobby
from django.template.defaulttags import register


@register.filter
def qset_length(qset):
    return len(qset.all())


def index(request):
    return render(request, "app/index.django", {"lobbies": Lobby.objects.all()})


def game(request):
    return render(request, "app/game.django")


def join(request: HttpRequest):
    if request.method == "GET":
        return render(request, "app/join.django", {"lobbies": Lobby.objects.all()})

    fields = request.POST.dict()

    # check that the request has all the mondatory fields
    if not all(
        key in fields for key in {"lobby-name", "type", "players", "player-1-name"}
    ):
        return HttpResponseBadRequest("Not all fields specified")

    # check the `lobby-name` field
    if not bool(re.compile(r"^[\w\-\.]{1,100}$").match(fields["lobby-name"])):
        return HttpResponseBadRequest(
            "Lobby name must be a valid unicode string with length < 100 containing only ASCII alphanumerics, hyphens, underscores, or periods"
        )

    # check the `player-1-name` field
    if not (1 <= len(fields["player-1-name"]) <= 12):
        return HttpResponseBadRequest(
            "Player 1 name must be between 1 and 12 characters"
        )

    # check the `player-2-name` field
    if fields["player-2-name"] and not (1 <= len(fields["player-2-name"]) <= 12):
        return HttpResponseBadRequest(
            "Player 2 name must be between 1 and 12 characters"
        )

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
                return HttpResponseBadRequest(
                    "Player count must be 2 for this game mode"
                )
        elif game_type in [
            "join.type.types.game1v1v1v1",
            "join.type.types.game1v1vAIvAI",
        ]:
            is_match_four = True
            if player_count != 4:
                return HttpResponseBadRequest(
                    "Player count must be 4 for this game mode"
                )
        elif game_type == "join.type.types.tournament1v1":
            is_tournament = True
            if player_count % 2:
                return HttpResponseBadRequest(
                    "Player count must be a modulo of 2 for this game mode"
                )
        elif game_type == "join.type.types.tournament1v1v1v1":
            is_tournament = True
            is_match_four = True
            if player_count % 4:
                return HttpResponseBadRequest(
                    "Player count must be a modulo of 4 for this game mode"
                )
        else:
            return HttpResponseBadRequest("Invalid game mode")

    except ValueError:
        pass  # If it's not an int, it just means the user is trying to join an existing game

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
            lobby.players.create(name="AI", is_ai=True)
        elif game_type == "join.type.types.game1v1vAIvAI":
            lobby.players.create(name="AI 1", is_ai=True)
            lobby.players.create(name="AI 2", is_ai=True)

    if len(lobby.players.all()) == lobby.max_players:
        return HttpResponseBadRequest("The lobby is full")
    if fields["player-2-name"] and len(lobby.players.all()) + 1 == lobby.max_players:
        return HttpResponseBadRequest("Only one spot left")
    if lobby.players.filter(name=fields["player-1-name"]).exists():
        return HttpResponseBadRequest("Player 1 name already taken")
    if (
        fields["player-2-name"]
        and lobby.players.filter(name=fields["player-2-name"]).exists()
    ):
        return HttpResponseBadRequest("Player 2 name already taken")
    lobby.players.create(name=fields["player-1-name"])
    if fields["player-2-name"]:
        lobby.players.create(name=fields["player-2-name"])

    return HttpResponse()
