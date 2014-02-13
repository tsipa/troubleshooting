#!/bin/bash

set -x
date
ohai
dmesg
uname -a
lsmod
rpm -qa
dpkg -l
free

