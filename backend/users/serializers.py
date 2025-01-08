from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Watchlist, WatchlistPosition


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


class WatchlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watchlist
        fields = ['id', 'name']

class WatchlistPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchlistPosition
        fields = ['id', 'ticker']