import os
from datetime import datetime, timedelta
import threading
from .xAPIConnector import *

class XTBAPIService:
    _instance = None
    _lock = threading.Lock()  # For thread-safe singleton initialization

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:  # Ensure only one thread initializes the instance
                if not cls._instance:  # Double-checked locking
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

    def connect_to_xtb(self):
        if not self.username or not self.password:
            logger.error("Username or password is not set.")
            return False
        try:
            self.client = APIClient()
            login_response = self.client.execute(loginCommand(userId=self.username, password=self.password))
            if not login_response['status']:
                logger.error(f"Login failed. Error code: {login_response['errorCode']}")
                return False
            self.client.ping()
            self.ssid = login_response['streamSessionId']
            self.sclient = APIStreamClient(
                ssId=self.ssid,
                tickFun=procTickExample,
                tradeFun=procTradeExample,
                profitFun=procProfitExample,
                tradeStatusFun=procTradeStatusExample,
                newsFun=procNewsExample,
                balanceFun=procBalanceExample,
                keepFun=procKeepAliveExample
            )
            self.sclient.subscribeKeepAlive()
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False

    def is_connected(self):
        if not self.client:
            logger.error("Client is not initialized.")
            return False
        try:
            response = self.client.commandExecute('ping')
            return response.get('status', False)
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            return False

    def get_last_chart(self, symbol, period):
        if not self.client:
            logger.error("Client is not initialized.")
            return None
        start_time = datetime.now() - timedelta(days=365)
        start_timestamp = int(start_time.timestamp() * 1000)  # Convert to milliseconds
        try:
            response = self.client.execute({
                "command": "getChartLastRequest",
                "arguments": {
                    "info": {
                        "start": start_timestamp,
                        "period": period,
                        "symbol": symbol,
                    }
                }
            })
            if response and response.get('status'):
                rate_infos = response['returnData']['rateInfos']
                num_data_points = len(rate_infos)
                logger.info(f"Number of data points: {num_data_points}")
            return response
        except Exception as e:
            logger.error(f"getChart command failed: {e}")
            return None

    def disconnect(self):
        try:
            if self.sclient:
                self.sclient.disconnect()
            if self.client:
                self.client.disconnect()
        except Exception as e:
            logger.error(f"Disconnection failed: {e}")
