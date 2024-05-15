from django.db import models


class Lobby(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    is_tournament = models.BooleanField(default=False)
    is_match_four = models.BooleanField(default=False)
    has_started = models.BooleanField(default=False)
    max_players = models.IntegerField()

    def __str__(self):
        return self.name


class Player(models.Model):
    lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE, related_name="players")
    name = models.CharField(max_length=12)
    channel_name = models.CharField(max_length=100, null=True)
    is_disconnected = models.BooleanField(default=True)
    is_eliminated = models.BooleanField(default=False)
    is_ai = models.BooleanField(default=False)

    def __str__(self):
        return self.name
