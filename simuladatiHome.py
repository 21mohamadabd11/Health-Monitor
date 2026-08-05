import random
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import numpy as np

class SimulatedHomeSensor:
    def __init__(self, interval=5):
        """
        Sensore simulato per la temperatura e umidità in una casa.
        
        :param interval: Intervallo di lettura (in secondi).
        """
        self.interval = interval
        self.loop = True

        self.temp_simulation_params = {
            'baseline': 22,  # Temperatura ambiente in gradi Celsius
            'std': 0.2  # Deviazione standard per la variabilità
        }
        self.temp_value = self.temp_simulation_params['baseline']  # Inizializza con il valore di baseline

        self.hum_simulation_params = {
            'baseline': 50,  # Umidità relativa (%)
            'std': 5  # Deviazione standard per la variabilità
        }

        self.hum_value = self.hum_simulation_params['baseline']  # Inizializza con il valore di baseline

    def get_data(self):
        """
        Restituisce i valori simulati di temperatura e umidità.
        """
        humidity = 0.9 * self.hum_value + 0.1 * random.gauss(self.hum_simulation_params['baseline'], self.hum_simulation_params['std'])
        temperature = 0.9 * self.temp_value + 0.1 * random.gauss(self.temp_simulation_params['baseline'], self.temp_simulation_params['std'])
        return humidity, temperature

    def sample(self, n=100, seed=None):
        """
        Genera n campioni simulati di umidità e temperatura.

        :param n: numero di campioni
        :param seed: opzionale, per riproducibilità
        :return: DataFrame pandas con colonne 't', 'temperature', 'humidity'
        """
        if seed is not None:
            random.seed(seed)

        t = []
        temps = []
        hums = []
        for i in range(n):
            t.append(i)
            humidity, temperature = self.get_data()
            hums.append(humidity)
            temps.append(temperature)

        df = pd.DataFrame({"t": t, "temperature": temps, "humidity": hums})
        return df

    @staticmethod
    def plot_histograms(df, bins=25):
        """
        Disegna istogrammi per Temperatura e Umidità con colori tenui e densità tratteggiata.
        """
        for col, label, color in [("temperature", "Temperature (°C)", "orange"), ("humidity", "Humidity (%)", "green")]:
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

    @staticmethod
    def plot_timeseries(df):
        """
        Disegna l’andamento temporale della Temperatura e dell'Umidità.
        """
        plt.figure()
        plt.plot(df["t"], df["temperature"], label="Temperatura (°C)", color="red")
        plt.xlabel("Campione")
        plt.ylabel("Temperatura (°C)")
        plt.title("Andamento della Temperatura nel tempo")
        plt.grid(alpha=0.3)
        plt.show()

        plt.figure()
        plt.plot(df["t"], df["humidity"], label="Umidità (%)", color="blue")
        plt.xlabel("Campione")
        plt.ylabel("Umidità (%)")
        plt.title("Andamento dell'Umidità nel tempo")
        plt.grid(alpha=0.3)
        plt.show()

# ----------------- esempio d'uso -----------------
if __name__ == "__main__":
    sensor = SimulatedHomeSensor(interval=1.0)

    # genera 500 campioni
    df = sensor.sample(n=3000, seed=42)
    # print(df.head())

    # plot descrittivi
    SimulatedHomeSensor.plot_histograms(df, bins=100)
    # SimulatedHomeSensor.plot_timeseries(df)
