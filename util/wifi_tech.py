import logging
import socket
import subprocess
import time

import rssi

from util.yaml_config_rw import YmalReader


def check_range(min_power):
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind(('0.0.0.0', 1884))
    serv.listen(5)
    while True:
        conn, addr = serv.accept()
        from_client = ''
        while True:
            data = conn.recv(4096)
            if not data: break
            from_client += str(data.decode())
            logging.info(f"Key Sent at {time.time()}")
            if from_client != '' and int(from_client) >= min_power:
                yml = YmalReader()
                broker_cfg = yml.read_yaml("broker_key.yml")
                if bool(broker_cfg):
                    logging.info(f"Key Found {broker_cfg['current_key']}")
                    logging.info(f"Key sent at {time.time()}")
                    conn.send(broker_cfg['current_key'])
                    conn.close()
                    serv.close()
                    logging.info('client socket for key closed successfully!')
                    return True


def check_range_test():
    output = subprocess.check_output(['iwgetid'])
    interface = output.decode().split()[0]
    APSSID = output.decode().split()[1]
    rssi_scanner = rssi.RSSI_Scan(interface)
    ap_info = rssi_scanner.getAPinfo([APSSID.split('"')[1]])
    if bool(ap_info[0]['signal']):
        rssi_value = str(ap_info[0]['signal'])
        print(f"Current RSSI: {rssi_value}")
        with open('wifi.txt', 'a') as f:
            f.write(str(rssi_value))
            f.write("\n")


# if __name__ == '__main__':
#     count = 0
#     while True:
#         check_range_test()
#         if count == 20:
#             break
#         count += 1
#         time.sleep(5)
