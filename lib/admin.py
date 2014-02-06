import os
import re
from utils import Utils

# Cloud Administrator Account \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ #
class CloudAdmin():
    def __init__(self, utils):
        self.utils      = utils
            
    # Create the admin user account
    def create_user(self):
        if self.utils.sys_type == 'Linux':
        
            # Generate a random password and hash
            admin_pass  = self.utils.gen_passwd()
            
            # Create the user account
            self.utils.log.info('Creating cloud administrator account: ' + self.utils.vm_admin)
            os.system("useradd -p '" + admin_pass['hash'] + "' " + self.utils.vm_admin)
            
            # Create the sudoers file depending on the Linux version
            if self.utils.os_type['distro'] == 'CentOS':
                self.utils.log.info('Updating sudoers configuration')
                
                # CentOS 6.x
                if re.match('^6\.[0-9]*$', self.utils.os_type['version']):
                    sf_file    = '/etc/sudoers.d/' + self.utils.vm_admin
                    sf_content = "Defaults !requiretty\n" \
                                 "" + self.utils.vm_admin + ' ALL = (root) NOPASSWD:ALL'
                    sf_handle  = open(sf_file, 'w+')
                    sf_handle.write(sf_content)
                    sf_handle.close()
                    
                    # Set permissions for the file
                    os.chmod(sf_file, 0400)
                    
                # CentOS 5.x
                elif re.match('^5\.[0-9]*$', self.utils.os_type['version']):
                    sf_file     = '/etc/sudoers'
                    sf_usr_line = self.utils.vm_admin + " ALL=(ALL) NOPASSWD:ALL\n"
                    sf_fc       = open(sf_file, 'r+').read()
            
                    # Disable TTY requirements for sudo
                    sf_tty_rx   = re.compile(r'(^Defaults[ ]*)(requiretty.*$)', re.MULTILINE)
                    sf_new      = sf_tty_rx.sub(r'\g<1>!\g<2>', sf_fc)
            
                    # Insert the cloud administrator user line
                    sf_usr_rx   = re.compile(r'(^root.*ALL.*$)', re.MULTILINE)
                    sf_final    = sf_usr_rx.sub(r'\g<1>\n' + sf_usr_line, sf_new)
            
                    # Write the new file
                    sf_fh       = open(sf_file, 'w+')
                    sf_fh.write(sf_final)
                    sf_fh.close()
            
                # Unsupported CentOS distribution
                else:
                    self.utils.error(3, self.utils.os_type['version'])
            
            # Create the authorized keys file
            self.utils.log.info('Loading SSH public key: ' + self.utils.meta_json['public_keys'][self.utils.vm_admin])
            admin_home    = '/home/' + self.utils.vm_admin
            os.mkdir(admin_home + '/.ssh')
            ak_file       = admin_home + '/.ssh/authorized_keys'
            ak_handle     = open(ak_file, 'w+')
            ak_handle.write(self.utils.meta_json['public_keys'][self.utils.vm_admin])
            ak_handle.close()
            
            # Set permissions on the SSH directory and files
            self.utils.log.info('Setting SSH directory permissions')
            os.chmod(admin_home + '/.ssh', 0700)
            os.chmod(ak_file, 0644)
            os.system('chown -R ' + self.utils.vm_admin + ':' + self.utils.vm_admin + ' ' + admin_home + '/.ssh')