#!/bin/bash

# Find the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# CentOS 6.x
if [ ! -z "$(cat /etc/issue | grep -e "^CentOS.*6\..*$")" ]; then
	/usr/bin/python $SCRIPT_DIR/cloud_init.py
fi

# CentOS 5.x
if [ ! -z "$(cat /etc/issue | grep -e "^CentOS.*5\..*$")" ]; then
	/usr/bin/python26 $SCRIPT_DIR/cloud_init.py
fi