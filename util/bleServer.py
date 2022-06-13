import logging
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
            self.clientSocket.close()
            self.serverSocket.close()
            logging.info("Bluetooth sockets successfully closed ...")
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
        self.acceptBluetoothConnection()

    def receive(self):
        # receive data
        dataRecv = self.recvData()
        logging.info(dataRecv)

    def stop(self):
        # Disconnecting bluetooth sockets
        self.closeBluetoothSocket()


# if __name__ == '__main__':
#     bleSvr = bleServer()
#     bleSvr.start()
#     # bleSvr.receive()
#     bleSvr.stop()
