import re
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render


def index(request):
    return render(
        request,
        "app/index.django",
        # TODO: temporary test data, this will be retrieved from the db
        {
            "games": [
                {
                    "name": "first_game",
                    "type": "Tournament 1v1v1v1",
                    "current_players": 2,
                    "max_players": 4,
                },
                {
                    "name": "Sec-game",
                    "type": "Game 1v1v1v1",
                    "current_players": 4,
                    "max_players": 4,
                },
            ]
        },
    )


def join(request: HttpRequest):
    fields = request.POST.dict()

    # check fields
    if not all(
        key in fields for key in {"game-name", "type", "players", "player-name"}
    ):
        return HttpResponseBadRequest("Not all fields specified")

    # validate the `game-name` field
    if not bool(re.compile(r"^[\w\-\.]{1,100}$").match(fields["game-name"])):
        return HttpResponseBadRequest(
            "Game name must be a valid unicode string with length < 100 containing only ASCII alphanumerics, hyphens, underscores, or periods"
        )

    # validate the `player-name` field
    if len(fields["player-name"]) == 0:
        return HttpResponseBadRequest("Player name must not be empty")

    # validate the `type` & `players` fields
    # only check them if creating a new game
    # we detect if a new game is created by checking if `players` is an integer
    # (eg: new game="4"; existing game="2/4")
    try:
        player_count = int(fields["players"])
        match fields["type"]:
            case "Game 1v1", "Game 1vAI":
                if player_count != 2:
                    return HttpResponseBadRequest(
                        "Player count must be 2 for this game mode"
                    )
            case "Game 1v1v1v1", "Game 1v1vAIvAI":
                if player_count != 4:
                    return HttpResponseBadRequest(
                        "Player count must be 4 for this game mode"
                    )
            case "Tournament 1v1":
                if player_count % 2 != 0:
                    return HttpResponseBadRequest(
                        "Player count must be a modulo of 2 for this game mode"
                    )
            case "Tournament 1v1v1v1":
                if player_count % 4 != 0:
                    return HttpResponseBadRequest(
                        "Player count must be a modulo of 4 for this game mode"
                    )
            case _:
                return HttpResponseBadRequest("Invalid game mode")
    except ValueError:
        pass

    # TODO: check if the game is full

    return HttpResponse()
