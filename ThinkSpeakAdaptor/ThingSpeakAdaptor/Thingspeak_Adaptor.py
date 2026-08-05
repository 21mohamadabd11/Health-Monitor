import requests
import json
from MyMQTT import *
import cherrypy
import random
import time
import uuid
from datetime import  datetime, timedelta, timezone
from pprint import pprint
import matplotlib.pyplot as plt
from io import BytesIO
import socket
import threading

class Thingspeak_Adaptor:
    exposed = True
    def __init__(self,settings):
        self.settings = settings
        self.catalogURL = self.settings['catalogURL']
        self.serviceInfo = self.settings['serviceInfo']
        self.serviceID = self.serviceInfo['id']
        self.baseURL = self.settings["ThingspeakURL"]
        self.base_ip = self.serviceInfo["url"]
        self.UserAPIKey = self.settings["UserAPIKey"]
        # Caricamento dei dati paziente dal catalog
        self.patients_dict = requests.get(f"{self.catalogURL}/patients").json()
        self.devices_dict = requests.get(f"{self.catalogURL}/devices").json()

        # Creazione della struttura dati per l'upload
        self.data_struct = {}
        for patientID in self.patients_dict:
            for channel in self.patients_dict[patientID]["TS_params"]:
                if patientID not in self.data_struct:
                    self.data_struct[patientID] = {}
                self.data_struct[patientID][channel] = {"write_api_key": self.patients_dict[patientID]["TS_params"][channel]["ChannelWriteAPIkey"],
                                                        "updates": []
                                                        }

        # MQTT settings
        self.broker=self.settings["brokerIP"]
        self.port=self.settings["brokerPort"]
        self.topic=self.settings["mqttTopic"]+"/#"
        self.clientID = "testIDfra" #str(uuid.uuid1())
        self.mqttClient = MyMQTT(clientID=self.clientID, broker=self.broker, port=self.port, notifier=self) #uuid is to generate a random string for the client id
        self.mqttClient.start()
        self.mqttClient.mySubscribe(self.topic)
        self.actualTime = time.time()
    
    def GET(self, *uri, **params):
        if uri[0] in self.patients_dict:
            patientID = uri[0]
            patientParams = self.patients_dict[patientID]["TS_params"]["health"]
            field = params["field"]
            field_number = patientParams["fields"][field][-1]

            if "start" in params and "end" in params:
                start = params["start"]
                end = params["end"]
            else:
                start = None
                end = None
            
            data_json = self.getFromThingspeak(field_number, start, end, TS_params=patientParams)
        return json.dumps(data_json)
    
    def notify(self,topic,payload):
        message_decoded=json.loads(payload)
        # message_value=message_decoded["e"][0]['v']
        # decide_measurement=message_decoded["e"][0]["n"]
        
        # field_number = self.topic2field.get(decide_measurement, None)
        
        # if field_number is None:
        #     print("Error: Wrong topic")
        # else:
        print(f'\nMessage received with the topic "{topic}" ')

        deviceID = topic.split("/")[-2]
        if deviceID not in self.devices_dict:
            self.catalog = requests.get(f"{self.catalogURL}/all").json()
            self.devices_dict = self.catalog["devices"]
            self.patients_dict = self.catalog["patients"]
            if deviceID not in self.devices_dict:
                print(f"Error: Device {deviceID} not found in the catalog")
                return
        devicetype = self.devices_dict[deviceID]["type"]

        found = False
        for patientID in self.patients_dict:
            if deviceID in self.patients_dict[patientID]["devices"]:
                found = True
                break
        
        if not found:
            self.patients_dict = requests.get(f"{self.catalogURL}/patients").json()
            print(f"Error: Device {deviceID} not associated with any patient")
            return
        
        # if patientID not in self.patients_dict:
        #     # Nuova richiesta per caricare il catalog aggiornato
        #     self.patients_dict = requests.get(f"{self.catalogURL}/patients").json()
        #     if patientID not in self.patients_dict:
        #         print(f"Error: Patient {patientID} not found in the catalog")
        #         return
        #     self.data_struct[patientID][devicetype] = {"write_api_key": self.patients_dict[patientID]["TS_params"][devicetype]["ChannelWriteAPIkey"],
        #                                     "updates": []
        #                                     }        
            
        if self.patients_dict[patientID]["TS_params"][devicetype]["ChannelID"] == "":
            print("\nCreating new channel...")
            name = self.patients_dict[patientID]["name"]
            surname = self.patients_dict[patientID]["surname"]
            channel_data = {
                                "api_key": self.UserAPIKey,
                                "name": f"Patient {patientID}: {name} {surname}, {devicetype} parameters"
                            }
            for i,field in enumerate(self.devices_dict[deviceID]["available"]):
                channel_data[f"field{i+1}"] = field
                self.patients_dict[patientID]["TS_params"][devicetype]["fields"][field] = f"field{i+1}"

            url = f"{self.baseURL}/channels.json"
            response = requests.post(url, json=channel_data)
            channel_info = response.json()
            print("DEBUG channel_info:", channel_info)
            self.patients_dict[patientID]["TS_params"][devicetype]["ChannelID"] = str(channel_info["id"])
            self.patients_dict[patientID]["TS_params"][devicetype]["ChannelWriteAPIkey"] = str(channel_info["api_keys"][0]["api_key"])
            self.patients_dict[patientID]["TS_params"][devicetype]["ChannelReadAPIKey"] = str(channel_info["api_keys"][1]["api_key"])
            for channel in self.patients_dict[patientID]["TS_params"]:
                if patientID not in self.data_struct:
                    self.data_struct[patientID] = {}
                self.data_struct[patientID][channel] = {"write_api_key": self.patients_dict[patientID]["TS_params"][channel]["ChannelWriteAPIkey"],
                                                        "updates": []
                                                        }
            self.data_struct[patientID][devicetype]["write_api_key"] = self.patients_dict[patientID]["TS_params"][devicetype]["ChannelWriteAPIkey"]
            print("\nChannel created")
            requests.post(f"{self.catalogURL}/patients/{patientID}/TS_params", data=json.dumps(self.patients_dict[patientID]["TS_params"]))

        msg = {"created_at": message_decoded["e"][0]["t"]}
        for element in message_decoded["e"]:
            field = self.patients_dict[patientID]["TS_params"][devicetype]["fields"][element["n"]]
            message_value = element["v"]
            msg[field] = message_value

        self.data_struct[patientID][devicetype]["updates"].append(msg)
        # print("\nData structure updated")    
        # pprint(self.data_struct)

    def uploadThingspeak(self):
        for patientID in self.data_struct:
            for channel in self.data_struct[patientID]:
                data = self.data_struct[patientID][channel]
                if self.data_struct[patientID][channel]["updates"]:
                    ChannelID = self.patients_dict[patientID]["TS_params"][channel]["ChannelID"]
                    url = f'{self.baseURL}/channels/{ChannelID}/bulk_update.json'
                    response = requests.post(url=url, json=data)
                    self.data_struct[patientID][channel]["updates"] = []
                    print('\n Uploading ThingSpeak ...')
                    # print(response.text)
                    # print(response.status_code)

    def getFromThingspeak(self, field_number, start_time = None, end_time = None, TS_params=None):
        ChannelID = TS_params["ChannelID"]
        ChannelReadAPIKey = TS_params["ChannelReadAPIKey"]
        if start_time is None or end_time is None:
            url = f"{self.baseURL}/channels/{ChannelID}/fields/{field_number}.json?api_key={ChannelReadAPIKey}"
        else:
            url = f"{self.baseURL}/channels/{ChannelID}/fields/{field_number}.json?api_key={ChannelReadAPIKey}&start={start_time}&end={end_time}"
        r=requests.get(url)
        return r.json()

    def registerService(self):
        self.serviceInfo['last_update']=self.actualTime
        requests.post(f'{self.catalogURL}/services',data=json.dumps(self.serviceInfo))
    
    def updateService(self):
        self.actualTime = time.time()
        self.serviceInfo['last_update']=self.actualTime
        requests.put(f'{self.catalogURL}/services',data=json.dumps(self.serviceInfo))

    def deleteService(self):
        requests.delete(f'{self.catalogURL}/services/{self.serviceID}')
        
    def stop(self):
        self.mqttClient.stop()

