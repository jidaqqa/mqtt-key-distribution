import subprocess
import time
import statistics
import numpy as np
import bluetooth

class RSSI:

    def __init__(self, addr):
        self.addr = addr


    def get_rssi(self):
        bt_sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        bt_sock.connect((self.addr, 1))
        cmd = 'hcitool'
        temp = subprocess.check_output([cmd, 'rssi', self.addr])
        output_rssi = temp.decode('utf-8').split()
        rssi_value = float(output_rssi[3])
        return rssi_value

    def get_average_rssi(self, number_of_loops):
        rssi_value = 0
        for i in range(1, number_of_loops):
            rssi_value = rssi_value + float(self.get_rssi())
            time.sleep(1)
        rssi_average = float(rssi_value / number_of_loops)
        return rssi_average

    def get_rssi_stdev(self, number_of_readings):
        rssi_value = []
        for i in range(0, number_of_readings):
            rssi_value.insert(i, float(self.get_rssi()))
            time.sleep(1)
        rssi_stdev = float(statistics.pstdev(rssi_value))
        return rssi_stdev

    def estimate_distance(self, power_received, params=None):
        """This function returns an estimated distance range
           given a single radio signal strength (RSS) reading
           (received power measurement) in dBm.
        Parameters:
            power_received (float): RSS reading in dBm
            params (4-tuple float): (d_ref, power_ref, path_loss_exp, stdev_power)
                d_ref is the reference distance in m
                power_ref is the received power at the reference distance
                path_loss_exp is the path loss exponent
                stdev_power is standard deviation of received Power in dB
        Returns:
            (d_est, d_min, d_max): a 3-tuple of float values containing
                the estimated distance, as well as the minimum and maximum
                distance estimates corresponding to the uncertainty in RSS,
                respectively, in meters rounded to two decimal points
        """
        if params is None:
            params = (1.0, -55.0, 2.0, 2.5)
            # the above values are arbitrarily chosen "default values"
            # should be changed based on measurements

        cmd = 'hcitool'
        temp = subprocess.check_output([cmd, 'rssi', self.addr])
        output_rssi = temp.decode('utf-8').split()
        rssi_value = float(output_rssi[3])

        d_ref = params[0]  # reference distance
        power_ref = params[1]  # mean received power at reference distance
        path_loss_exp = params[2]  # path loss exponent
        stdev_power = params[3]  # standard deviation of received power

        uncertainty = 2 * stdev_power  # uncertainty in RSS corresponding to 95.45% confidence

        d_est = d_ref * (10 ** (-(power_received - power_ref) / (10 * path_loss_exp)))
        d_min = d_ref * (10 ** (-(power_received - power_ref + uncertainty) / (10 * path_loss_exp)))
        d_max = d_ref * (10 ** (-(power_received - power_ref - uncertainty) / (10 * path_loss_exp)))

        return (np.round(d_est, 2), np.round(d_min, 2), np.round(d_max, 2))

# if __name__ == '__main__':
#    print(get_rssi('E8:5A:8B:9E:EE:D8'))
