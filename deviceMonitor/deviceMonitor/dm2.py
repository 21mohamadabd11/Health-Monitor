import cherrypy
import requests
import json
import time
import threading
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
        threading.Thread(target=self.run_cherrypy, daemon=True).start()
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
        
    def run_cherrypy(self):
        conf = {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tools.sessions.on': True
            }
        }

        settings = json.load(open('settings.json'))
        local_ip = "dm"
        port = 9099

        settings["serviceInfo"]["url"] = f"http://{local_ip}:{port}"

        # Cherrypy configurations
        cherrypy.config.update({'server.socket_host': local_ip, 'server.socket_port': port})
        cherrypy.tree.mount(self, '/', conf)
        cherrypy.engine.start()

        print("\n____________________________________________________________\n")
        print(f"  Device Monitor running at http://{local_ip}:{port}")
        print("____________________________________________________________\n")
        print("Press Ctrl+C to stop the server. \n")

        cherrypy.engine.block()  # Questo blocca il server finché non viene fermato


if __name__ == "__main__":
    tout=120
    dm=monitor(tout)
    dm.run()