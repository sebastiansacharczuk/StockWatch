from django.apps import AppConfig
import logging

from django.db.models.signals import post_migrate
from django.dispatch import receiver

logger = logging.getLogger(__name__)

@receiver(post_migrate)
def start_connection(**kwargs):
    """Attempt to connect to the XTB API."""
    from .xtbapi.XTBAPIService import XTBAPIService  # Adjust import path as needed
    max_retries = 3  # Number of connection attempts
    retry_count = 0
    xtb_service = XTBAPIService()

    while retry_count < max_retries:
        try:
            if xtb_service.connect():
                logger.warning("Successfully connected to XTB API.")
                return True  # Exit the loop and indicate success
            else:
                retry_count += 1
                logger.warning(f"Failed to connect to XTB API. Retry {retry_count} of {max_retries}.")
        except Exception as e:
            retry_count += 1
            logger.error(f"Error during XTB API connection attempt {retry_count}: {e}")

    logger.critical("All attempts to connect to XTB API failed.")
    return False  # Indicate failure


@receiver(post_migrate)
def reload_economic_calendar(**kwargs):
    """Fetch and save economic calendar data after migrations."""
    from .models import save_calendar_data
    from .xtbapi.XTBAPIService import XTBAPIService

    xtb_service = XTBAPIService()
    if xtb_service.connect():
        response = xtb_service.get_calendar()
        if response.get('status'):
            calendar_data = response.get('returnData')
            save_calendar_data(calendar_data)
            logger.info("Economic calendar data saved successfully.")
        else:
            logger.error(f"Failed to fetch calendar data. Error code: {response.get('errorCode')}")
    else:
        logger.error("Failed to connect to XTB API for calendar data.")


class BaseConfig(AppConfig):
    """Base application configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'

    def ready(self):
        """Start XTB connection in a separate thread."""