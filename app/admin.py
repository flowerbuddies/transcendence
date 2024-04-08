from django.contrib import admin

from app.models import Lobby, Player


class PlayerInline(admin.TabularInline):
    model = Player
    extra = 0


class LobbyAdmin(admin.ModelAdmin):
    inlines = [PlayerInline]


admin.site.register(Lobby, LobbyAdmin)
admin.site.register(Player)
