import subprocess
import json
import requests
import time
import sys

class mainbot:
    def __init__(self):
        self.settings = json.load(open('settings.json'))
        self.catalogURL = self.settings['catalogURL']
        self.serviceInfo = self.settings['serviceInfo']
        self.running = True
        self.bot1 = None
        self.bot2 = None

    def registerService(self):
        self.serviceInfo['last_update'] = time.time()
        requests.post(f'{self.catalogURL}/services', data=json.dumps(self.serviceInfo))

    def updateService(self):
        self.serviceInfo['last_update'] = time.time()
        requests.put(f'{self.catalogURL}/services', data=json.dumps(self.serviceInfo))

    def run(self):
        # Start the bots as subprocesses (not threads)
        self.bot1 = subprocess.Popen(["python", "DoctorBot.py"])
        self.bot2 = subprocess.Popen(["python", "PatientBot.py"])
        self.registerService()

        try:
            while self.running:
                time.sleep(5)
                self.updateService()
        except KeyboardInterrupt:
            print("\nStopping Telegram Bot...")
            self.running = False
        finally:
            print("Terminating bots...")
            for bot in [self.bot1, self.bot2]:
                bot.terminate()
            print("Exited cleanly.")
            sys.exit(0)

if __name__ == '__main__':
    time.sleep(15)
    bot = mainbot()
    bot.run()