pool.defaultinstall_role(role='controller', pkg='gawk')
for n in range(0, 10):
  pool.runon_role(role='controller', cmd='. ~/openrc ; nova --debug list 2>&1 | gawk "{ print systime(), \$0; fflush() }"', async=True, timeout=300)
  pool.runon_role(role='controller', cmd='. ~/openrc ; cinder --debug list 2>&1 | gawk "{ print systime(), \$0; fflush() }"', async=True, timeout=300)
  pool.runon_role(role='controller', cmd='. ~/openrc ; keystone --debug user-list 2>&1 | gawk "{ print systime(), \$0; fflush() }"', async=True, timeout=300)
  pool.runon_role(role='controller', cmd='. ~/openrc ; neutron --debug net-list 2>&1 | gawk "{ print systime(), \$0; fflush() }"', async=True, timeout=300)
  pool.runon_role(role='controller', cmd='. ~/openrc ; quantum --debug net-list 2>&1 | gawk "{ print systime(), \$0; fflush() }"', async=True, timeout=300)
  pool.runon_role(role='controller', cmd='. ~/openrc ; glance --debug image-list 2>&1 | gawk "{ print systime(), \$0; fflush() }"', async=True, timeout=300)
  time.sleep(5)

