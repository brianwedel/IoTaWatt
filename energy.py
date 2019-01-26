import random

import numpy
from scipy import integrate

# Input is power samples of the format
# [{
#     "timestamp_ms" :
#     "main0_power_watt" :
#     "main1_power_watt" :
# }]

def gen_meas_rand(prev_meas):
    return prev_meas + random.randint(-50,50)

def gen_meas_const(prev_meas):
    return prev_meas

def gen_test_data(
        num_samples=1,
        sample_rate_samples_per_sec=5,
        start_timestamp_ms=0,
        start_power_meas_watt=0,
        power_model=gen_meas_const):

    running_timestamp_ms = start_timestamp_ms
    data_array = [
        {
            "timestamp_ms" : running_timestamp_ms,
            "main0_power_watt" : power_model(start_power_meas_watt),
            "main1_power_watt" : power_model(start_power_meas_watt)
        }
    ]

    for i in range(1, num_samples):
        running_timestamp_ms = (running_timestamp_ms
                               + int((1/sample_rate_samples_per_sec)*1000))

        data_array.append(
            {
                "timestamp_ms" : running_timestamp_ms,
                "main0_power_watt" : power_model(data_array[-1]["main0_power_watt"]),
                "main1_power_watt" : power_model(data_array[-1]["main1_power_watt"]),
            })

    return data_array

class EnergyCalculator:
    """ Calculate amount of energy used from stream of power measurements
    """
    def __init__(self, power_meas):
        self.power_meas = power_meas
        self.num_samples = len(self.power_meas)

        # Assume array is ordered
        self.num_seconds = (self.power_meas[-1]["timestamp_ms"]
                            - self.power_meas[0]["timestamp_ms"])/1000

    def energy_kwh(self):
        power_meas = [m["main0_power_watt"] for m in self.power_meas]
        # Convert timestamp from msec to sec
        timestamp = [m["timestamp_ms"]/1000 for m in self.power_meas]

        r = integrate.simps(power_meas, timestamp)

        # Convert joules (ws) to kwh
        return r/(1000*60*60)


if __name__ == "__main__":

    target_time_sec = 60*60*24 # 24 hr
    sample_rate = 5 # 5 samples per second

    a = gen_test_data(
        num_samples = (target_time_sec*sample_rate),
        sample_rate_samples_per_sec = sample_rate,
        start_timestamp_ms = 15478893849,
        start_power_meas_watt = 1000,
        power_model = gen_meas_const)

    e = EnergyCalculator(a)

    print("\nEnergy: {} kwh \nTime duration: {} seconds ({} samples)".format(
        round(e.energy_kwh(), ndigits=3),
        e.num_seconds,
        e.num_samples))
