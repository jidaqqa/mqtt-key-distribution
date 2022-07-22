import logging
import subprocess

from bluetooth import *  # Python Bluetooth library


class bleServer:
    def __init__(self, serverSocket=None, clientSocket=None):
        if serverSocket is None:
            self.serverSocket = serverSocket
            self.clientSocket = clientSocket
            self.serviceName = "MQTT-Broker"
            self.uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
        else:
            self.serverSocket = serverSocket
            self.clientSocket = clientSocket

    def getBluetoothSocket(self):
        try:
            self.serverSocket = BluetoothSocket(RFCOMM)
            logging.info("Bluetooth server socket successfully created for RFCOMM service...")
        except (BluetoothError, SystemExit, KeyboardInterrupt) as e:
            logging.error("Failed to create the bluetooth server socket ", exc_info=True)

    def getBluetoothConnection(self):
        try:
            self.serverSocket.bind(("", PORT_ANY))
            logging.info("Bluetooth server socket bind successfully on host "" to PORT_ANY...")
        except (Exception, BluetoothError, SystemExit, KeyboardInterrupt) as e:
            logging.error("Failed to bind server socket on host to PORT_ANY ... ", exc_info=True)
        try:
            self.serverSocket.listen(1)
            logging.info("Bluetooth server socket put to listening mode successfully ...")
        except (Exception, BluetoothError, SystemExit, KeyboardInterrupt) as e:
            logging.error("Failed to put server socket to listening mode  ... ", exc_info=True)
        try:
            port = self.serverSocket.getsockname()[1]
            logging.info("Waiting for connection on RFCOMM channel %d" % (port))
        except (Exception, BluetoothError, SystemExit, KeyboardInterrupt) as e:
            logging.error("Failed to get connection on RFCOMM channel  ... ", exc_info=True)

    def advertiseBluetoothService(self):
        try:
            advertise_service(self.serverSocket, self.serviceName,
                              service_id=self.uuid,
                              service_classes=[self.uuid, SERIAL_PORT_CLASS],
                              profiles=[SERIAL_PORT_PROFILE],
                              #                   protocols = [ OBEX_UUID ]
                              )
            logging.info("%s advertised successfully ..." % (self.serviceName))
        except (Exception, BluetoothError, SystemExit, KeyboardInterrupt) as e:
            logging.error("Failed to advertise bluetooth services  ... ", exc_info=True)

    def acceptBluetoothConnection(self):
        try:
            self.clientSocket, clientInfo = self.serverSocket.accept()
            logging.info("Accepted bluetooth connection from %s", clientInfo)
            return clientInfo
        except (Exception, BluetoothError, SystemExit, KeyboardInterrupt) as e:
            logging.error("Failed to accept bluetooth connection ... ", exc_info=True)

    def recvData(self):
        try:
            while True:
                data = self.clientSocket.recv(1024)
                if not data:
                    break
                return data.decode()
            logging.info("Data received successfully over bluetooth connection")
            return data
        except (Exception, IOError, BluetoothError) as e:
            pass

    def closeBluetoothSocket(self):
        try:
            if self.clientSocket:
                self.clientSocket.close()
            self.serverSocket.close()
            logging.info("Bluetooth sockets successfully closed ...")
        except (Exception, BluetoothError) as e:
            logging.error("Failed to close the bluetooth sockets ", exc_info=True)

    def closeClientSocket(self):
        try:
            self.clientSocket.close()
            logging.info("Client Bluetooth sockets successfully closed ...")
        except (Exception, BluetoothError) as e:
            logging.error("Failed to close the bluetooth sockets ", exc_info=True)

    def sendData(self, data):
        logging.info("Sending Data!")
        self.clientSocket.send(data)

    def start(self):
        # Create the server socket
        self.getBluetoothSocket()
        # get bluetooth connection to port # of the first available
        self.getBluetoothConnection()
        # advertising bluetooth services
        self.advertiseBluetoothService()
        # Accepting bluetooth connection
        # self.acceptBluetoothConnection()

    def receive(self):
        # receive data
        dataRecv = self.recvData()
        logging.info(dataRecv)
        return dataRecv

    def stop(self):
        # Disconnecting bluetooth sockets
        self.closeBluetoothSocket()

    def get_rssi(self, addr):
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


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s',
                                  '%m-%d-%Y %H:%M:%S')

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)

    file_handler = logging.FileHandler('logs.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stdout_handler)

    bleSvr = bleServer()
    bleSvr.start()
    clientInfo = bleSvr.acceptBluetoothConnection()

    count = 0
    while True:
        try:
            current_rssi = bleSvr.get_rssi(clientInfo[0])
        except SystemError as e:
            logging.info("RSSI Value No Found!")
            continue
        if current_rssi is not None:
            print(f"Current RSSI: {str(current_rssi)}")
            with open('bl.txt', 'a') as f:
                f.write(str(current_rssi))
                f.write("\n")
            count = count + 1
            if count == 20:
                bleSvr.start()
                break

    # bleSvr.receive()
    # bleSvr.stop()
