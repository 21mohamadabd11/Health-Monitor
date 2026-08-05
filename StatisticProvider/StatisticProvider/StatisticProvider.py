import requests
import json
import cherrypy
import time
import socket
import threading
from fpdf import FPDF
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np
import tempfile
import os
from io import BytesIO
from datetime import datetime
import uuid
from scipy import stats

class StatisticProvider:
    exposed = True
    def __init__(self, settings):
        self.settings = settings
        self.catalogURL = settings['catalogURL']
        self.serviceInfo = settings['serviceInfo']
        self.serviceID = self.serviceInfo['id']
        self.url=self.serviceInfo['url']
        self.patients_dict = requests.get(f"{self.catalogURL}/patients").json()
        self.services = requests.get(f"{self.catalogURL}/services").json()
        print(self.services)
        time.sleep(7)
        a=False
        for service in self.services:
            #print(f'\n{service.get("serviceName")} == "ThingspeakAdaptor"\n')
            if service.get("serviceName") == "ThingspeakAdaptor":
                self.ts_adaptor_url = service.get("url")
                #print('TROVATO')
                a=True
                break
        if not a:
            self.ts_adaptor_url= "http://tsa:9091"
            #raise Exception("ThingspeakAdaptor service not found in catalog!")
            
        self.actualTime = time.time()

    def GET(self, *uri, **params):
        self.patients_dict = requests.get(f"{self.catalogURL}/patients").json()
        self.services = requests.get(f"{self.catalogURL}/services").json()
        if uri[0] in self.patients_dict:
            patientID = uri[0]
            field = params["field"]
            start = params["start"]
            end = params["end"]
            
            url = f"{self.ts_adaptor_url}/{patientID}?field={field}&start={start}&end={end}"

            try:
                response = requests.get(url=url)
                response.raise_for_status()  # Verifica errori HTTP (es. 404, 500)
                data = response.json()
            except requests.exceptions.HTTPError as errh:
                print("HTTP error:", errh)
                raise cherrypy.HTTPError(502, "Errore nella richiesta al ThingSpeakAdaptor")
            except requests.exceptions.ConnectionError as errc:
                print("Connection error:", errc)
                raise cherrypy.HTTPError(504, "Connessione al ThingSpeakAdaptor fallita")
            except requests.exceptions.Timeout as errt:
                print("Timeout error:", errt)
                raise cherrypy.HTTPError(504, "Timeout nella richiesta al ThingSpeakAdaptor")
            except requests.exceptions.RequestException as err:
                print("Altro errore richiesta:", err)
                raise cherrypy.HTTPError(500, "Errore generico nella richiesta")
            except requests.exceptions.JSONDecodeError:
                print("Risposta non JSON dal ThingSpeakAdaptor")
                print("Contenuto:", response.text)

                raise cherrypy.HTTPError(500, "Risposta non valida (non JSON) dal ThingSpeakAdaptor")
            
            field_number = self.patients_dict[patientID]["TS_params"]["health"]["fields"][field]
            data_list = [float(d[field_number]) for d in data["feeds"] if d.get(field_number) not in [None, "null", ""]]
            timestamps = [d["created_at"] for d in data["feeds"]]
            all_data = requests.get(f"{self.ts_adaptor_url}/{patientID}?field={field}").json()
            all_data_list = [float(d[field_number]) for d in all_data["feeds"] if d.get(field_number) not in [None, "null", ""]]

            statistics, statistics_historical, t_stat, p_value, results = self.getStatistics(data_list, all_data_list)
            image_buffer = self.createPlot(timestamps=timestamps, data=data_list, label=field, title=data["channel"]["name"])

            # Creazione del PDF
            pdf_buffer = self.createPdf(statistics, statistics_historical,  t_stat, p_value, results, image_buffer, self.patients_dict[patientID])

            cherrypy.response.headers['Content-Type'] = 'application/pdf'
            return pdf_buffer.getvalue()

    def getStatistics(self, data, historical_data):
        """Calcola le statistiche sui dati"""
        data = np.array(data)
        historical_data = np.array(historical_data)

        # Calcolo statistiche
        statistics = {
            "mean": np.mean(data),
            "min": np.min(data),
            "max": np.max(data),
            "std_dev": np.std(data),
        }

        statistics_historical = {
            "mean": np.mean(historical_data),
            "min": np.min(historical_data),
            "max": np.max(historical_data),
            "std_dev": np.std(historical_data),
        }

        # Test statistico (t-test)
        t_stat, p_value = stats.ttest_ind(data, historical_data, equal_var=False)

        # Interpretazione del risultato
        significance_threshold = 0.05
        if p_value < significance_threshold:
            result = "Differenza significativa (p < 0.05)"
        else:
            result = "Nessuna differenza significativa"

        return statistics, statistics_historical, t_stat, p_value, result

    def createPlot(self, timestamps, data, label, title):

        img_buffer = BytesIO()

        plt.figure(figsize=(15, 10))

        n_ticks = 10
        tick_pos = np.linspace(0, len(timestamps) - 1, n_ticks, dtype=int)
        tick_labels = [f"{timestamps[i]}" for i in tick_pos]

        # Plotta la temperatura
        plt.plot(timestamps, data, color='tab:red', label=label)

        # Personalizza il grafico
        plt.xlabel('Tempo', fontsize=18)
        plt.ylabel(label, fontsize=18)
        plt.title(title)
        plt.xticks(ticks=tick_pos, labels=tick_labels, rotation=45, ha="right")
        plt.tight_layout()  # Aggiunge margini per evitare il taglio

        plt.savefig(img_buffer, format='PNG')
        plt.close()
        img_buffer.seek(0)

        return img_buffer

    def createPdf(self, statistics, statistics_historical,  t_stat, p_value, result, img_buffer, patient_data):
        """Crea un PDF con le statistiche e il grafico"""
        pdf_buffer = BytesIO()
        pdf = FPDF()
        pdf.add_page()
        patient_name = patient_data["name"]
        patient_surname = patient_data["surname"]

        # Aggiunta del testo con le statistiche
        pdf.set_font("Times", style="B", size=16)
        patientID = patient_data["id"]
        pdf.cell(200, 12, txt=f"Report Paziente: {patient_name} {patient_surname}", ln=True, align='C')
        pdf.ln(10)

        # Aggiunta dell'immagine del grafico
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_image_file:
            temp_image_file.write(img_buffer.getvalue())
            temp_image_file.close()  # Chiudi il file temporaneo

            # Aggiungi l'immagine al PDF utilizzando il percorso del file temporaneo
            pdf.image(temp_image_file.name, x=10, y=pdf.get_y(), w=180, h=120)  # Posizione e larghezza dell'immagine
            pdf.ln(120)  # Spazio dopo l'immagine

            # Rimuovi il file temporaneo
            os.remove(temp_image_file.name)

        pdf.set_font("Times", "B", size=12)
        pdf.cell(200, 10, txt="Parametri statistici relativi al periodo analizzato", ln=True)
        pdf.set_font("Times", size=12)
        pdf.cell(200, 10, txt="Confronto con i dati storici del paziente", ln=True)
        pdf.set_font("Times", "B", size=12)
        pdf.cell(95, 10, "Dati Recenti", border=1, ln=False, align='L')
        pdf.cell(95, 10, "Dati Storici", border=1, ln=True, align='R')

        pdf.set_font("Times", size=12)
        pdf.cell(95, 10, f"Media: {statistics['mean']:.2f}", border=1, ln=False, align='L')
        pdf.cell(95, 10, f"Media: {statistics_historical['mean']:.2f}", border=1, ln=True, align='R')

        pdf.cell(95, 10, f"Dev. Standard: {statistics['std_dev']:.2f}", border=1, ln=False, align='L')
        pdf.cell(95, 10, f"Dev. Standard: {statistics_historical['std_dev']:.2f}", border=1, ln=True, align='R')

        pdf.cell(95, 10, f"Minimo: {statistics['min']}", border=1, ln=False, align='L')
        pdf.cell(95, 10, f"Minimo: {statistics_historical['min']}", border=1, ln=True, align='R')

        pdf.cell(95, 10, f"Massimo: {statistics['max']}", border=1, ln=False, align='L')
        pdf.cell(95, 10, f"Massimo: {statistics_historical['max']}", border=1, ln=True, align='R')

        pdf.ln(10)

        # Test statistico
        pdf.set_font("Times", 'B', 12)
        pdf.cell(200, 10, "Test Statistico (t-test) con significatività al 5 %", ln=True)
        pdf.set_font("Times", size=12)
        pdf.cell(200, 10, f"P-Value: {p_value:.4f}", ln=True)
        pdf.cell(200, 10, f"Risultato: {result}", ln=True)
        pdf.ln(10)

        # Salvataggio del PDF nel buffer
        pdf_output = pdf.output(dest='S').encode('latin1')  # Usa 'S' per restituire come stringa/bytes

        pdf_buffer.write(pdf_output)  # Scrivi il PDF nel buffer
        pdf_buffer.seek(0)  # Spostati all'inizio del buffer

        return pdf_buffer

    def registerService(self):
        self.serviceInfo['last_update'] = self.actualTime
        requests.post(f'{self.catalogURL}/services', data=json.dumps(self.serviceInfo))

    def updateService(self):
        self.actualTime = time.time()
        self.serviceInfo['last_update'] = self.actualTime
        requests.put(f'{self.catalogURL}/services', data=json.dumps(self.serviceInfo))

    def deleteService(self):
        requests.delete(f'{self.catalogURL}/services/{self.serviceID}')


