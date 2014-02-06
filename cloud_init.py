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

# Get the instance mode
mode = utils.get_mode()

# If initializing the instance
if mode == 'init':
    gpart.extend_root()         # Extend the root partition
    utils.init_complete()       # Set the cloud_mode marker and reboot
    
# If rebooting the node after initialization
if mode == 'reboot':
    gpart.resize_root()         # Resize the new root partition
    rpass.update()              # Set a random root password
    nconf.update()              # Update network configuration
    admin.create_user()         # Create the cloud administrator
    utils.reboot_complete()     # Update the cloud_mode marker
    utils.send_callback()       # Send the callback response