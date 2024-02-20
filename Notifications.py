import requests
from logging_config import configure_logging, load_config  
import logging

configure_logging()

def send_notification(config_data, message="test", title="", priority=0):
    if(config_data['server'] == 'dev'):
        print("\n" + "*" * 10)
        print(message)
        print("*" * 10 + "\n")
    else:
        token = config_data['api_token']
        user = config_data['user_key']
        url = "https://api.pushover.net/1/messages.json"

        payload = {
            'token': token,
            'user': user,
            'message': message,
            'title':title,
            priority:priority
        }
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        res = requests.request("POST", url, headers=headers, data=payload)
        return res

