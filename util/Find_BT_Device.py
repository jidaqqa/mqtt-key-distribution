#!/usr/bin/env python

# simple inquiry example
import logging

import bluetooth
import yaml

class FindDevices:

    @staticmethod
    def getavailabledevices(configfilepath):

        with open(configfilepath, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)

        while True:
            nearby_devices = bluetooth.discover_devices(lookup_names=True, lookup_class=True)
            found = len(nearby_devices)

            if found:
                logging.info("Devices Found:")
                for idx, device in enumerate(nearby_devices):
                    logging.info(f"Device %s  %s - %s" % (idx, device[0], device[1]))

                logging.info("Choose your devices number or Enter to repeat the scan or -1 to skip:")
                choice = int(input())

                if choice == "":
                    continue
                elif choice == -1:
                    break
                else:
                    device = nearby_devices[choice]

                # while True:
                #     print("Choose your devices number:")
                #     try:
                #
                #         if choice == -1:
                #             break
                #         else:
                #             device = nearby_devices[choice]
                #     except (ValueError, IndexError):
                #         print("Error: please enter you devices number only e.g. 0")
                #         continue
                #
                #     break

                logging.info(f"Device: {device[1]} has been added to the config")

                cfg['mac_address'] = device[0]

                with open("", 'w') as ymlfile:
                    yaml.dump(cfg, ymlfile, default_flow_style=False)
                break
            else:
                logging.info("No devices found, make sure your device is discoverable, Repeating Scan....")
                continue


