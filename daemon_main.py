import os
import sys
import time

from utils import logger as log
from utils import daemon as dm
from utils import params as my_params
import training as my_train

class TDaemon(dm.Daemon):
    def __init__(self, *args, **kwargs):
        super(TDaemon, self).__init__(*args, **kwargs)

        self.log_obj = log.logger(my_params.default_logpath + my_params.app_name + '.log')

        my_params.g_config.print_current_information()

    def run(self):
        my_train.loadconfig(my_params.default_configfile)

def control_daemon(action):
    os.system(" ".join((sys.executable, __file__, action)))

def usage():
    print("usage : start, stop , restart")

if __name__ == '__main__':

    if len(sys.argv) == 1:
        # unittest.main()
        usage()
    elif len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg in ('start', 'stop', 'restart'):
            d = TDaemon(my_params.default_pid, verbose = 0)
            getattr(d, arg)()
