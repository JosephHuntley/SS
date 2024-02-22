import json
import logging
import requests
import websockets
from door_sensor import subscribe_to_door_sensor, handle_door_sensor_events
from logging_config import configure_logging, load_config
from alarm_control import subscribe_to_armed_mode, handle_armed_mode_change, get_armed_mode
import sleep

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
    try:
        # Set initial state
        armed_mode = await get_armed_mode(config_data)
    except Exception as e:
        logging.error("Could not get armed mode: ", e)
        return
    logging.info("Connecting...")
    async with websockets.connect(config_data['HA_WS_URL']) as ws:
        try:
            logging.info("Connection successful")
            authenticated = await authenticate(ws, config_data)
            if authenticated:
                await subscribe_to_armed_mode(ws)
                logging.info(f'Device is {armed_mode}')

                await subscribe_to_door_sensor(ws)
                await subscribe_to_ha_reboot_event(ws)

                while True:
                    res = await ws.recv()
                    id = json.loads(res)["id"]

                    if id == 1:
                        armed_mode = await handle_armed_mode_change(res)
                    elif id == 2:
                        await handle_door_sensor_events(res, config_data, armed_mode)
                    elif id == 3:
                        await handle_reboot_event(ws)
                        sleep(60)
                        break
        except websockets.exceptions.ConnectionClosed as e:
            logging.warning(f"WebSocket connection closed: {e}")
        except Exception as e:
            logging.error(f"Error in WebSocket connection: {e}")
        finally:
            await ws.close()

async def subscribe_to_ha_reboot_event(ws):
    logging.info("Subscribing to reboot event...")

    subscribe_payload = json.dumps({
        "id": 3,
        "type": "subscribe_events",
        "event_type": "SS_reboot"
    })

    await ws.send(subscribe_payload)
    response = await ws.recv()

    logging.info("Subscribing successful.")

async def handle_reboot_event(ws):
    logging.info("Home Assistant Server is rebooting...")
    reboot_home_assistant(ws)

def reboot_home_assistant(ws):
    config_data = load_config()

    headers = {
        'Authorization': f'Bearer {config_data["HA_TOKEN"]}',
        'Content-Type': 'application/json',
    }

    api_url = f'{config_data["HA_URL"]}/services/homeassistant/restart'

    try:
        requests.post(api_url, headers=headers)
        # response.raise_for_status()  # Raise an exception for HTTP errors
        logging.info("Home Assistant restart initiated successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error initiating Home Assistant restart: {e}")
