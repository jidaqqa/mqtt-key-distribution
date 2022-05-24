import logging
import yaml


class YmalReader():

    def __init__(self, yamlfilepath):
        self.yamlfilepath = yamlfilepath

    def read(self):
        with open(self.yamlfilepath, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)



# if __name__ == '__main__':
#     YmalReader("../mode.yml").readmodeconfig()
