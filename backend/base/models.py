from django.contrib.auth.models import User
from django.db import models


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlists')
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} - {self.user.username}"

class WatchlistPosition(models.Model):
    watchlist = models.ForeignKey(Watchlist, on_delete=models.CASCADE, related_name='positions')
    ticker = models.CharField(max_length=10)
