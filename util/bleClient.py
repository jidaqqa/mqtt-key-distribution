import logging
import logging.config
import json  # Uses JSON package
from bluetooth import *  # Python Bluetooth library


class bleClient:
    def __init__(self, clientSocket=None):
        if clientSocket is None:
            self.clientSocket = clientSocket
            self.bleService = None
            self.addr = None
            self.uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
        else:
            self.clientSocket = clientSocket

    def getBluetoothServices(self):
        try:
            bleService = {}
            logging.info("Searching for  Bluetooth services ...")
            for reConnect in range(1, 4):
                bleService = find_service(name="MQTT-Broker", address=self.addr)
                if len(bleService) == 0:
                    logging.info("Re-connecting  Bluetooth services : %d attempt", reConnect)
                else:
                    break
            if not bleService:
                raise SystemExit()
            else:
                logging.info("Found  Bluetooth services ..")
                logging.info("Protocol\t: %s", bleService[0]['protocol'])
                logging.info("Name\t\t: %s", bleService[0]['name'])
                logging.info("Service-id\t: %s", bleService[0]['service-id'])
                logging.info("Profiles\t: %s", bleService[0]['profiles'])
                logging.info("Service-class\t: %s", bleService[0]['service-classes'])
                logging.info("Host\t\t: %s", bleService[0]['host'])
                logging.info("Provider\t: %s", bleService[0]['provider'])
                logging.info("Port\t\t: %s", bleService[0]['port'])
                logging.info("Description\t: %s", bleService[0]['description'])
                self.bleService = bleService
        except (Exception, BluetoothError, SystemExit, KeyboardInterrupt) as e:
            logging.error("Couldn't find the MQTT-Broker Bluetooth service", exc_info=True)

    def getBluetoothSocket(self):
        try:
            self.clientSocket = BluetoothSocket(RFCOMM)
            logging.info("Bluetooth client socket successfully created for RFCOMM service  ...")
        except (Exception, BluetoothError, SystemExit, KeyboardInterrupt) as e:
            logging.error("Failed to create the bluetooth client socket for RFCOMM service  ...  ", exc_info=True)

    def getBluetoothConnection(self):
        bleServiceInfo = {}
        try:
            bleServiceInfo = self.bleService[0]
            logging.info("Connecting to \"%s\" on %s with port %s" % (
                bleServiceInfo['name'], bleServiceInfo['host'], bleServiceInfo['port']))
            self.clientSocket.connect((bleServiceInfo['host'], bleServiceInfo['port']))
            logging.info("Connected successfully to %s " % (bleServiceInfo['name']))
        except (Exception, BluetoothError, SystemExit, KeyboardInterrupt) as e:
            logging.error("Failed to connect to \"%s\" on address %s with port %s" % (
                bleServiceInfo['name'], bleServiceInfo['host'], bleServiceInfo['port']), exc_info=True)

    def sendData(self):
        logging.info("Sending Data!")
        self.clientSocket.send("Hi")

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
            self.clientSocket.close()
            logging.info("Bluetooth client socket successfully closed ...")
        except (Exception, BluetoothError, SystemExit, KeyboardInterrupt) as e:
            logging.error("Failed to close the bluetooth client socket ", exc_info=True)

    def start(self):
        # Search for the MQTT-Broker Bluetooth service
        if self.getBluetoothServices():
            # Create the client socket
            self.getBluetoothSocket()
            # Connect to bluetooth service
            self.getBluetoothConnection()
            # self.sendData()

    def receive(self):
        # receive data
        dataRecv = self.recvData()
        logging.info(dataRecv)
        return dataRecv

    def stop(self):
        # Disconnecting bluetooth service
        self.closeBluetoothSocket()


# if __name__ == '__main__':
#     logging.info("Setup logging configuration")
#     bleClnt = bleClient()
#     bleClnt.start()
#     bleClnt.receive()
#     bleClnt.stop()
