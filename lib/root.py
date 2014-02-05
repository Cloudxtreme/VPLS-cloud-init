#!/usr/bin/python
import os
import re
import crypt
import shutil
from utils import Utils
from error import Error

# Set Root Password \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ #
class RootPasswd():
    
    # Initialize the class
    def __init__(self, utils):
        self.utils = utils
        self.error = Error(self.utils.cbs)
        self.rp    = self.utils.meta_pass
        self.sm    = '/etc/shadow'
        self.sa    = '/etc/shadow-'
    
    # Prepare the system shadow password files
    def _sprep(self):
        shutil.copyfile(self.sm, self.sm + '.bak')
        shutil.copyfile(self.sa, self.sa + '.bak')
        os.chmod(self.sm, 0700)
        os.chmod(self.sm, 0700)
    
    # Restore backup shadow files
    def _srestore(self):   
        shutil.copyfile(self.sm + '.bak', self.sm)
        shutil.copyfile(self.sa + '.bak', self.sa)
        os.chmod(self.sm, 0000)
        os.chmod(self.sa, 0000)
    
    # Clean up altered shadow files
    def _sclean(self):
        os.remove(self.sm + '.bak')
        os.remove(self.sa + '.bak')
        os.chmod(self.sm, 0000)
        os.chmod(self.sa, 0000)
    
    # Update the root password
    def update(self):
        
        # Linux root password
        if self.utils.sys_type == 'Linux':
            if not self.rp: self.rp = self.utils.rstring(12)
            root_salt       = self.utils.rstring(16)
            root_hash       = crypt.crypt(self.rp, '$6$' + root_salt)
            
            # Get the shadow files ready
            self._sprep()
            
            # Open both shadow files
            sm_fc = open(self.sm, 'r+').read()
            sa_fc = open(self.sa, 'r+').read()
            
            # Update the root password
            pass_rx = re.compile('(^root:)[^:]*(:.*$)', re.MULTILINE)
            shadow_new = pass_rx.sub(r'\g<1>' + root_hash + r'\g<2>', sm_fc)
            
            # Write the the files
            open(self.sm, 'r+').write(shadow_new)
            open(self.sa, 'r+').write(shadow_new)
            
            # Clean up the shadow files and return the root password
            self._sclean()
            self.utils.adm_pass = self.rp