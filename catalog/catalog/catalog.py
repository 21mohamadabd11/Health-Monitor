import cherrypy
import json
import time
import socket
import threading
import pprint
lock = threading.Lock()

def addService(catalog, serviceInfo):
    catalog["services"].append(serviceInfo)

def updateService(catalog, serviceid, serviceInfo):
    for i in range(len(catalog["services"])):
        service = catalog["services"][i]
        if service['id'] == serviceid:
            catalog["services"][i] = serviceInfo

def removeService(catalog, serviceid):
    for i in range(len(catalog["services"])):
        service = catalog["services"][i]
        if service['id'] == int(serviceid):
            catalog["services"].pop(i)
            break

def removeDevice(catalog, deviceid):
    catalog["devices"].pop(deviceid)

def removePatient(catalog, patientid):
    catalog["patients"].pop(patientid)
#function that checks if the device is active and associated to a patient
def check_dev_isactive(catalog, device_id):
    for patient_dict in catalog['patients'].values():
        #pprint.pprint(patient_dict)
        if 'devices' in patient_dict and device_id in patient_dict['devices']:
            return 1
    return 0


class CatalogREST:
    exposed = True

    def __init__(self, catalog_address):
        self.catalog_address = catalog_address
        self.ip=json.load(open(self.catalog_address,'r'))['catalog_url']
    
    def GET(self, *uri, **params):
        with lock:
            with open(self.catalog_address, "r") as f:
                catalog = json.load(f)
            if len(uri)==0: #An error will be raised in case there is no uri 
                raise cherrypy.HTTPError(status=400, message='UNABLE TO MANAGE THIS URL')
            
            elif len(uri)==1:
                if uri[0]=='all':
                    output = catalog
                elif uri[0]=='patients' or uri[0]=='devices' or uri[0]=='services':
                    output = catalog.get(uri[0],'not found')

            elif len(uri)>2:
                device_id = uri[1]
                output = check_dev_isactive(catalog, device_id)
            return json.dumps(output)
    
    def POST(self, *uri, **params):
        with lock:
            with open(self.catalog_address, "r") as f:
                catalog = json.load(f)
            body = cherrypy.request.body.read()
            json_body = json.loads(body.decode('utf-8'))
            print(uri)
            # Richiesta dal bot telegram 
            if len(uri) <= 2:
                if uri[0]=='patients':
                    if json_body['id'] not in catalog['patients'].keys():
                        last_update = time.time()
                        json_body['last_update'] = last_update
                        catalog['patients'][json_body['id']] = json_body
                        output = f"Device with id {json_body['id']} has been added"
                        print(output)
                    else:
                        raise cherrypy.HTTPError(status=400, message='PATIENT ALREADY REGISTERED')
                elif uri[0]=='devices':
                    if json_body['id'] not in catalog['devices'].keys():
                        last_update = time.time()
                        json_body['last_update'] = last_update
                        catalog['devices'][json_body['id']] = json_body
                        output = f"Device with id {json_body['id']} has been added"
                        print(output)
                    else:
                        raise cherrypy.HTTPError(status=400, message='DEVICE ALREADY REGISTERED')
                elif uri[0]=='services':
                    if not any(d['id'] == json_body['id'] for d in catalog["services"]):
                        last_update = time.time()
                        json_body['last_update'] = last_update
                        addService(catalog, json_body)
                        output = f"Service with id {json_body['id']} has been added"
                        print(output)
                    else:
                        raise cherrypy.HTTPError(status=400, message='SERVICE ALREADY REGISTERED')
                elif uri[0]=='doctors':
                    if json_body['id'] not in catalog["doctors"].keys():
                        last_update = time.time()
                        json_body['last_update'] = last_update
                        catalog['doctors'][json_body['id']] = json_body
                        output = f"Doctor with id {json_body['id']} has been added"
                        print(output)
                    else:
                        raise cherrypy.HTTPError(status=400, message='DOCTOR ALREADY REGISTERED')
            elif len(uri) > 2:
                patientid = uri[1]
                catalog['patients'][patientid]['last_update'] = time.time()
                catalog['patients'][patientid][uri[2]] = json_body
            with open(self.catalog_address, "w") as f:
                json.dump(catalog, f, indent=4)
            output = f"Service added"
            print(output)
            return output


    def PUT(self, *uri, **params):
        with lock:
            with open(self.catalog_address, "r") as f:
                catalog = json.load(f)
            body = cherrypy.request.body.read()
            json_body = json.loads(body.decode('utf-8'))
            if uri[0]=='patients':
                if str(json_body['id']) not in catalog['patients'].keys():
                    raise cherrypy.HTTPError(status=400, message='DEVICE NOT FOUND')
                else:
                    last_update = time.time()
                    json_body['last_update'] = last_update
                    catalog['patients'][uri[1]]=json_body
                with open(self.catalog_address, "w") as f:
                    json.dump(catalog, f, indent=4)
                return json_body
            elif uri[0]=='devices':
                if str(json_body.get('id')) not in catalog["devices"].keys():
                    raise cherrypy.HTTPError(status=400, message='DEVICE NOT FOUND')
                else:
                    last_update = time.time()
                    json_body['last_update'] = last_update
                    catalog['devices'][uri[1]]=json_body
                with open(self.catalog_address, "w") as f:
                    json.dump(catalog, f, indent=4)
                return json_body
        
            elif uri[0]=='services':
                if not any(d['id'] == json_body['id'] for d in catalog["services"]):
                    raise cherrypy.HTTPError(status=400, message='SERVICE NOT FOUND')
                else:
                    last_update = time.time()
                    json_body['last_update'] = last_update
                    updateService(catalog, json_body['id'], json_body)
            elif uri[0]=='doctors':
                if str(json_body['id']) not in catalog['doctors'].keys():
                    raise cherrypy.HTTPError(status=400, message='DOCTOR NOT FOUND')
                else:
                    last_update = time.time()
                    json_body['last_update'] = last_update
                    catalog['doctors'][uri[1]]=json_body
                with open(self.catalog_address, "w") as f:
                    json.dump(catalog, f, indent=4)
                return json_body
            else:
                raise cherrypy.HTTPError(status=400, message=f'ERROR in post request, {uri[0]} field not found')
            with open(self.catalog_address, "w") as f:
                json.dump(catalog, f, indent=4)
            return json_body
      
    def DELETE(self, *uri):
        with lock:
            with open(self.catalog_address, "r") as f:
                catalog = json.load(f)
            if uri[0]=='devices':
                removeDevice(catalog,uri[1])
                output = f"Device with id {uri[1]} has been removed"
                print(output)
            elif uri[0]=='patients':
                removePatient(catalog,uri[1])
                output = f"Service with id {uri[1]} has been removed"
                print(output)
            elif uri[0]=='services':
                removeService(catalog,uri[1])
                output = f"Service with id {uri[1]} has been removed"
                print(output)
            else:
                raise cherrypy.HTTPError(status=400, message=f'ERROR in delete request, {uri[0]} field not found')
            with open(self.catalog_address, "w") as f:
                json.dump(catalog, f, indent=4)
    

def run_cherrypy_server(catalog,ip):
    local_ip=ip[:-5]
    port=ip[-4:]
    # Configurazioni di CherryPy
    cherrypy.config.update({'server.socket_host': local_ip, 'server.socket_port': int(port)})
    cherrypy.tree.mount(catalog, '/', conf)

    cherrypy.engine.start()

    print("\n____________________________________________________________\n")
    print(f"  Catalog running at http://{ip}")
    print("____________________________________________________________\n")
    print("Press Ctrl+C to stop the server. \n")

    cherrypy.engine.block()  # Questo blocca il thread in esecuzione di CherryPy

if __name__ == "__main__":
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }

    catalog = CatalogREST("catalog.json")
    
    # Crea un thread separato per eseguire il server CherryPy
    cherrypy_thread = threading.Thread(target=run_cherrypy_server, args=(catalog,catalog.ip,))
    cherrypy_thread.start()

    # Questo ciclo sarà nel main thread e permetterà di gestire l'interruzione
    try:
        while True:
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("Catalog stopped by user")
        cherrypy.engine.exit()  # Termina il motore di CherryPy
        cherrypy_thread.join()  # Aspetta che il thread di CherryPy finisca
