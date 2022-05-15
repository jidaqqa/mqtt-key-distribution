import bluetooth
import logging


class BluetoothTech:

    def __init__(self, addr):
        self.addr = addr

    @staticmethod
    def receivemessages():

        port = 1
        server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        server_sock.bind(("mqtt", port))
        server_sock.listen(1)

        # port = server_sock.getsockname()[1]

        # uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
        #
        # bluetooth.advertise_service(server_sock, "mqttclient", service_id=uuid,
        #                             service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
        #                             profiles=[bluetooth.SERIAL_PORT_PROFILE],
        #                             )

        logging.info("Waiting for connection on RFCOMM channel", port)

        client_sock, client_info = server_sock.accept()
        logging.info("Accepted connection from", client_info)

        try:
            while True:
                data = client_sock.recv(1024)
                if not data:
                    break
                print("Received", data)
        except OSError:
            pass

        logging.info("Disconnected.")

        client_sock.close()
        server_sock.close()
        logging.info("All done.")

    def sendmessage(self, message):

        port = 1
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        sock.connect((self.addr, port))
        sock.send(message)
        logging.info("Message is sent!")
        sock.close()

# lookUpNearbyBluetoothDevices()
# receiveMessages()
