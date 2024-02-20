from configparser import ConfigParser
from DoorSensor import subscribe_to_door_sensor, handle_door_sensor_events
import websockets
import os
import json

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
    print("Authenticating...")
    await ws.recv()
    await ws.send(json.dumps({"type": "auth", "access_token": config_data['HA_TOKEN']}))
    response = await ws.recv()
    if json.loads(response)["type"] != "auth_ok":
        print("Authentication failed.")
        return False
    print("Authentication successful.")
    return True

async def connect_to_ha_server(config_data):
    print("Connecting...")
    async with websockets.connect(config_data['HA_WS_URL']) as ws:
            print("Connection successful")
            authenticated = await authenticate(ws, config_data)    
            if authenticated:
                await subscribe_to_door_sensor(ws)
                await handle_door_sensor_events(ws, config_data, armed_mode)
