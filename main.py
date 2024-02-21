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
            await connect_to_ha_server(config_data)
            i = max_retries #Stops if the server exits successfully
        except Exception as e:
            send_notification(config_data, "Could not connect to the Home Assistant server")
            logging.error("Could not connect to the Home Assistant server: %s", e)
            i += 1 
            sleep(60)
        

if __name__ == "__main__":
    configure_logging()
    asyncio.run(main())
