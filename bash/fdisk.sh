#!/bin/bash
DEVICE="$1"
PARTITION="$2"

# Get the maximum partition size
MAX_BLOCKS="$(fdisk -l /dev/vda | grep heads | sed "s/^.*[ ]\([0-9]*\)[ ]cylinders.*$/\1/g")"

# Resize the partition to max blocks
fdisk $DEVICE <<EOF
d
n
p
1
1
$MAX_BLOCKS
w
EOF