#!/bin/bash

set -x
date
. ~/openrc
for f in `seq 1 10`; do
  nova-manage service list
  cinder-manage host list 
  neutron agent list
  quantum agent-list
  crm status
  rabbitmqctl cluster_status
  rabbitmqctl list_queues
  sleep 5
done
