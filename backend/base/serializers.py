from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Watchlist, WatchlistPosition, CalendarEvent, SymbolRecord


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class WatchlistPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchlistPosition
        fields = ['id', 'ticker']

class WatchlistSerializer(serializers.ModelSerializer):
    positions = WatchlistPositionSerializer(many=True, read_only=True)
    class Meta:
        model = Watchlist
        fields = ['id', 'name', 'positions']

class GetWatchlistSerializer(serializers.ModelSerializer):
    watchlist_id = serializers.UUIDField()

    class Meta:
        model = Watchlist  # Replace Watchlist with the appropriate model name
        fields = ['watchlist_id']  # Include all fields you want in the serializer


class CreateWatchlistSerializer(serializers.Serializer):
    watchlist_name = serializers.CharField(max_length=255)

class RenameWatchlistSerializer(serializers.Serializer):
    watchlist_id = serializers.IntegerField()
    watchlist_name = serializers.CharField(max_length=255)

class DeleteWatchlistSerializer(serializers.Serializer):
    watchlist_id = serializers.IntegerField()

class CreateWatchlistPositionSerializer(serializers.Serializer):
    watchlist_id = serializers.IntegerField()
    ticker = serializers.CharField(max_length=10)

class DeleteWatchlistPositionSerializer(serializers.Serializer):
    watchlist_id = serializers.IntegerField()
    watchlist_position_id = serializers.IntegerField()


class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = [
            'id',
            'country',
            'current',
            'forecast',
            'impact',
            'period',
            'previous',
            'time',
            'title'
        ]


class SymbolRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymbolRecord
        fields = '__all__'
