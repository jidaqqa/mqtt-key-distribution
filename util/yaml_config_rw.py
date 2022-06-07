import logging
import os
import datetime
import yaml


class YmalReader():

    def read_yaml(self, filename):
        config_file_path = os.path.dirname(os.path.abspath(filename)) + "/" + filename
        with open(config_file_path, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        return cfg

    def write_yaml(self, filename, key_cfg_dic):
        config_file_path = os.path.dirname(os.path.abspath(filename)) + "/" + filename
        with open(config_file_path, 'w') as ymlfile:
            yaml.dump(key_cfg_dic, ymlfile, default_flow_style=False)

    def read_key_distribution_timing(self, filename):
        timing = {}
        config_file_path = os.path.dirname(os.path.abspath(filename)) + "/" + filename
        with open(config_file_path, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)

        if bool(cfg['key_renew_timing']):
            value = str(cfg['key_renew_timing'])
            splited_value =value.split("/")
            timing["seconds"] = int(splited_value[3])
            timing["minutes"] = int(splited_value[2])
            timing["hours"] = int(splited_value[1])
            timing["days"] = int(splited_value[0])
        else:
            timing["days"] = 0
            timing["hours"] = 12
            timing["minutes"] = 0
            timing["seconds"] = 0
        return timing


