import threading
import time
from datetime import datetime, timezone
import random

class HealthSensors(threading.Thread):
    def __init__(self, interval=5):
        """
        Sensore simulato di frequenza cardiaca e pressione sanguigna.
        
        :param interval: Intervallo di lettura (in secondi).
        """
        super().__init__()
        self.interval = interval
        self.loop = True
        
        self.hr_simulation_params = {
            'baseline': 70,
            'std': 3
        }
        self.hr_value = self.hr_simulation_params['baseline']  # Inizializza con il valore di baseline

        self.spo2_simulation_params = {
            'baseline': 98,
            'std': 1
        }

        self.spo2_value = self.spo2_simulation_params['baseline']  # Inizializza con il valore di baseline

    def get_hr_data(self):
        """
        Restituisce i valori di frequenza cardiaca simulandoli con una variazione gaussiana rispetto al valore precedente.
        """
        
        self.hr_value = 0.9 * self.hr_value + 0.1 * random.gauss(self.hr_simulation_params['baseline'], self.hr_simulation_params['std'])
        return

    def get_spo2_data(self):
        """
        Restituisce i valori di saturazione dell'ossigeno simulandoli con una variazione gaussiana rispetto al valore precedente.
        """
        
        self.spo2_value = 0.9 * self.spo2_value + 0.1 * random.gauss(self.spo2_simulation_params['baseline'], self.spo2_simulation_params['std'])
        return
    
    def run(self):
        while self.loop:
            # Generazione dei dati simulati
            self.get_hr_data()
            self.get_spo2_data()

            time.sleep(self.interval)

    def stopSim(self):
        self.loop = False