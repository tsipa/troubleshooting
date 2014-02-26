needed_files = ['/etc/openvswitch/', '/etc/astute.yaml', '/etc/corosync/', '/var/log/', '/etc/my.cnf', '/etc/mysql/', '/etc/fuel-uuid', '/etc/naily.facts', '/etc/nailgun/', '/etc/naily/', '/etc/haproxy/' ]
for file in needed_files:
  pool.get_fromrole('all', file)
