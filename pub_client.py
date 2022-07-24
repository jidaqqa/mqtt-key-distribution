import asyncio
import subprocess
import rssi
from util.gmqtt.client import Client as MQTTClient
import argparse
import random
import ssl
import warnings
import uvloop
import signal
from util.yaml_config_rw import YmalReader
from util.fernet_cha_xtea import *
from util.bleClient import *
from util.lora_wan import loraWan
import socket

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
STOP = asyncio.Event()


def on_connect(client, flags, rc, properties):
    """
    Executed if the client successfully connects to the specified broker
    :param client: client information
    :param flags: flags set in the CONNACK packet
    :param rc: reconnection flag
    :param properties: specified user properties
    """
    logging.info("[CONNECTION ESTABLISHED]")


def on_disconnect(client, packet, exc=None):
    """
    Handle disconnection of client
    :param client: Client that disconnected
    :param packet: Disconnect packet
    :param exc: NOT USED
    """
    logging.info(f'[DISCONNECTED]')


def create_tls_context(cert, key):
    """
    Create an SSLContext object for the TLS connection to the Broker
    :param cert: Client certificate
    :param key: Client private key
    :return: SSL context
    """
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    if os.path.isfile(cert) and os.path.isfile(key):
        context.load_cert_chain(certfile=cert, keyfile=key)
        return context
    else:
        if not os.path.isfile(cert):
            raise FileNotFoundError(f"Certfile '{cert}' not found.")
        if not os.path.isfile(key):
            raise FileNotFoundError(f"Keyfile '{key}' not found.")


def ask_exit(*args):
    STOP.set()


