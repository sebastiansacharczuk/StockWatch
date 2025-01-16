from django.urls import path
from .views import CustomTokenObtainPairView, CustomTokenRefreshView, logout, register, is_logged_in, get_watchlists, \
    create_watchlist, rename_watchlist, delete_watchlist, create_watchlist_position, delete_watchlist_position, \
    get_watchlist, get_calendar

urlpatterns = [
    path('login', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout', logout),
    path('token/refresh', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('register', register),
    path('authenticated', is_logged_in),
    path('get_watchlists', get_watchlists),
    path('get_watchlist', get_watchlist),
    path('create_watchlist', create_watchlist),
    path('rename_watchlist', rename_watchlist),
    path('delete_watchlist', delete_watchlist),
    path('create_watchlist_position', create_watchlist_position),
    path('delete_watchlist_position', delete_watchlist_position),
    path('get_calendar', get_calendar),
]
