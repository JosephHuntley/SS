import json
import logging
import requests
import websockets
from DoorSensor import subscribe_to_door_sensor, handle_door_sensor_events
from logging_config import configure_logging, load_config
from alarm_control import subscribe_to_armed_mode, handle_armed_mode_change, get_armed_mode

# Load configuration
config_data = load_config()

# Configure logging based on the loaded configuration
configure_logging()

async def authenticate(ws, config_data):
    logging.info("Authenticating...")
    await ws.recv()
    await ws.send(json.dumps({"type": "auth", "access_token": config_data['HA_TOKEN']}))
    response = await ws.recv()
    if json.loads(response)["type"] != "auth_ok":
        logging.error("Authentication failed.")
        return False
    logging.info("Authentication successful.")
    return True

async def connect_to_ha_server(config_data):
    # Set initial state
    armed_mode = await get_armed_mode(config_data)
    logging.info("Connecting...")
    async with websockets.connect(config_data['HA_WS_URL']) as ws:
        logging.info("Connection successful")
        authenticated = await authenticate(ws, config_data)
        if authenticated:
            await subscribe_to_armed_mode(ws)
            logging.info(f'Device is {armed_mode}')
            await subscribe_to_door_sensor(ws)
            while True:
                res = await ws.recv()
                if json.loads(res)["id"] == 1:
                    armed_mode = await handle_armed_mode_change(res)
                else:
                    await handle_door_sensor_events(res, config_data, armed_mode)


