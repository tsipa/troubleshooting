#!/bin/bash

set -x
netstat -an
ip r
ip netns
ifconfig -a

iptables-save

for f in `ip netns` ; do echo "ns ----- $f" ; ip netns exec $f iptables-save ; done

for dev in $(ls /sys/block); do udevadm info --query=property --export --name=${dev}; done
echo "common information about interfaces and links"
for x in `ip a | egrep ": eth[0..1]:" | awk '{print $2}' | sed s/://`; do ethtool $x ; done
for y in `ip a | egrep ": eth[0..1]:" | awk '{print $2}' | sed s/://`; do ethtool -k $y ; done

