import logging
import subprocess
import time
import statistics
import numpy as np
from util.bleServer import bleServer
from util.yaml_config_rw import *


def get_rssi(addr):
    try:
        p = subprocess.Popen('sudo btmgmt find | grep {}'.format(addr), stdout=subprocess.PIPE, shell=True)
        a, b = p.communicate()
        read_lst = []
        for reading in str(a).split('\\n')[:-1]:
            reading = reading.split('rssi ')[1]
            reading = reading.split(' flags')[0]
            reading = int(reading)
            read_lst.append(reading)
        if len(read_lst) > 0:
            return read_lst[0]
        else:
            logging.info("Make sure your device is discoverable, disconnect and connect again!")
            return None
    except SystemError as e:
        logging.info("Make sure your device is discoverable, disconnect and connect again!")


def estimate_distance(d_ref, power_ref, path_loss_exp, key_range):
    """This function returns an estimated distance range
       given a single radio signal strength (RSS) reading
       (received power measurement) in dBm.
    """
    bleSvr = bleServer()
    bleSvr.start()
    clientInfo = bleSvr.acceptBluetoothConnection()
    key_required = bleSvr.receive()
    if key_required != "0":
        current_rssi = get_rssi(clientInfo[0])
        if current_rssi is not None:
            d_est = d_ref * (10 ** (-(current_rssi - power_ref) / (10 * path_loss_exp)))
            logging.info("Current RSSI: " + str(current_rssi))
            logging.info("Power Reference at 1m: " + str(power_ref))
            logging.info(f"Estimated distance in meters is: {d_est} ")
            if d_est <= key_range:
                yml = YmalReader()
                broker_cfg = yml.read_yaml("broker_key.yml")
                if bool(broker_cfg):
                    logging.info(f"Key Found {broker_cfg['current_key']}")
                    bleSvr.sendData(broker_cfg['current_key'])
            else:
                logging.info(f"Device {clientInfo[0]} is out of range! ")
                bleSvr.closeClientSocket()

    bleSvr.stop()


def check_range(min_power):
    """This function returns an estimated range depending on
       given a single radio signal strength (RSS) reading
       (received power measurement) in dBm.
    """
    bleSvr = bleServer()
    bleSvr.start()
    clientInfo = bleSvr.acceptBluetoothConnection()
    key_required = bleSvr.receive()
    if key_required != "0":
        current_rssi = get_rssi(clientInfo[0])
        if current_rssi is not None:
            logging.info("Current RSSI: " + str(current_rssi))
            if current_rssi >= min_power:
                yml = YmalReader()
                broker_cfg = yml.read_yaml("broker_key.yml")
                if bool(broker_cfg):
                    logging.info(f"Key Found {broker_cfg['current_key']}")
                    bleSvr.sendData(broker_cfg['current_key'])
            else:
                logging.info(f"Device {clientInfo[0]} is out of range! ")
                bleSvr.closeClientSocket()

    bleSvr.stop()

# class RSSI:

# def __init__(self):
# def get_rssi(self):
#     bt_sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
#     bt_sock.connect((self.addr, 1))
#     cmd = 'hcitool'
#     temp = subprocess.check_output([cmd, 'rssi', self.addr])
#     output_rssi = temp.decode('utf-8').split()
#     rssi_value = float(output_rssi[3])
#     bt_sock.close()
#     return rssi_value.

# def get_average_rssi(self, number_of_loops):
#     rssi_value = 0
#     for i in range(1, number_of_loops):
#         rssi_value = rssi_value + float(self.get_rssi())
#         time.sleep(1)
#     rssi_average = float(rssi_value / number_of_loops)
#     return rssi_average
#
# def get_rssi_stdev(self, number_of_readings):
#     rssi_value = []
#     for i in range(0, number_of_readings):
#         rssi_value.insert(i, float(self.get_rssi()))
#         time.sleep(1)
#     rssi_stdev = float(statistics.pstdev(rssi_value))
#     return rssi_stdev


# if __name__ == '__main__':
#    print(get_rssi('E8:5A:8B:9E:EE:D8'))
