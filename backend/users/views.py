from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from .models import Watchlist
from .serializers import UserSerializer, UserRegisterSerializer, WatchlistSerializer
from .utils import format_response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_watchlists(request):
    user = request.user
    watchlists = Watchlist.objects.filter(user=user)
    serializer = WatchlistSerializer(watchlists, many=True)
    return Response(format_response(status=True, return_data=serializer.data))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_watchlist(request):
    user = request.user
    watchlist_name = request.data.get('watchlist_name')
    watchlist = Watchlist.objects.create(user=user, name=watchlist_name)
    serializer = WatchlistSerializer(watchlist)
    return Response(format_response(status=True, return_data=serializer.data))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rename_watchlist(request):
    user = request.user
    watchlist_id = request.data.get('watchlist_id')  # Name of the watchlist to rename
    new_name = request.data.get('watchlist_name')  # New name for the watchlist

    # Retrieve the specific watchlist
    try:
        watchlist = Watchlist.objects.get(user=user, id=watchlist_id)
    except Watchlist.DoesNotExist:
        return Response(format_response(status=False, error_descr="Watchlist not found"), status=404)

    # Update the name
    watchlist.name = new_name
    watchlist.save()

    # Serialize the updated instance
    serializer = WatchlistSerializer(watchlist)
    return Response(format_response(status=True, return_data=serializer.data))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_watchlist(request):
    user = request.user
    watchlist_id = request.data.get('watchlist_id')

    # Validate input
    if not watchlist_id:
        return Response(
            format_response(status=False, error_descr="'watchlist_id' is required"),
            status=400
        )

    try:
        watchlist = Watchlist.objects.get(user=user, id=watchlist_id)
        watchlist.delete()
        return Response(format_response(status=True))
    except Watchlist.DoesNotExist:
        return Response(format_response(status=False, error_descr="Watchlist not found"), status=404)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)
    res = Response()
    if serializer.is_valid():
        serializer.save()
        return Response(format_response(status=True, return_data=serializer.data))
    return Response(format_response(status=False, error_descr=serializer.errors))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):

    try:
        res = Response(format_response(status=True))
        res.delete_cookie('access_token', path='/', samesite='None')
        res.delete_cookie('response_token', path='/', samesite='None')

        return res

    except Exception as e:
        print(e)
        return Response(format_response(status=False))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def is_logged_in(request):
    serializer = UserSerializer(request.user, many=False)

    return Response(format_response(status=True, return_data=serializer.data))


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            tokens = response.data

            access_token = tokens['access']
            refresh_token = tokens['refresh']

            # serializer = UserSerializer(request.user, many=False)

            res = Response(format_response(status=True))

            res.set_cookie(
                key='access_token',
                value=str(access_token),
                httponly=True,
                secure=True,
                samesite='None',
                path='/'
            )

            res.set_cookie(
                key='refresh_token',
                value=str(refresh_token),
                httponly=True,
                secure=True,
                samesite='None',
                path='/'
            )
            res.data.update(tokens)
            return res

        except Exception as e:
            print(e)
            return Response(format_response(status=False, error_descr=e.args))


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')

            request.data['refresh'] = refresh_token

            response = super().post(request, *args, **kwargs)

            tokens = response.data
            access_token = tokens['access']

            res = Response(format_response(status=True))

            res.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=False,
                samesite='None',
                path='/'
            )
            return res

        except Exception as e:
            print(e)
            return Response(format_response(status=False))