def run_cherrypy():
    global ts_adaptor
    settings = json.load(open('settings.json'))
    ts_adaptor = Thingspeak_Adaptor(settings)
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }

    
    local_ip=ts_adaptor.base_ip[-8:-5]
    port=int(ts_adaptor.base_ip[-4:])

    settings["serviceInfo"]["url"] = f"http://{local_ip}:{port}"
    
    ts_adaptor.registerService()

    # Cherrypy configurations
    cherrypy.config.update({'server.socket_host': local_ip, 'server.socket_port': port})
    cherrypy.tree.mount(ts_adaptor, '/', conf)
    cherrypy.engine.start()

    print("\n____________________________________________________________\n")
    print(f"  Thingspeak adaptor running at http://{local_ip}:{port}")
    print("____________________________________________________________\n")
    print("Press Ctrl+C to stop the server. \n")

    cherrypy.engine.block()  # Questo blocca il server finché non viene fermato

if __name__ == "__main__":
    time.sleep(2)
    try:
        # Avvia il server CherryPy in un thread separato
        cherrypy_thread = threading.Thread(target=run_cherrypy)
        cherrypy_thread.daemon = True
        cherrypy_thread.start()

        # Ciclo principale del programma
        counter_ts = 0
        counter_catalog = 0
        '''
        while 'ts_adaptor' not in globals():
            time.sleep(1)
            print('EXITED THE WHILE LOOP')
        '''

        while True:
            time.sleep(1)
            counter_ts += 1
            counter_catalog += 1
            if counter_catalog == 40:
                # Aggiorna il servizio ogni 40 secondi
                ts_adaptor.updateService()
                counter_catalog = 0
            if counter_ts == 15:
                # Carica i dati su ThingSpeak ogni 15 secondi
                ts_adaptor.uploadThingspeak()
                counter_ts = 0

    except KeyboardInterrupt:
        print("\nShutting down...")
        ts_adaptor.stop()
        ts_adaptor.deleteService()
        cherrypy.engine.exit()
        print("Thingspeak Adaptor Stopped")
