#%%
import time
import requests
import random
from datetime import  datetime, timedelta, timezone
from pprint import pprint
import cherrypy
from MyMQTT import *
# #%%
# # ThingSpeak API configuration
# THINGSPEAK_API_KEY = 'YOUR_API_KEY'
# THINGSPEAK_URL = 'https://api.thingspeak.com/channels/2876523/bulk_update.json'

# def send_data_to_thingspeak(payload):
#     print("Sending data to ThingSpeak:")
#     pprint(payload)
#     response = requests.post(THINGSPEAK_URL, json=payload)
#     return response

# def main():
#     try:
#         counter = 0
#         payload = {
#                 "write_api_key": "7DB76CHWGFDEAT04",
#                 "updates": [
#                 ]
#             }
#         while True:
#             # Replace with your actual data fetching logic
#             data1 = random.randint(60,140)
#             data2 = random.randint(80,100)
#             #%%
#             timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
#             payload["updates"].append({"created_at": timestamp, "field1": data1, "field2": data2})
#             #%%
#             if counter == 20: 
#                 response = send_data_to_thingspeak(payload)
#                 print(f"Response: {response.status_code}, {response.text}")
#                 payload["updates"] = []
#                 counter = 0
#             time.sleep(1)
#             counter += 1

#     except KeyboardInterrupt:
#         print("Terminated by user")

# if __name__ == "__main__":
#     main()

#%%

clientID = "testMQTT"
topic = "poli/IoTProject/sensors/90"
client = MyMQTT(clientID=clientID, broker="mqtt.eclipseprojects.io", port=1883, notifier=None)
client.start()
time.sleep(2)

try:
    while True:
        message= {'bn': 'SensorREST_MQTT_90',
          'e': [
           {'n': 'spo2', 'v': 97.74405186579072, 't': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), 'u': '%'}, 
           {'n': 'hr', 'v': 88.34631487915362, 't': datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), 'u': 'bpm'}]}
        client.myPublish(topic=topic,msg=message)
        time.sleep(5)

except KeyboardInterrupt:
    print("Terminated by user")