import asyncio
import json
import websockets
import requests
import os
from configparser import ConfigParser
from Notifications import send_notification
from time import sleep

# Home Assistant API information
HA_WS_URL = "ws://homeassistant.local:8123/api/websocket"
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIxMjcyNDM2NDRiZGU0NWNiYTYwYjYwMmI0ZWNhYzA3YiIsImlhdCI6MTcwODM2NTMzNSwiZXhwIjoyMDIzNzI1MzM1fQ.F_nj_z1qrBTtgdcdHIrKgGVurJi-nMbSWVEWCe1gP5U"

# Door sensor entity ID
DOOR_SENSOR = "binary_sensor.front_door_sensor_opening"

# Set initial state
armed_mode = "armed"
    
def load_config(file_path=None):
    if file_path is None:
        # If file_path is not provided, use the directory of the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'config.ini')
    config = ConfigParser()
    config.read(file_path)
    return config["credentials"]

async def authenticate(ws, config_data):
    await ws.recv()
    await ws.send(json.dumps({"type": "auth", "access_token": HA_TOKEN}))
    response = await ws.recv()
    print(f"Authentication response: {response}")
    if json.loads(response)["type"] != "auth_ok":
        print("Authentication failed.")
        return False
    print("Authentication successful.")
    return True

async def subscribe_to_door_sensor(ws):
    subscribe_command = {
        "id": 1,
        "type": "subscribe_trigger",
        "trigger": {
            "platform": "state",
            "entity_id": DOOR_SENSOR,
            "from": "off",
            "to": "on"
        }
    }
    await ws.send(json.dumps(subscribe_command))
    response = await ws.recv()
    print(f"Subscription response: {response}")

async def handle_door_sensor_events(ws, config_data):
    # Implement logic here
    while True:
        response = await ws.recv()
        if json.loads(response)["event"]["variables"]["trigger"]["entity_id"] == DOOR_SENSOR and armed_mode == "armed":
            send_notification(config_data, DOOR_SENSOR + " has been opened")

async def connect_to_ha_server(config_data):
    async with websockets.connect(HA_WS_URL) as ws:
            authenticated = await authenticate(ws, config_data)
            if authenticated:
                await subscribe_to_door_sensor(ws)
                await handle_door_sensor_events(ws, config_data)

async def main():
    config_data = load_config()

    i = 0
    while(i < 10):
        try:
            await connect_to_ha_server(config_data)
            i = 10
        except as e:
            send_notification(config_data, "Could not connect to the Home Assistant server")
            print("Could not connect to the Home Assistant server", e)
            i += 1 
            sleep(60)
        

if __name__ == "__main__":
    asyncio.run(main())
