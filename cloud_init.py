#!/usr/bin/python

# VPLS Cloud Init Python Script
#
# This is a self destructing script that runs on the first boot of an instance
# created in our OpenStack environment. Mainly it is used for setting the root
# password and other first boot tasks, and sending an email summary to the owner
# of the virtual machine.
#
# TODO: Need a way to retrieve the URL of the callback server from the
# instance metadata so its not hard coded into the script. Best thing I have so
# far is a config file outside of Python scripts read at runtime.
#
# TODO: Password retrieval isn't working right now, so I have to default to a
# random root password. 
#
# IMPORTANT: This only works for CentOS 6.x now
from lib.utils import Utils
from lib.root import RootPasswd
from lib.netconf import NetConf
from lib.admin import CloudAdmin
from lib.growpart import GrowPart

# Initialize the cloud_init classes
utils = Utils()
admin = CloudAdmin(utils)
nconf = NetConf(utils)
gpart = GrowPart(utils)
rpass = RootPasswd(utils)

# Set the root password
rpass.update()

# Set the network configuration
nconf.update()

# Set up the cloud administrator
admin.create_user()

# Grow the root partition
gpart.extend_root()

# Send the callback response
utils.send_callback()