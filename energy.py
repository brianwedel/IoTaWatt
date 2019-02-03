import numpy
from scipy import integrate
import matplotlib.pyplot as plt
import matplotlib.dates as md

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import json
import time
import datetime
import pathlib

class DocumentCache:
    """ Cache documents from firestore database locally in a file.
        Format of cache file is as follows:
        {
            "path": <path to documents> example: /house/kTwB5pLnvThWmqcqIvaU/meas/
            "key" : <name of element in each doc to uniquely identify doc,
                     expect key to be increasing>
            "docs": [
                {
                    "id": <firebase id>
                    "data": <firebase data>
                },
                ...
            ]
        }
    """
    def __init__(self, cred_file, path, key):
        self.path = path
        self.cred_file = cred_file
        self.key = key

        f = self._local_cache_file(path, key)
        with open(f, 'r') as infile:
            self.cache_data = json.load(infile)

        if len(self.cache_data["docs"]) == 0:
            last_key_value = 0
        else:
            last_key_value = self.cache_data["docs"][-1]["data"][self.key]

        # Connect to firestore database and retrieve new data
        cred = credentials.Certificate(self.cred_file)
        firebase_admin.initialize_app(cred)
        db = firestore.client()

        # TODO build doc reference from given path
        new_docs = db.collection(u'house').document(u'kTwB5pLnvThWmqcqIvaU').collection('meas').where(
           self.key, u'>', last_key_value).get()


        # save new data into cache
        num_new_docs = 0
        for d in new_docs:
            num_new_docs = num_new_docs + 1
            cache_entry = {}
            cache_entry["id"] = d.id
            cache_entry["data"] = d.to_dict()
            self.cache_data["docs"].append(cache_entry)

        print("New docs from remote {}".format(num_new_docs))

        # write new cache file
        with open(f, 'w') as outfile:
            json.dump(self.cache_data, outfile)

    def _local_cache_file(self, path, key):
        """ Return path to valid cache file. Create one if doesn't exist
        """
        filename = "cache.json"
        if not pathlib.Path(filename).is_file():
            new_cache = {}
            new_cache["key"] = key
            new_cache["path"] = path
            new_cache["docs"] = []
            with open(filename, 'w') as outfile:
                json.dump(new_cache, outfile)

        return filename

    def docs(self):
       return self.cache_data["docs"]



class EnergyCalculator:
    """ Calculate amount of energy used from stream of power measurements
    """
    def __init__(self, start_time, end_time):

        cache = DocumentCache(
            cred_file = "../wellshire-testbed-firebase-adminsdk-cdfa8-ade79ce610.json",
            path = "/house/kTwB5pLnvThWmqcqIvaU/meas",
            key = "start_time_ms")

        self.data = cache.docs()
        self.power_meas = []
        self.timestamp = []

        # Each measurement is 10 second interval with a timestamp "start_time_ms"
        for d in self.data:
            remote_time_ref = d["data"]["start_time_ms"] - d["data"]["samples"][0]["meas_time_ms"]
            meas_start = d["data"]["start_time_ms"]/1000.0
            if meas_start > start_time and meas_start < end_time:
                for s in d["data"]["samples"]:
                    self.power_meas.append(s["channel1_power_meas"] + s["channel2_power_meas"])
                    timestamp = (remote_time_ref + s["meas_time_ms"])/1000.0
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
        dt = [datetime.datetime.fromtimestamp(t) for t in self.timestamp]
        plt.subplots_adjust(bottom=0.2)
        plt.xticks( rotation=25 )
        ax=plt.gca()
        xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
        ax.xaxis.set_major_formatter(xfmt)

        ax.callbacks.connect('xlim_changed', lambda axes : print(ax.get_xlim()))
        plt.plot(md.date2num(dt), self.power_meas)
        plt.show()

if __name__ == "__main__":

    start_time = time.mktime((2019, 2, 2, 17, 0, 0, -1, -1, -1))
    end_time = time.mktime((2019, 2, 3, 0, 0, 0, -1, -1, -1))

    e = EnergyCalculator(start_time, end_time)

    print("Energy: {} kwh".format(round(e.energy_kwh(), ndigits=3)))
    e.plot()
