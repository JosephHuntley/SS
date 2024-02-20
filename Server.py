from configparser import ConfigParser
from DoorSensor import subscribe_to_door_sensor, handle_door_sensor_events
import websockets
import os
import json
import asyncio


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
    # Set initial state
    armed_mode = "armed"
    print("Connecting...")
    async with websockets.connect(config_data['HA_WS_URL']) as ws:
            print("Connection successful")
            authenticated = await authenticate(ws, config_data)    
            if authenticated:
                await subscribe_to_armed_mode(ws)
                await subscribe_to_door_sensor(ws)
                while(True):
                    res = await ws.recv()
                    if(json.loads(res)["id"] == 1):
                        armed_mode = await handle_armed_mode_change(res)
                    else:
                        await handle_door_sensor_events(res,config_data, armed_mode)

async def subscribe_to_armed_mode(ws):
    print("Subscribing to armed mode...")
    subscribe_command = {
        "id": 1,
        "type": "subscribe_trigger",
        "trigger": {
            "platform": "state",
            "entity_id": "input_select.armed_mode",
        }
    }
    await ws.send(json.dumps(subscribe_command))
    response = await ws.recv()
    print("Subscribing successful.")
    print("Armed successfully")

async def handle_armed_mode_change(res):
    armed_mode = json.loads(res)['event']['variables']['trigger']['to_state']['state']
    print(f"Armed Mode: {armed_mode}")
    return armed_mode