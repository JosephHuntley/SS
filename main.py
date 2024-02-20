import asyncio
from Server import load_config, connect_to_ha_server
from time import sleep

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
            print("Could not connect to the Home Assistant server", e)
            i += 1 
            sleep(60)
        

if __name__ == "__main__":
    asyncio.run(main())
