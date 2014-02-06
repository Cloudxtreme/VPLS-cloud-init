import os
import logging

# Cloud Init Logging \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ #
class Logger():
    
    # Class initializer
    def __init__(self):
        self.root      = os.path.abspath(os.path.join(os.path.realpath(__file__), '..', os.pardir))
        logging.basicConfig(filename = self.root + '/cloud_init.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%d-%m-%Y %I:%M:%S')
        self.console   = logging.StreamHandler()
        self.console.setLevel(logging.INFO)
        logging.getLogger('').addHandler(self.console)
        self.log       = logging.getLogger('cloud_init')
    def get_logger(self):
        return self.log