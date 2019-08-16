

import configparser
from utils import utils as my_utils

################################################################################

version = 'Atom Quant Analysis System, Version: 0.0.1'

configfile = './config.ini'
default_section = 'default'
default_datapath = './data/'
default_daypath = 'day/'
default_inxpath = 'inx/'
default_model = 'rate'

default_logpath = './data/logs/'

################################################################################

ohlc_lst = ['open', 'high', 'low', 'close']
volume_lst = ['volume']
profit_lst = ['next_profit_1', 'next_profit_2', 'next_profit_3', 'next_profit_4', 'next_profit_5', 'next_profit_6', 'next_profit_7', 'next_profit_8', 'next_profit_9', 'next_profit_10']

################################################################################

ma100_lst_var = [2, 3, 5, 10, 15, 20, 25, 30, 50, 100]
ma100_lst = ['ma_2', 'ma_3', 'ma_5', 'ma_10', 'ma_15', 'ma_20', 'ma_25', 'ma_30', 'ma_50', 'ma_100']
ma200_lst_var = [2, 3, 5, 10, 15, 20, 25, 30, 50, 100, 150, 200]
ma200_lst = ['ma_2', 'ma_3', 'ma_5', 'ma_10', 'ma_15', 'ma_20','ma_30', 'ma_50', 'ma_100', 'ma_150', 'ma_200']
ma030_lst_var = [2, 3, 5, 10, 15, 20, 25, 30]
ma030_lst = ['ma_2', 'ma_3', 'ma_5', 'ma_10', 'ma_15', 'ma_20', 'ma_25', 'ma_30']
xagv_lst = ['xavg1', 'xavg2', 'xavg3', 'xavg4', 'xavg5', 'xavg6', 'xavg7', 'xavg8', 'xavg9']
rate_lst = ['next_rate_5', 'next_rate_10']
other_lst = ['price_range', 'amp', 'amp_type']

################################################################################



class config:
    def __init__(self, filename=configfile):
        self.conf = configparser.ConfigParser()
        self.filename = filename
        if my_utils.path_exists(self.filename) == False:
            self.writeconfig('init')

        self.conf.read(self.filename)
        section = self.conf.sections()[0]
        print(section) # print(self.conf.options(section))
        print(self.conf.items(section))

    def readconfig(self, section='default', item=''):
        if len(section) <= 0:
            section = self.conf.sections()[0]
        return self.conf.get(section, item)

    def writeconfig(self, section=default_section, item='', value=''):
        if section == 'init':
            section = default_section
            # 写入配置文件
            self.conf.add_section('default')  # 添加section
            # 添加值
            self.conf.set(section, 'datapath', default_datapath)
            self.conf.set(section, 'daypath', default_daypath)
            self.conf.set(section, 'inxpath', default_inxpath)
        else:
            self.conf.set(section, item, value)

        # 写入文件
        with open(self.filename, 'w') as fw:
            self.conf.write(fw)

class params:
    def __init__(self, filename=configfile):
        self.config_obj = config(filename)
        self.data_path = self.config_obj.readconfig(default_section, "datapath")
        self.day_path = self.data_path + self.config_obj.readconfig(default_section, "daypath")
        self.inx_path = self.data_path + self.config_obj.readconfig(default_section, "inxpath")

    def set_item_value(self, item, value):
        self.config_obj.writeconfig(default_section, item, value)

    def print_current_information(self):
        print("-----------------------------")
        print("current_information:")
        print("main_path:" + self.main_path)
        print("day_path:" + self.day_path)
        print("inx_path:" + self.inx_path)
        print("-----------------------------")

global_obj = params()