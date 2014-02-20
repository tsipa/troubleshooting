needed_files = ['/etc/nova/', '/etc/cinder/', '/etc/quantum/', '/etc/neutron/', '/etc/ceilometer/', '/etc/heat/', '/etc/swift/', '/etc/murano/', '/etc/ceph/', '/etc/keystone/', '/etc/openstack-dashboard/' ]
for file in needed_files:
  pool.get_fromrole('all', file)

