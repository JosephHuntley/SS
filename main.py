import asyncio
from Notifications import send_notification
from Server import connect_to_ha_server
from time import sleep
import logging
from logging_config import configure_logging, load_config  

configure_logging()

async def main():
    config_data = load_config()
    max_retries = 10
    i = 0
    while(i < max_retries):
        try:
            logging.info(f"Retry: {i}")
            await connect_to_ha_server(config_data)
            i = 0
            logging.info("Waiting to reconnect..")
            sleep(60)
        except Exception as e:
            if(i >= 5):
                send_notification(config_data, "Could not connect to the Home Assistant server")
            logging.error(f"Could not connect to the Home Assistant server: {e}. Retry: {i}")
            i += 1 
            sleep(60)
    logging.info("Shutting Down....")
if __name__ == "__main__":
    asyncio.run(main())
