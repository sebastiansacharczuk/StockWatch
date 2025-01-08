from django.urls import path
from .views import CustomTokenObtainPairView, CustomTokenRefreshView, logout, register, is_logged_in, get_watchlists, \
    create_watchlist, rename_watchlist, delete_watchlist

urlpatterns = [
    path('login', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout', logout),
    path('token/refresh', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('register', register),
    path('authenticated', is_logged_in),
    path('watchlists', get_watchlists),
    path('create_watchlist', create_watchlist),
    path('rename_watchlist', rename_watchlist),
    path('delete_watchlist', delete_watchlist)
]
