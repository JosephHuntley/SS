import asyncio
from Server import load_config, connect_to_ha_server
from time import sleep

async def main():
    config_data = load_config()
    i = 0
    while(i < 10):
        try:
            await connect_to_ha_server(config_data)
            i = 10
        except Exception as e:
            send_notification(config_data, "Could not connect to the Home Assistant server")
            print("Could not connect to the Home Assistant server", e)
            i += 1 
            sleep(60)
        

if __name__ == "__main__":
    asyncio.run(main())
