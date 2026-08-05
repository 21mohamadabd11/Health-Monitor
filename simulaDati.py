import time
import random
from dataclasses import dataclass
from typing import Optional
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import numpy as np

@dataclass
class SimParams:
    baseline: float
    std: float

class SimulatedVitalsSensor:
    def __init__(self, interval: float = 5.0):
        """
        Sensore simulato per HR (bpm) e SpO2 (%).

        :param interval: intervallo di lettura in secondi (solo per la simulazione "realtime")
        """
        self.interval = float(interval)
        self.loop = True

        self.hr_simulation_params = SimParams(baseline=70.0, std=3.0)
        self.hr_value = self.hr_simulation_params.baseline

        self.spo2_simulation_params = SimParams(baseline=98.0, std=1.0)
        self.spo2_value = self.spo2_simulation_params.baseline

    # ---------- generatori di singolo campione ----------
    def get_hr_data(self) -> float:
        """
        Aggiorna e restituisce il valore di HR (bpm) usando un random-walk smorzato verso la baseline.
        """
        self.hr_value = 0.9 * self.hr_value + 0.1 * random.gauss(
            self.hr_simulation_params.baseline, self.hr_simulation_params.std
        )
        return float(self.hr_value)

    def get_spo2_data(self) -> float:
        """
        Aggiorna e restituisce il valore di SpO2 (%) usando un random-walk smorzato verso la baseline.
        """
        self.spo2_value = 0.9 * self.spo2_value + 0.1 * random.gauss(
            self.spo2_simulation_params.baseline, self.spo2_simulation_params.std
        )
        return float(self.spo2_value)

    # ---------- generazione batch ----------
    def sample(self, n: int, seed: Optional[int] = None) -> pd.DataFrame:
        """
        Genera n campioni senza attese temporali e li ritorna in un DataFrame.
        Colonne: ['t', 'hr', 'spo2'] dove t è un indice (0..n-1).

        :param n: numero di campioni
        :param seed: opzionale, per riproducibilità
        """
        if seed is not None:
            random.seed(seed)

        t = []
        hrs = []
        spo2s = []
        for i in range(n):
            t.append(i)
            hrs.append(self.get_hr_data())
            spo2s.append(self.get_spo2_data())

        df = pd.DataFrame({"t": t, "hr": hrs, "spo2": spo2s})
        return df

    # ---------- plotting ----------
    @staticmethod
    def plot_histograms(df, bins=25):
        """
        Disegna istogrammi per HR e SpO2 con colori tenui e curva di densità tratteggiata.
        """
        for col, label, color in [("hr", "HR (bpm)", "red"), ("spo2", "SpO₂ (%)", "blue")]:
            data = df[col].dropna()

            # Istogramma con alpha per colore tenue + bordi visibili ma non invadenti
            plt.figure()
            counts, edges, _ = plt.hist(
                data,
                bins=bins,
                color=color,
                edgecolor=color,
                alpha=0.25,        # trasparenza -> colore tenue
                linewidth=1.0,
                density=True
            )

            # Stima e disegna la densità continua (KDE)
            kde = gaussian_kde(data)
            x = np.linspace(data.min(), data.max(), 200)
            plt.plot(x, kde(x), linestyle="--", color=color, linewidth=2)

            # Etichette e titolo
            plt.xlabel(label)
            plt.ylabel("Probability distribution")
            plt.title(f"Histogram and probability distribution of {label}")
            plt.grid(alpha=0.3)
            plt.show()

# ----------------- esempio d'uso -----------------
if __name__ == "__main__":
    sensor = SimulatedVitalsSensor(interval=1.0)

    # genera 500 campioni riproducibili
    df = sensor.sample(n=3000, seed=42)
    # print(df.head())

    # plot descrittivi
    SimulatedVitalsSensor.plot_histograms(df, bins=100)
    # SimulatedVitalsSensor.plot_timeseries(df)
