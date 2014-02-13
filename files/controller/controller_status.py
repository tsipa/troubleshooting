for n in range(0, 30):
  pool.runon_role(role='controller', cmd='nova-manage service list', async=True, timeout=300)
  pool.runon_role(role='controller', cmd='cinder-manage host list', async=True, timeout=300)
  pool.runon_role(role='controller', cmd='neutron agent list', async=True, timeout=300)
  pool.runon_role(role='controller', cmd='quantum agent-list', async=True, timeout=300)
  pool.runon_role(role='controller', cmd='crm status', async=True, timeout=300)
  pool.runon_role(role='controller', cmd='rabbitmqctl cluster_status', async=True, timeout=300)
  pool.runon_role(role='controller', cmd='rabbitmqctl list_queues', async=True, timeout=300)
  time.sleep(5)