async def main(args):
    """
    Main function of the program. Initiates the publishing process of the Client.
    :param args: arguments provided via CLI
    """

    logging.info(f"Connecting you to {args.host} on Port {args.port}. Your clientID: '{args.client_id}'. "
                 f"Multilateral Security for all messages {'is' if args.multilateral else 'is not'} enabled.")

    user_property = ('multilateral', '1') if args.multilateral else None
    if user_property:
        client = MQTTClient(args.client_id, user_property=user_property)
    else:
        client = MQTTClient(args.client_id)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    # Ready the mode that the Broker needs to use for key distribution such as Bluethooth, Wifi or LoraWAN and the
    # required keys
    yml = YmalReader()
    mode_cfg = yml.read_yaml('mode.yml')
    mode = mode_cfg['mode']

    if not os.path.exists("./client_key.yml"):
        with open("./client_key.yml", "w"):
            pass
        broker_key = {"current_key": ""}
        yml = YmalReader()
        yml.write_yaml('./client_key.yml', broker_key)

    key_cfg = yml.read_yaml('client_key.yml')


    # if both, cert and key, are specified, try to establish TLS connection to broker
    if args.cert and args.key:
        try:
            context = create_tls_context(args.cert, args.key)
            await client.connect(host=args.host, port=args.port, ssl=context)
        except FileNotFoundError as e:
            logging.error(e)
            exit(0)
        except ssl.SSLError:
            logging.error(f"SSL Error. Either your key/cert is not valid or the Broker does not support TLS on Port {args.port}.")
            exit(0)

    # if both are not specified, then connect via insecure channel
    elif not args.cert and not args.key:
        # if mode == "BL" and key_cfg['current_key'] == "":
        #     logging.info("Bluetooth Mode!")
        #     temp = subprocess.check_output(['hcitool', 'dev'])
        #     device_info = temp.decode('utf-8').split()
        #     client.set_auth_credentials(device_info[2])
        # elif mode == "WIFI" and key_cfg['current_key'] == "":
        #     output = subprocess.check_output(['iwgetid'])
        #     interface = output.decode().split()[0]
        #     APSSID = output.decode().split()[1]
        #     rssi_scanner = rssi.RSSI_Scan(interface)
        #     ap_info = rssi_scanner.getAPinfo([APSSID.split('"')[1]])
        #     logging.info(f"WiFi Signal: {ap_info[0]['signal']}")
        #     client.set_auth_credentials(ap_info[0]['signal'])
        # elif mode == "LORA" and key_cfg['current_key'] == "":
        #     client.set_auth_credentials("LORA")
        await client.connect(host=args.host, port=args.port)

    # if only one of them is specified, print error and exit
    else:
        logging.error(f"Client certificate and client private key must be specified if connection should be secure. You have only specified {'the certificate' if args.cert else 'the private key'}.")
        exit(0)

    # Once connected, publish the specified message to the specified topic with specified user properties (multilateral)
    if len(args.multilateral_message) > 0:
        for i, multilateral_security_index in enumerate(args.multilateral_message):
            i += 1
            if multilateral_security_index:
                logging.info(f"Message {i} sent with enforced Multilateral Security")
                user_property_message = ('multilateral', '1')
                client.publish(args.topic, args.message + f" {i}", user_property=user_property_message, qos=0)
            else:
                logging.info(f"Message {i} sent without Multilateral Security")
                client.publish(args.topic, args.message + f" {i}", qos=0)
    else:
        lr = loraWan("/dev/ttyS0", 433, 100, 22, True)
        if key_cfg['current_key'] != "":
            # if mode == "BL":
            #     bleClnt = bleClient()
            #     bleClnt.start("0")
            #     bleClnt.stop()
            # elif mode == "LORA":
            #     lr.send_deal("0", 100)
            # elif mode == "WIFI":
            #     output = subprocess.check_output(['iwgetid'])
            #     interface = output.decode().split()[0]
            #     APSSID = output.decode().split()[1]
            #     rssi_scanner = rssi.RSSI_Scan(interface)
            #     ap_info = rssi_scanner.getAPinfo([APSSID.split('"')[1]])
            #     logging.info(f"WiFi Signal: {ap_info[0]['signal']}")

            if mode_cfg['encryption'] == 0:
                logging.info(f"Publishing '{args.topic}:{args.message}'")
                logging.info(f"Publish Message sent at {time.time()}")
                client.publish(args.topic, args.message, qos=0)
            elif mode_cfg['encryption'] == 1:
                xtea_instance = FernetXtea(key_cfg['current_key'])
                logging.info(f"Publish Message sent at {time.time()}")
                ciphertext = xtea_instance.encrypt(bytes(args.message.encode()))
                logging.info(f"Publishing encrypted message using Xtea for '{args.topic}'")
                client.publish(args.topic, ciphertext, qos=0)
            elif mode_cfg['encryption'] == 2:
                cha_instance = FernetChaCha20Poly1305(bytes(key_cfg['current_key']))
                logging.info(f"Publish Message sent at {time.time()}")
                ciphertext = cha_instance.encrypt(args.message)
                logging.info(f"Publishing encrypted message using ChaCha20Poly1305 for '{args.topic}'")
                client.publish(args.topic, ciphertext, qos=0)
        else:
            logging.info("Reading client key from failed or does not exist")
            if mode == "BL":
                bleClnt = bleClient()
                bleClnt.start()
                key_cfg['current_key'] = bleClnt.receive()
                logging.info(f"Key received at {time.time()}")
                logging.info(key_cfg["current_key"])
                yml.write_yaml('client_key.yml', key_cfg)
                bleClnt.stop()
            elif mode == "LORA":
                lr.send_deal("1", 100)
                data = lr.receive_data()
                logging.info(f"Key received at {time.time()}")
                #if mode_cfg['encryption'] == 1:
                key_cfg['current_key'] = data['payload']
                logging.info(key_cfg["current_key"])
                yml.write_yaml('client_key.yml', key_cfg)
            elif mode == "WIFI":
                output = subprocess.check_output(['iwgetid'])
                interface = output.decode().split()[0]
                APSSID = output.decode().split()[1]
                rssi_scanner = rssi.RSSI_Scan(interface)
                if rssi_scanner.getAPinfo([APSSID.split('"')[1]]):
                    ap_info = rssi_scanner.getAPinfo([APSSID.split('"')[1]])
                key_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                key_socket.connect(('192.168.0.100', 1884))
                if bool(ap_info[0]['signal']):
                    rssi_value = str(ap_info[0]['signal'])
                    key_socket.send(bytes(rssi_value.encode()))
                    from_server = key_socket.recv(4096)
                    logging.info(f"Key Received at {time.time()}")
                    logging.info(from_server)
                else:
                    logging.info("Re-connect!")
                key_socket.close()

    await STOP.wait()
    try:
        await client.disconnect(session_expiry_interval=0)
    except ConnectionResetError:
        logging.info("Broker successfully closed the connection.")

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
    warnings.filterwarnings('ignore', category=DeprecationWarning)

    HOSTNAME = "172.18.0.103"
    PORT = 1883
    CLIENT_ID = str(random.randint(0,50000))

    # argument parser
    parser = argparse.ArgumentParser("client_pub", description="MQTT Publish client supporting Multilateral Security",
                                     epilog="Developed by Babbadeckl. Questions and Bug-reports can be mailed to korbinian.spielvogel@uni-passau.de")
    # argument for client name
    parser.add_argument('-i', '--id', default=CLIENT_ID, type=str, dest="client_id", metavar="CLIENT_ID", help=f"Client identifier. Defaults to random int.")

    # argument for host
    parser.add_argument('-H', '--host', default=HOSTNAME, type=str, dest="host", metavar="HOST", help=f"MQTT host to connect to. Defaults to {HOSTNAME}.")

    # argument for port
    parser.add_argument('-p', '--port', default=PORT, type=int, dest="port", metavar="PORT", help=f"Network port to connect to. Defaults to {PORT}.")

    # argument for topic
    parser.add_argument('-t', '--topic', type=str, dest="topic", metavar="TOPIC", help="MQTT topic to publish to.")

    # argument for message
    parser.add_argument('-m', '--message', type=str, dest="message", metavar="MESSAGE", help="Message payload to send.")

    # argument for cert
    parser.add_argument('--cert', type=str, dest="cert", metavar="CERT", help="Client certificate for authentication, if required by the server.")

    # argument for key
    parser.add_argument('--key', type=str, dest="key", metavar="KEY", help="Client private key for authentication, if required by the server.")

    # argument for multilateral security
    parser.add_argument('--multilateral', action='store_true', dest="multilateral", default=0, help="Enforce multilateral security.")
    # argument for multilateral security per message
    parser.add_argument('--multilateral_message', nargs="+", type=int, dest="multilateral_message", default=[], help="Boolean list (separated by whitespace): define which messages should be sent with enforced multilateral security.")

    args = parser.parse_args()

    try:
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(signal.SIGINT, ask_exit)
        loop.add_signal_handler(signal.SIGTERM, ask_exit)
        loop.run_until_complete(main(args))

    except (KeyboardInterrupt, RuntimeError):
        logging.info("Closing the client.")

