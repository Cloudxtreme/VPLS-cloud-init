#!/usr/bin/python
import os
import crypt
import string
import random
import requests
import platform
import ConfigParser
from error import Error

# Cloud Init Utilities \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ #
class Utils():
    
    # Class initializer
    def __init__(self):
        
        # Load the configuration file
        self.root      = os.path.abspath(os.path.join(os.path.realpath(__file__), '..', os.pardir))
        self.conf      = ConfigParser.ConfigParser()
        self.conf.read(self.root + '/cloud_init.ini')
        
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
        
        # Root/administrator password
        self.passwd    = None
        
        # Define the callback and metadata server connect strings
        self.cbs       = '%s://%s:%s/%s', self.cbs_proto, self.cbs_host, self.cbs_port, self.cbs_path
        self.mds       = '%s://%s:%s/%s', self.mds_proto, self.mds_host, self.mds_port, self.mds_path
        
        # Initialize the error handler
        self.error     = Error(slef.cbs)
        
        # Retrieve core system properties
        self.sys_type  = platform.system()
    
        # Linux instances
        if self.sys_type == 'Linux':
            
            # Find the OS type
            self.os_distro = platform.linux_distribution()
            self.os_type   = {'distro': self.os_distro[0],
                              'version': self.os_distro[1]}
                
        # Windows instances
        elif self.sys_type == 'Windows':
            
            # Find the windows version
            self.win32   = platform.win32_ver()
            self.os_type = {'distro': self.win32[0],
                            'version': self.win32[1]}
            
        # Invalid system type
        else:
            self.error(3, self.sys_type)
    
        # Try to fetch the metadata
        try:
            self.meta_data = requests.get(self.mds)
            self.meta_json = self.meta_data.json()
            self.meta_pass = None
        except:
            self.error.response(1)
    
    # Generate a random string of optional specified size
    def rstring(self, size = 12):
        chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
        return ''.join(random.choice(chars) for x in range(size))
      
    # Handle the callback server response
    def handle_response(self, response):
        print response
                
    # Send the callback response
    def send_callback(self):
        
        # Define the callback parameters
        callback_rsp = {'status': 'success',
                        'type': self.os_type['distro'] + ' ' + self.os_type['version'],
                        'host': self.meta_json['name'],
                        'uuid': self.meta_json['uuid'],
                        'password': self.passwd,
                        'ip_pub': self.ip_info['pub_addr'],
                        'ip_priv': self.ip_info['priv_addr']}

        # Send the response to the callback handler and store the server response
        server_response = requests.get(self.cbs, params = callback_rsp)
        
        # Handle the callback server response
        self.handle_response(server.response)