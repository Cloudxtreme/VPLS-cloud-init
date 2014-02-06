import os
import re
import shutil
from utils import Utils

# Set Root Password \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ #
class RootPasswd():
    
    # Initialize the class
    def __init__(self, utils):
        self.utils = utils
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
            root_pass = self.utils.gen_passwd(self.rp)
            
            # Get the shadow files ready
            self._sprep()
            
            # Open both shadow files
            sm_fc = open(self.sm, 'r+').read()
            sa_fc = open(self.sa, 'r+').read()
            
            # Update the root password
            self.utils.log.info('Updating root password hash in: ' + self.sm + ' and ' + self.sa)
            pass_rx = re.compile('(^root:)[^:]*(:.*$)', re.MULTILINE)
            shadow_new = pass_rx.sub(r'\g<1>' + root_pass['hash'] + r'\g<2>', sm_fc)
            
            # Write the the files
            open(self.sm, 'r+').write(shadow_new)
            open(self.sa, 'r+').write(shadow_new)
            
            # Clean up the shadow files and return the root password
            self._sclean()
            self.utils.passwd = root_pass['clear']