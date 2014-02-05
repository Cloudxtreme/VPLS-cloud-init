#!/usr/bin/python
import os
import re
from utils import Utils
from error import Error

# Grow Root Partition \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ #
class GrowPart():
    
    # Class initializer
    def __init__(self, utils):
        self.utils = utils
        self.error = Error(self.utils.cbs)
        
        # Grab the primary partition device and number
        part_rx   = re.compile(r'(^\/dev\/[a-z]*)([0-9]*).*$')
        part_main = os.popen('fdisk -l | grep -e "^\/dev\/[a-z]*1"').read()
        self.part_dev  = part_rx.sub(r'\g<1>', part_main).rstrip()
        self.part_num  = part_rx.sub(r'\g<2>', part_main).rstrip()
        
    # Grow the root partition
    def extend_root(self):
        if self.utils.sys_type == 'Linux':
            os.system('growpart ' + self.part_dev + ' ' + self.part_num)