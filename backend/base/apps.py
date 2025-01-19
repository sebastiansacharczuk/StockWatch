import sys
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


def startup_actions(**kwargs):
    from .xtbapi.XTBAPIService import XTBAPIService
    try:
        xtb_service = XTBAPIService()
        if xtb_service.connect_to_xtb():
            xtb_service.sclient.subscribeNews()
        else:
            logger.warning("Server is shutting down...")
            sys.exit(1)
    except Exception as e:
        logger.error(e)
        logger.warning("Server is shutting down...")
        sys.exit(1)


class BaseConfig(AppConfig):
    """Base application configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'

    def ready(self):
        """Initialize the application."""
        startup_actions()