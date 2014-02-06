import os
import re
import crypt
import string
import random
import requests
import platform
import ConfigParser
import simplejson as json
from log import Logger
from error import Error

# Cloud Init Utilities \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ #
class Utils():
    
    # Class initializer
    def __init__(self):
        self.logger    = Logger()
        self.log       = self.logger.get_logger()
        self.log.info('Logger initialized')
        
        # Load the configuration file
        self.root      = os.path.abspath(os.path.join(os.path.realpath(__file__), '..', os.pardir))
        self.conf      = ConfigParser.ConfigParser()
        self.conf.read(self.root + '/cloud_init.ini')
        
        # Log configuration details
        self.log.info('Discovered cloud_init root: ' + self.root)
        self.log.info('Using configuration file: ' + self.root + '/cloud_init.ini')
        
        # Retrieve the callback server parameters
        self.cbs_host  = self.conf.get('callback', 'host')
        self.cbs_port  = self.conf.get('callback', 'port')
        self.cbs_proto = self.conf.get('callback', 'proto')
        self.cbs_path  = self.conf.get('callback', 'path')
        
        # Retrieve the metadata server parameters
        self.mds_host  = self.conf.get('metadata', 'host')
        self.mds_port  = self.conf.get('metadata', 'port')
        self.mds_proto = self.conf.get('metadata', 'proto')
        self.mds_path  = self.conf.get('metadata', 'path')
        
        # Get the cloud administrator account
        self.vm_admin  = self.conf.get('user', 'name')
        
        # Get the public and private network adapters
        self.if_pub    = self.conf.get('network', 'if_pub')
        self.if_priv   = self.conf.get('network', 'if_priv')
        self.ip_info   = None
        
        # Log the cloud administrator and IP information
        self.log.info('Using cloud administrator account: ' + self.vm_admin)
        self.log.info('Using network interfaces: public = ' + self.if_pub + ', private = ' + self.if_priv)
        
        # Root/administrator password
        self.passwd    = None
        
        # Define the callback and metadata server connect strings
        self.cbs       = "%s://%s:%s/%s/" % (self.cbs_proto, self.cbs_host, self.cbs_port, self.cbs_path)
        self.mds       = "%s://%s:%s/%s" % (self.mds_proto, self.mds_host, self.mds_port, self.mds_path)
        
        # Initialize the error handler
        self.error     = Error(self.cbs, self.log)
        
        # Retrieve core system properties
        self.sys_type  = platform.system()
        self.sys_arch  = platform.machine()
    
        # Log the callback and metadata servers, and machine information
        self.log.info('Using callback server: ' + self.cbs)
        self.log.info('Using metadata server: ' + self.mds)
        self.log.info('Discovered system type: ' + self.sys_type)
        self.log.info('Discovered system architecture: ' + self.sys_arch)
    
        # Linux instances
        if self.sys_type == 'Linux':
            
            # Find the OS type
            self.os_distro = platform.linux_distribution()
            self.os_type   = {'distro': self.os_distro[0],
                              'version': self.os_distro[1]}
            self.log.info('Discovered system OS distribution and version: ' + str(self.os_type))
                
        # Windows instances
        elif self.sys_type == 'Windows':
            
            # Find the windows version
            self.win32   = platform.win32_ver()
            self.os_type = {'distro': self.win32[0],
                            'version': self.win32[1]}
            self.log.info('Discovered system OS distribution and version: ' + str(self.os_type))
            
        # Invalid system type
        else:
            self.error(3, self.sys_type)
    
        # Try to fetch the metadata
        try:    self.meta_data = requests.get(self.mds)
        except: self.error.response(1)
    
        if self.os_type['distro'] == 'CentOS' \
        and re.match('^5\.[0-9]*$', self.os_type['version']):
            self.meta_json = self.meta_data.json
        else:
            self.meta_json = self.meta_data.json()
        self.meta_pass = None
    
        # Log the meta data JSON object
        self.log.info('Retrieved meta data JSON object: ' + str(self.meta_json))
    
    # Generate a random string of optional specified size
    def _rstring(self, size = 12):
        chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
        return ''.join(random.choice(chars) for x in range(size))
    
    # Get the current instance mode
    def get_mode(self):
        cloud_mfh  = open(self.root + '/cloud_mode.ini', 'r')
        cloud_mode = cloud_mfh.read()
        cloud_mfh.close()
        self.log.info('Retrieved cloud_mode marker file value: ' + cloud_mode)
        return cloud_mode
    
    # Set the current instance mode
    def _set_mode(self, cloud_mode):
        self.log.info('Setting cloud_mode marker file value: ' + cloud_mode)
        cloud_mfh  = open(self.root + '/cloud_mode.ini', 'w+')
        cloud_mfh.write(cloud_mode)
        cloud_mfh.close()
      
    # Instance initialization complete
    def init_complete(self):
        self._set_mode('reboot')
        self.log.info('Instance initialization complete, rebooting server')
        os.system('reboot')
      
    # Instance reboot complete
    def reboot_complete(self):
        self.log.info('Instance initialization and reboot complete')
        self._set_mode('complete')
      
    # Generate password hash
    def gen_passwd(self, passwd_text = None):
      if not passwd_text: 
          passwd_text = self._rstring(12)
      passwd_salt = self._rstring(16)
      passwd_hash = crypt.crypt(passwd_text, '$6$' + passwd_salt)
      passwd_obj  = {'clear': passwd_text,
                     'hash': passwd_hash}
      return passwd_obj
      
    # Handle the callback server response
    def handle_response(self, response):
        self.log.info('Retrieved response from callback server: ' + str(response))
                
    # Send the callback response
    def send_callback(self):
        
        # Define the callback parameters
        callback_rsp = {'status': 'success',
                        'type': self.sys_type,
                        'os': "%s %s %s" % (self.os_type['distro'], self.os_type['version'], self.sys_arch),
                        'host': self.meta_json['name'],
                        'uuid': self.meta_json['uuid'],
                        'password': self.passwd,
                        'ip_pub': self.ip_info['pub_addr'],
                        'ip_priv': self.ip_info['priv_addr']}

        # Send the response to the callback handler and store the server response
        server_response = requests.get(self.cbs, params = callback_rsp)
        self.log.info('Sent callback response to server')
        
        # Handle the callback server response
        self.handle_response(server_response)