def run_cherrypy_server(stat_provider,url):
    local_ip=url[-7:-5]
    port=int(url[-4:])
    # Configurazioni di CherryPy
    cherrypy.config.update({'server.socket_host': local_ip, 'server.socket_port': port})
    cherrypy.tree.mount(stat_provider, '/', conf)

    cherrypy.engine.start()

    print("\n____________________________________________________________\n")
    print(f"  Statistic provider running at http://{local_ip}:{port}")
    print("____________________________________________________________\n")
    print("Press Ctrl+C to stop the server. \n")

    cherrypy.engine.block()  # Questo blocca il thread in esecuzione di CherryPy

if __name__ == "__main__":
    time.sleep(5)
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True
        }
    }

    settings = json.load(open('settings.json'))
    stat_provider = StatisticProvider(settings)
    stat_provider.registerService()

    # Crea un thread separato per eseguire il server CherryPy
    cherrypy_thread = threading.Thread(target=run_cherrypy_server, args=(stat_provider,stat_provider.url,))
    cherrypy_thread.start()

    # Questo ciclo sarà nel main thread e permetterà di gestire l'interruzione
    try:
        counter_catalog = 0
        while True:
            time.sleep(1)
            counter_catalog += 1
            if counter_catalog == 40:
                stat_provider.updateService()
                counter_catalog = 0

    except KeyboardInterrupt:
        stat_provider.deleteService()
        print("Statistic provider stopped")
        cherrypy.engine.exit()  # Termina il motore di CherryPy
        cherrypy_thread.join()  # Aspetta che il thread di CherryPy finisca