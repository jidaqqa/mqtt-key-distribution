import time
import hci_rssi

for i in range(0, 100):
    bt_rssi = hci_rssi.RSSI("E4:5F:01:A5:71:BF")
    current_rssi = bt_rssi.get_rssi()
    time.sleep(1)
