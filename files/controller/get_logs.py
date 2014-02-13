needed_files = ['/etc/openvswitch/', '/etc/nova/', '/etc/cinder/', '/etc/quantum/', '/etc/neutron/', '/etc/corosync/', '/var/log/' ]
for file in needed_files:
  pool.get_fromrole('all', file)
