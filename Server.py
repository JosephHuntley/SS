from configparser import ConfigParser
from DoorSensor import subscribe_to_door_sensor, handle_door_sensor_events
import requests
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
    armed_mode = await get_armed_mode(config_data)
    print("Connecting...")
    async with websockets.connect(config_data['HA_WS_URL']) as ws:
            print("Connection successful")
            authenticated = await authenticate(ws, config_data)    
            if authenticated:
                await subscribe_to_armed_mode(ws)
                print(f'Device is {armed_mode}')
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

async def handle_armed_mode_change(res):
    armed_mode = json.loads(res)['event']['variables']['trigger']['to_state']['state']
    print(f"Armed Mode: {armed_mode}")
    return armed_mode

async def get_armed_mode(config_data):
    headers = {
        'Authorization': f'Bearer {config_data["HA_TOKEN"]}',
        'Content-Type': 'application/json',
        }

    # Specify the entity_id for the input_select.armed_mode
    entity_id = 'input_select.armed_mode'

    # Build the API endpoint for getting the state of the entity
    api_endpoint = f'{config_data["HA_URL"]}/states/{entity_id}'

    try:
        # Make the GET request to the Home Assistant API
        response = requests.get(api_endpoint, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the JSON response
        data = response.json()

        # Extract and return the state of the entity
        return data['state']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching armed_mode status: {e}")
        return None