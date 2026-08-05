import requests
import json
import time
class monitor:
    exposed = True
    def __init__(self,maxTimeOut):
        self.settings = json.load(open('settings.json'))
        self.catalogURL=self.settings['catalogURL']
        self.maxTimeOut=maxTimeOut
        self.serviceInfo=self.settings['serviceInfo']
        self.loop=True
        self.loopTime=15
 
    def removeInactive(self):
        self.actualTime = time.time()
        for device in self.devices().values():  # <-- use .values()
            last_update = device.get('last_update', 0)
            if self.actualTime - last_update > self.maxTimeOut:
                device_id = device.get('id')
                requests.delete(f'{self.catalogURL}/devices/{device_id}')
                print(f'Device {device_id} has been removed')
    def devices(self):
        r = requests.get(f'{self.catalogURL}/devices')
        r.raise_for_status()  # lanza error si el código no es 2xx
        return r.json()
    

    def run(self):
        self.registerService()
        while self.loop:
            self.removeInactive()
            time.sleep(self.loopTime)
            self.updateService()
    
    def registerService(self):
        self.serviceInfo['last_update']=time.time()
        response=requests.post(f'{self.catalogURL}/services',data=json.dumps(self.serviceInfo))
        if response.status_code == 201:
            print('Service registered')

    def updateService(self):
        self.serviceInfo['last_update']=time.time()
        print('updating service')
        requests.put(f'{self.catalogURL}/services',data=json.dumps(self.serviceInfo))


if __name__ == "__main__":
    tout=120
    dm=monitor(tout)
    dm.run()