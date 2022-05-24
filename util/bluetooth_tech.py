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
        logging.info("Waiting for connection on RFCOMM channel" + str(port))

        client_sock, client_info = server_sock.accept()
        logging.info(f"Accepted connection from {client_info}")

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
