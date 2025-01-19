from datetime import datetime, timedelta

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from .models import Watchlist, WatchlistPosition, CalendarEvent, refresh_calendar_data, refresh_symbol_data
from .serializers import WatchlistSerializer, WatchlistPositionSerializer, UserSerializer, UserRegisterSerializer, \
    CreateWatchlistSerializer, RenameWatchlistSerializer, DeleteWatchlistPositionSerializer, \
    CreateWatchlistPositionSerializer, DeleteWatchlistSerializer, GetWatchlistSerializer, CalendarEventSerializer
from .utils import format_response
from .xtbapi.XTBAPIService import XTBAPIService

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_watchlists(request):
    user = request.user
    watchlists = Watchlist.objects.filter(user=user)
    serializer = WatchlistSerializer(watchlists, many=True)
    return Response(format_response(status=True, return_data=serializer.data))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_watchlist(request):
    serializer = GetWatchlistSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        watchlist_id = serializer.validated_data['watchlist_id']
        try:
            watchlist = Watchlist.objects.get(user=user, id=watchlist_id)
            resp = WatchlistSerializer(watchlist)
            return Response(format_response(status=True, return_data={"watchlist": resp.data}))
        except Watchlist.DoesNotExist:
            return Response(format_response(status=False, error_descr="Watchlist not found"), status=404)
    return Response(format_response(status=False, error_descr="Invalid ID"))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_watchlist(request):
    serializer = CreateWatchlistSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        watchlist_name = serializer.validated_data['watchlist_name']
        if Watchlist.objects.filter(user=user, name=watchlist_name).exists():
            return Response(format_response(status=False, error_descr="Watchlist already exists"))
        watchlist = Watchlist.objects.create(user=user, name=watchlist_name)
        watchlist_serializer = WatchlistSerializer(watchlist)
        return Response(format_response(status=True, return_data=watchlist_serializer.data))
    return Response(format_response(status=False, error_descr=serializer.errors), status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rename_watchlist(request):
    serializer = RenameWatchlistSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        watchlist_id = serializer.validated_data['watchlist_id']
        new_name = serializer.validated_data['watchlist_name']
        if Watchlist.objects.filter(user=user, name=new_name).exists():
            return Response(format_response(status=False, error_descr="A watchlist with this name already exists"), status=400)
        try:
            watchlist = Watchlist.objects.get(user=user, id=watchlist_id)
            watchlist.name = new_name
            watchlist.save()
            watchlist_serializer = WatchlistSerializer(watchlist)
            return Response(format_response(status=True, return_data=watchlist_serializer.data))
        except Watchlist.DoesNotExist:
            return Response(format_response(status=False, error_descr="Watchlist not found"), status=404)
    return Response(format_response(status=False, error_descr=serializer.errors), status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_watchlist(request):
    serializer = DeleteWatchlistSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        watchlist_id = serializer.validated_data['watchlist_id']
        try:
            watchlist = Watchlist.objects.get(user=user, id=watchlist_id)
            watchlist.delete()
            return Response(format_response(status=True))
        except Watchlist.DoesNotExist:
            return Response(format_response(status=False, error_descr="Watchlist not found"), status=404)
    return Response(format_response(status=False, error_descr=serializer.errors), status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_watchlist_position(request):
    serializer = CreateWatchlistPositionSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        watchlist_id = serializer.validated_data['watchlist_id']
        ticker = serializer.validated_data['ticker']

        try:
            watchlist = Watchlist.objects.get(user=user, id=watchlist_id)
        except Watchlist.DoesNotExist:
            return Response(format_response(status=False, error_descr="Watchlist not found"), status=404)

        if WatchlistPosition.objects.filter(ticker=ticker, watchlist=watchlist).exists():
            return Response(format_response(status=False, error_descr="A watchlist with this ticker already exists"))

        watchlist_position = WatchlistPosition.objects.create(ticker=ticker, watchlist=watchlist)
        watchlist_position_serializer = WatchlistPositionSerializer(watchlist_position)

        return Response(format_response(status=True, return_data=watchlist_position_serializer.data))

    return Response(format_response(status=False, error_descr=serializer.errors), status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_watchlist_position(request):
    serializer = DeleteWatchlistPositionSerializer(data=request.data)
    if serializer.is_valid():
        watchlist_id = serializer.validated_data['watchlist_id']
        watchlist_position_id = serializer.validated_data['watchlist_position_id']

        try:
            watchlist = Watchlist.objects.get(user=request.user, id=watchlist_id)
        except Watchlist.DoesNotExist:
            return Response(format_response(status=False, error_descr="Watchlist not found"), status=404)

        try:
            watchlist_position = WatchlistPosition.objects.get(id=watchlist_position_id, watchlist=watchlist)
            watchlist_position.delete()
            return Response(format_response(status=True))
        except WatchlistPosition.DoesNotExist:
            return Response(format_response(status=False, error_descr="WatchlistPosition not found"), status=404)

    return Response(format_response(status=False, error_descr=serializer.errors), status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(format_response(status=True, return_data=serializer.data), status=201)
    return Response(format_response(status=False, error_descr=serializer.errors), status=400)

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
            return Response(format_response(status=False, error_descr=e.args), status=401)


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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_calendar(request):
    try:
        events = CalendarEvent.objects.all().order_by('time')  # Ordered by time
        serializer = CalendarEventSerializer(events, many=True)
        return Response(format_response(status=True, return_data=serializer.data))
    except Exception as e:
        return Response(format_response(status=False, error_descr=e.args), status=401)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def reload_calendar(request):
    xtb_service = XTBAPIService()
    if not xtb_service:
        return Response(format_response(status=False, error_descr="Server is not connected with XTB"), 401)

    response = xtb_service.client.getCalendar()
    if response.get('status'):
        calendar_data = response.get('returnData')
        refresh_calendar_data(calendar_data)
        return Response(format_response(status=True))
    else:
        return Response(format_response(status=False, error_descr=response.get('errorDescr')))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_news(request):
    xtb_service = XTBAPIService()
    if not xtb_service:
        return Response(format_response(status=False, error_descr="Server is not connected with XTB"), 401)

    start_time = datetime.now() - timedelta(days=3)
    start_timestamp = int(start_time.timestamp() * 1000)
    return Response(xtb_service.client.getNews(start=start_timestamp, end=0))

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_symbols(request):
    xtb_service = XTBAPIService()
    if not xtb_service:
        return Response(format_response(status=False, error_descr="Server is not connected with XTB"), 401)

    return Response(xtb_service.client.getAllSymbols())

@api_view(['POST'])
@permission_classes([IsAdminUser])
def reload_symbols(request):
    xtb_service = XTBAPIService()
    if not xtb_service:
        return Response(format_response(status=False, error_descr="Server is not connected with XTB"), 401)

    response = xtb_service.client.getAllSymbols()
    if response.get('status'):
        calendar_data = response.get('returnData')
        refresh_symbol_data(calendar_data)
        return Response(format_response(status=True))
    else:
        return Response(format_response(status=False, error_descr=response.get('errorDescr')))
