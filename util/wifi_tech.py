import logging
import socket
import time

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
                    logging.info('client socket for key closed successfully!')
