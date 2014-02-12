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
for f in `ip netns` ; do echo "ns ----- $f" ; ip netns exec $f iptables-save ; done

for f in `seq 1 300` ; do
  ps awxuf
  netstat -s
  ovs-dpctl dump-flows
  sleep 1
done


