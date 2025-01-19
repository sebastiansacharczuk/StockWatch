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

class SymbolRecord(models.Model):
    symbol = models.CharField(max_length=50)
    description = models.TextField()
    category_name = models.CharField(max_length=50)
    group_name = models.CharField(max_length=50)
    currency = models.CharField(max_length=10)
    currency_pair = models.BooleanField()
    currency_profit = models.CharField(max_length=10)
    contract_size = models.FloatField()
    leverage = models.FloatField()
    lot_min = models.FloatField()
    lot_max = models.FloatField()
    lot_step = models.FloatField()
    precision = models.IntegerField()
    pips_precision = models.IntegerField()
    swap_enable = models.BooleanField()
    swap_long = models.FloatField()
    swap_short = models.FloatField()
    swap_type = models.IntegerField()
    trailing_enabled = models.BooleanField()
    short_selling = models.BooleanField()
    long_only = models.BooleanField()

    def __str__(self):
        return self.symbol

def refresh_symbol_data(symbol_data):
    SymbolRecord.objects.all().delete()
    symbols = []
    batch_size = 100  # Adjust batch size as needed
    for record in symbol_data:
        symbols.append(SymbolRecord(
            symbol=record['symbol'],
            description=record['description'],
            category_name=record['categoryName'],
            group_name=record['groupName'],
            currency=record['currency'],
            currency_pair=record['currencyPair'],
            currency_profit=record['currencyProfit'],
            contract_size=record['contractSize'],
            leverage=record['leverage'],
            lot_min=record['lotMin'],
            lot_max=record['lotMax'],
            lot_step=record['lotStep'],
            precision=record['precision'],
            pips_precision=record['pipsPrecision'],
            swap_enable=record['swapEnable'],
            swap_long=record['swapLong'],
            swap_short=record['swapShort'],
            swap_type=record['swapType'],
            trailing_enabled=record['trailingEnabled'],
            short_selling=record['shortSelling'],
            long_only=record['longOnly']
        ))
        if len(symbols) >= batch_size:
            SymbolRecord.objects.bulk_create(symbols)
            symbols = []
    if symbols:
        SymbolRecord.objects.bulk_create(symbols)


class CalendarEvent(models.Model):
    country = models.CharField(max_length=2)
    current = models.CharField(max_length=255, null=True, blank=True)
    forecast = models.CharField(max_length=255, null=True, blank=True)
    impact = models.IntegerField()
    period = models.CharField(max_length=255)
    previous = models.CharField(max_length=255, null=True, blank=True)
    time = models.DateTimeField()
    title = models.CharField(max_length=255)


def refresh_calendar_data(calendar_data):
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
