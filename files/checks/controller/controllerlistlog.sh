#!/bin/bash

set -x
. ~/openrc

for f in `seq 1 10`; do
  nova --debug list 2>&1 | gawk '{ print systime(), $0; fflush() }'
  echo '------------------------------------------------------'
  cinder --debug list 2>&1 | gawk '{ print systime(), $0; fflush() }'
  echo '------------------------------------------------------'
  keystone --debug user-list 2>&1 | gawk '{ print systime(), $0; fflush() }'
  echo '------------------------------------------------------'
  neutron --debug net-list 2>&1 | gawk '{ print systime(), $0; fflush() }'
  echo '------------------------------------------------------'
  quantum --debug net-list 2>&1 | gawk '{ print systime(), $0; fflush() }'
  echo '------------------------------------------------------'
  glance --debug image-list 2>&1 | gawk '{ print systime(), $0; fflush() }'
  echo '------------------------------------------------------'
done

