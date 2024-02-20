import json
from Notifications import send_notification

# Door sensor entity ID
DOOR_SENSOR = "binary_sensor.front_door_sensor_opening"

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

async def handle_door_sensor_events(ws, config_data, armed_mode):
    # Implement logic here
    while True:
        res = await ws.recv()
        # print(res)
        if json.loads(res)["event"]["variables"]["trigger"]["entity_id"] == DOOR_SENSOR and armed_mode == "armed":
            sensor = json.loads(res)["event"]["variables"]["trigger"]["to_state"]["attributes"]["friendly_name"]
            send_notification(config_data, sensor + " has been opened")
