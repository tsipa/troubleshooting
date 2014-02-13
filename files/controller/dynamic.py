for n in range(0, 30):
  pool.runon_role(role='all', cmd='ps awxuf', async=True, timeout=300)
  pool.runon_role(role='all', cmd='netstat -s', async=True, timeout=300)
  pool.runon_role(role='all', cmd='ovs-dpctl dump-flows', async=True, timeout=300)
  time.sleep(5)
