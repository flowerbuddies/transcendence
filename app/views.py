from django.shortcuts import render


def index(request):
    return render(
        request,
        "app/index.django",
        # TODO: temporary test data, this will be retrieved from the db
        {
            "games": [
                {
                    "name": "Game 1",
                    "type": "Tournament 1v1v1v1",
                    "current_players": 2,
                    "max_players": 4,
                },
                {
                    "name": "Game 2",
                    "type": "Game 1v1v1v1",
                    "current_players": 4,
                    "max_players": 4,
                },
            ]
        },
    )
