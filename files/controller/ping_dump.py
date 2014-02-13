pool.defaultinstall_role(role='all', pkg='tcpdump')
pool.run_one2one(cmd_from='ping', cmd_to='tcpdump -n -i any host', role_from='all',role_to='all',timeout=60, async=True)
