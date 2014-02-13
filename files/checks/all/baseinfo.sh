#!/bin/bash

set -x
date
ohai
dmesg
uname -a
lsmod
rpm -qa
dpkg -l
lsblk
df -h
df -i

free
netstat -an
lsof

ip r
ip netns
ifconfig -a
ovs-vsctl show
ovs-dpctl show


iptables-save

for dev in $(ls /sys/block); do udevadm info --query=property --export --name=${dev}; done
echo "common information about interfaces and links"
for x in `ip a | egrep ": eth[0..1]:" | awk '{print $2}' | sed s/://`; do ethtool $x ; done
for y in `ip a | egrep ": eth[0..1]:" | awk '{print $2}' | sed s/://`; do ethtool -k $y ; done
for u in $(ls /sys/block); do udevadm info --query=property --export --name=${u}; done


for f in `ip netns` ; do echo "ns ----- $f" ; ip netns exec $f iptables-save ; done

for f in `seq 1 300` ; do
  ps awxuf
  netstat -s
  ovs-dpctl dump-flows
  sleep 1
done


