import requests
import random
import json
from datetime import datetime


# Event generator
def generate_random_event():
    event_types = ["ERROR", "INFO", "WARNING", "DEBUG"]
    source_apps = ["App1", "App2", "App3", "App4"]

    event = {
        "event_type": random.choice(event_types),
        "timestamp": datetime.now().isoformat(),
        "source_app_id": random.choice(source_apps),
        "data_payload": {
            "traceId": random.choice(["x-random-correlation-id-1","x-random-correlation-id-2","x-random-correlation-id-3"]),
            "log": random.choice(["login", "logout", "update_profile", "delete_account"])
        }
    }
    return event


# Send event to the API
def send_event_to_api(event, api_url="http://127.0.0.1:5000/api/events"):
    response = requests.post(api_url, json=event)
    return response.status_code, response.json()


# Generate and send events
if __name__ == "__main__":
    for _ in range(3):  # Simulate 5 events
        event = generate_random_event()
        print("Generated Event:", json.dumps(event, indent=2))
        status_code, response = send_event_to_api(event)
        print(f"API Response [{status_code}]: {response}")
