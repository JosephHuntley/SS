import json
from Notifications import send_notification
import logging
from logging_config import configure_logging, load_config  
from alarm_control import ArmedMode

configure_logging()

# Door sensor entity ID
SENSORS = ["binary_sensor.window_opening", "binary_sensor.front_door_sensor_opening",  "binary_sensor.sliding_door_opening"]

async def subscribe_to_door_sensor(ws):
    logging.info("Subscribing to door sensors...")
    subscribe_command = {
        "id": 2,
        "type": "subscribe_trigger",
        "trigger": {
            "platform": "state",
            "entity_id": SENSORS,
            "from": "off",
            "to": "on"
        }
    }
    await ws.send(json.dumps(subscribe_command))
    response = await ws.recv()
    logging.info("Subscribing successful.")

async def handle_door_sensor_events(res, config_data, armed_mode):
    # Implement logic here
    if armed_mode.strip() in (ArmedMode.ARMED_AWAY.value, ArmedMode.ARMED_HOME.value):
        sensor = json.loads(res)["event"]["variables"]["trigger"]["to_state"]["attributes"]["friendly_name"]
        send_notification(config_data, sensor + " has been opened")

    