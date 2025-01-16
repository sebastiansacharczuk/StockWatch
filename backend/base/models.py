from django.contrib.auth.models import User
from django.db import models
from datetime import datetime
from django.utils.timezone import make_aware

import logging

logger = logging.getLogger(__name__)

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlists')
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} - {self.user.username}"

class WatchlistPosition(models.Model):
    watchlist = models.ForeignKey(Watchlist, on_delete=models.CASCADE, related_name='positions')
    ticker = models.CharField(max_length=10)



class CalendarEvent(models.Model):
    country = models.CharField(max_length=2)
    current = models.CharField(max_length=255, null=True, blank=True)
    forecast = models.CharField(max_length=255, null=True, blank=True)
    impact = models.IntegerField()
    period = models.CharField(max_length=255)
    previous = models.CharField(max_length=255, null=True, blank=True)
    time = models.DateTimeField()
    title = models.CharField(max_length=255)


def save_calendar_data(calendar_data):
    CalendarEvent.objects.all().delete()
    events = []
    batch_size = 100  # Adjust batch size as needed
    for record in calendar_data:
        naive_time = datetime.fromtimestamp(record['time'] / 1000)
        aware_time = make_aware(naive_time)

        events.append(CalendarEvent(
            country=record['country'],
            current=record.get('current', ''),
            forecast=record.get('forecast', ''),
            impact=int(record['impact']),
            period=record['period'],
            previous=record.get('previous', ''),
            time=aware_time,
            title=record['title']
        ))
        if len(events) >= batch_size:
            CalendarEvent.objects.bulk_create(events)
            events = []
    if events:
        CalendarEvent.objects.bulk_create(events)
