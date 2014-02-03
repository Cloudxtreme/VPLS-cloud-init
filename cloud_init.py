#!/usr/bin/python

# VPLS Cloud Init Python Script
#
# This is a self destructing script that runs on the first boot of an instance
# created in our OpenStack environment. Mainly it is used for setting the root
# password and other first boot tasks, and sending an email summary to the owner
# of the virtual machine.
#
# TODO: Need a way to retrieve the URL of the callback server from the
# instance metadata so its not hard coded into the script.
#
# TODO: Password retrieval isn't working right now, so I have to default to a
# random root password. 
#
# IMPORTANT: This only works for CentOS 6.x now
import requests
import simplejson as json
from lib.root import RootPasswd
from lib.netconf import NetConf
from lib.error import Error

# Callback server/port
cbs = '192.168.213.70:8080'

# Error code handling
err = Error(cbs)

# Metadata API URL and contents
meta_url      = 'http://169.254.169.254/openstack/latest'

# Try to get the meta data content
try:
    meta_data_rsp = requests.get(meta_url + '/meta_data.json')
except:
    err.response(1)
    
# Parse the response string into a JSON object
meta_json     = meta_data_rsp.json()
meta_pass     = None

# Class instances
rp = RootPasswd(meta_pass)
nc = NetConf('eth0', 'eth1', '/etc/sysconfig/network')

# Run the system prep commands
root_passwd = rp.update()
ip_config   = nc.update(meta_json['name'])

# Define the callback parameters
callback_rsp = {'status': 'success',
                'host': meta_json['name'],
                'uuid': meta_json['uuid'],
                'password': root_passwd,
                'ip_pub': ip_config['pub_addr'],
                'ip_priv': ip_config['priv_addr']}

# Send the response to the callback handler and store the server response
server_response = requests.get('http://' + cbs + '/cloud_callback/', params = callback_rsp)