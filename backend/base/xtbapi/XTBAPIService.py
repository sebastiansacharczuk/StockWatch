import os
from .xAPIConnector import *

class XTBAPIService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(XTBAPIService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self.username = os.getenv('XAPI_USER_ID')
        self.password = os.getenv('XAPI_USER_PASSWORD')
        self.client = None
        self.sclient = None
        self.ssid = None
        self._initialized = True  # Avoid re-initialization


    def connect(self):
        try:
            self.client = APIClient()
            login_response = self.client.execute(loginCommand(userId=self.username, password=self.password))
            if not login_response['status']:
                print('Login failed. Error code: {0}'.format(login_response['errorCode']))
                return False
            self.ssid = login_response['streamSessionId']
            self.sclient = APIStreamClient(ssId=self.ssid, tickFun=procTickExample, tradeFun=procTradeExample, profitFun=procProfitExample, tradeStatusFun=procTradeStatusExample)
            self.sclient.execute({"command": "ping", "streamSessionId": self.ssid})
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def is_connected(self):
        try:
            response = self.client.commandExecute('ping')
            return response['status']
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            return False

    def ping(self):
        try:
            self.client.commandExecute('ping')
        except Exception as e:
            logger.error(f"Ping command failed: {e}")

    def get_calendar(self):
        try:
            response = self.client.execute({"command": "getCalendar"})
            return response
        except Exception as e:
            logger.error(f"getCalendar command failed: {e}")
            response = {'status': False}
            return response

    def get_keep_alive(self):
        try:
            self.sclient.execute({"command": "keepAlive", "streamSessionId": self.ssid})
        except Exception as e:
            logger.error(f"KeepAlive command failed: {e}")

    def stop_keep_alive(self):
        try:
            self.sclient.execute({"command": "stopKeepAlive"})
        except Exception as e:
            logger.error(f"StopKeepAlive command failed: {e}")

    def disconnect(self):
        try:
            self.sclient.disconnect()
            self.client.disconnect()
        except Exception as e:
            logger.error(f"Disconnection failed: {e}")
