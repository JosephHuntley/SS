from enum import Enum
import requests
import logging
from logging_config import configure_logging
import json

configure_logging()

class ArmedMode(Enum):
    ARMED_HOME = "ARMED HOME"
    DISARMED = "DISARMED"
    ARMED_AWAY = "ARMED AWAY"

async def subscribe_to_armed_mode(ws):
    logging.info("Subscribing to armed mode...")
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
    logging.info("Subscribing successful.")

async def handle_armed_mode_change(res):
    armed_mode = json.loads(res)['event']['variables']['trigger']['to_state']['state']
    logging.info(f"Armed Mode: {armed_mode}")
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
        logging.error(f"Error fetching armed_mode status: {e}")
        return None