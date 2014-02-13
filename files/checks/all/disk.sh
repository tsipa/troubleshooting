#!/bin/bash

df -h
df -i


lsof

for u in $(ls /sys/block); do udevadm info --query=property --export --name=${u}; done

