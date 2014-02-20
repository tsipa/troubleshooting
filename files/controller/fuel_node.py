controller_dir = target_dir + '/controller/'
try:
  os.mkdir(controller_dir)
except:
  pass
files = ['/etc/openvswitch/', '/etc/corosync/', '/var/log/', '/etc/my.cnf', '/etc/mysql/', '/etc/fuel-uuid', '/etc/naily.facts', '/etc/nailgun/', '/etc/naily/', '/etc/haproxy/']
for file in files:
  os.system('cp -a ' + file + ' ' + controller_dir)

