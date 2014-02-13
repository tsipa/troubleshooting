pool.localinstall_role(role='all', pkg='atop')
pool.runon_role(role='all', cmd='atop -w ' + target_dir + '/atop.log 1 500', async=True, timeout=600)
