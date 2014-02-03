#!/usr/bin/python
import os
import re
import crypt
import shutil
import string
import random

# Set Root Password \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ #
class RootPasswd():
    
    # Initialize the class
    def __init__(self, meta_pass = None):
        self.rp  = meta_pass
        self.sm  = '/etc/shadow'
        self.sa  = '/etc/shadow-'
    
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
    
    # Random string generator
    def _gen_rstring(self, size = 12):
        chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
        return ''.join(random.choice(chars) for x in range(size))
    
    # Update the root password
    def update(self):
        if not self.rp: self.rp = self._gen_rstring(12)
        root_salt       = self._gen_rstring()
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
        return self.rp