import requests

def send_notification(config_data, message="test", title="", priority=0):
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

