import os
import re
from utils import Utils

# Grow Root Partition \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ #
class GrowPart():
    
    # Class initializer
    def __init__(self, utils):
        self.utils = utils
        
        # Grab the primary partition device and number
        part_rx   = re.compile(r'(^\/dev\/[a-z]*)([0-9]*).*$')
        part_main = os.popen('fdisk -l | grep -e "^\/dev\/[a-z]*1"').read()
        self.part_dev  = part_rx.sub(r'\g<1>', part_main).rstrip()
        self.part_num  = part_rx.sub(r'\g<2>', part_main).rstrip()
        
        # Log the device details
        self.utils.log.info('Discovered root device and partition: ' + self.part_dev + self.part_num)
        
    # Grow the root partition
    def extend_root(self):
        if self.utils.sys_type == 'Linux':
            self.utils.log.info('Extending root partition table to maximum disk capacity')
            
            # CentOS 5/6.x
            if self.utils.os_type['distro'] == 'CentOS':
                
                # CentOS 6.x | cloud-utils-growpart
                if re.match('^6\.[0-9]*$', self.utils.os_type['version']):
                    os.system('growpart ' + self.part_dev + ' ' + self.part_num + ' &> /dev/null')
                
                # CentOS 5.x | fdisk
                if re.match('^5\.[0-9]*$', self.utils.os_type['version']):
                    os.system('sh ' + self.utils.root + '/bash/fdisk.sh "' + self.part_dev + '" "' + self.part_num + '" &> /dev/null')
                    
    # Resize the root partition after reboot
    def resize_root(self):
        self.utils.log.info('Resizing root file system to full partition size')
        os.system('resize2fs ' + self.part_dev + self.part_num + ' &> /dev/null')