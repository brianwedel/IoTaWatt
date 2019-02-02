import numpy
from scipy import integrate
import matplotlib.pyplot as plt

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import json
import time

# Connect to firestore database
cred = credentials.Certificate('../wellshire-testbed-firebase-adminsdk-cdfa8-ade79ce610.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

class EnergyCalculator:
    """ Calculate amount of energy used from stream of power measurements
    """
    def __init__(self, start_time, end_time):

        docs = db.collection(u'house').document(u'kTwB5pLnvThWmqcqIvaU').collection('meas').where(
           u'start_time_ms', u'>', start_time*1000).where(u'start_time_ms', u'<', end_time*1000).get()

        self.data = [d.to_dict() for d in docs]

        self.power_meas = []
        self.timestamp = []

        # Each measurement is 10 second interval with a timestamp "start_time_ms"
        # Just use the first sample
        for d in self.data:
            remote_time_ref = d["samples"][0]["meas_time_ms"]
            for s in d["samples"]:
                self.power_meas.append(s["channel1_power_meas"] + s["channel2_power_meas"])
                timestamp = (d["start_time_ms"] + s["meas_time_ms"] - remote_time_ref)/1000.0
                self.timestamp.append(timestamp)

        print("Number of samples: {}".format(len(self.power_meas)))

    def energy_kwh(self):
        if len(self.timestamp) == 0:
            return 0
        else:
            r = integrate.simps(self.power_meas, self.timestamp)

            # Convert joules (ws) to kwh
            return r/(1000*60*60)

    def plot(self):
        plt.plot(self.timestamp, self.power_meas)
        plt.show()

if __name__ == "__main__":

    start_time = time.mktime((2019, 2, 2, 0, 0, 0, -1, -1, -1))
    end_time = time.mktime((2019, 2, 3, 0, 0, 0, -1, -1, -1))

    e = EnergyCalculator(start_time, end_time)

    print("Energy: {} kwh".format(round(e.energy_kwh(), ndigits=3)))
    e.plot()
