import re
import os
import commands
import json
import tempfile
import sys
import subprocess
import threading
import signal
import time
import atexit


class Alarm(Exception):
    pass

def alarm_handler(signum, frame):
    raise Alarm

def cleanup(*args):
  #print "Cleaning"
  executor.clean()
  time.sleep(1)
  try:
    pool.clean()
  except:
    pass

signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGHUP, cleanup)
atexit.register(cleanup)

class Executor():
  def __init__(self):
    self.to_wait = {}
    self.to_kill = []

  def clean(self):
    self.check_for_waiting()
    time.sleep(1)
    self.kill_all_killable()

  def check_for_pid(self, pid):
    self.check_all_waiting()
    self.check_all_killed()
    if pid in self.to_wait.keys() + self.to_kill:
      return True
    return False

  def check_all_waiting(self):
    for pid in self.to_wait.keys():
      try:
        os.waitpid(pid,os.WNOHANG)
        os.kill(pid,0)
        if time.time() > self.to_wait[pid]:
          del self.to_wait[pid]
          self.to_kill.append(pid)
          self.kill_single(pid)
      except:
        del self.to_wait[pid]
        

  def check_for_waiting(self):
    #wait while all running processes with limited timeout will end
    #if len(self.to_wait) != 0:
    #  print 'Waiting for pids:', self.to_wait
    while len(self.to_wait) != 0:
      self.check_all_waiting()
      time.sleep(1)

  def kill_all_killable(self):
    #kill all unlimited processes
    for pid in self.to_kill:
      self.kill_single_term(pid)
    time.sleep(1)
    self.check_all_killed()
    for pid in self.to_kill:
      self.kill_single_kill(pid)
    time.sleep(1)
    self.check_all_killed()

  def kill_single(self,pid):
    self.kill_single_term(pid)
    time.sleep(1)
    self.check_all_killed()
    self.kill_single_kill(pid)
    time.sleep(1)
    self.check_all_killed()

  def kill_single_term(self, pid):
    try:
      os.killpg(pid, signal.SIGTERM)
    except:
      pass

  def check_all_killed(self):
    for pid in self.to_kill:
      try:
        os.waitpid(pid,os.WNOHANG)
        os.kill(pid,0)
      except:
        self.to_kill.remove(pid)
        pass

  def kill_single_kill(self, pid):
    try:
      os.killpg(pid, signal.SIGKILL)
    except:
      pass

  def run_cmd(self, cmd, timeout=0, logged=True, async=False, setsid=False):
    #print "going to run", cmd, "with timeout", timeout, " async =", async, " logged =", logged
    if async:
      pid = os.fork()
      if pid != 0:
        if timeout != 0:
          #print "Will wait for pid", pid, "for", timeout
          self.to_wait[pid] = time.time() + int(timeout) + 10
        else:
          self.to_kill.append(pid)
        return pid
    if (async and pid == 0) or not async:
      if async:
        self.to_wait = {}
        self.to_kill = []
        os.setsid()

      logfile = re.sub('[^a-zA-Z0-9]', '_', cmd)
      if logged:
        n = 0
        while os.path.isfile(target_dir + logfile + str(n)):
          n = n + 1
        logfd = open(target_dir + logfile + str(n), 'w')
      else:
        logfd = open('/dev/null', 'w')
      if (not async) and (not setsid):
        running = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=logfd, shell=True, preexec_fn=os.setsid)
      else:
        running = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=logfd, shell=True, preexec_fn=os.setpgrp)
      subpid = running.pid
      if int(timeout) == 0: 
        #print "Will kill subpid", subpid
        self.to_kill.append(subpid)
      else:
        #print "Will wait for subpid", subpid, "for", timeout
        self.to_wait[subpid] = time.time() + int(timeout) + 10
      signal.signal(signal.SIGALRM, alarm_handler)
      signal.alarm(int(timeout))
      try:
        errcode = running.wait()
        logfd.write(str(cmd) + ' exit with ' + str(errcode))
      except Alarm:
        logfd.write(str(cmd) + ' exceed timeout ' + str(timeout))
        os.killpg(subpid, signal.SIGTERM)
        signal.alarm(10)
        try:
          running.wait()
        except Alarm:
          os.killpg(subpid, signal.SIGKILL)
          logfd.write(str(cmd) + ' was killed with -9')
        except OSError:
          pass
      except OSError:
        pass

      logfd.close()
      signal.alarm(0)
      if timeout == 0:
        self.to_kill.remove(subpid)
      else:
        del self.to_wait[subpid]
      if async:
        os._exit(0)


class Platform():
  def __init__(self):
    if not os.system('gem list | grep ohai &>/dev/null') == 0 and not os.system('gem install ohai') == 0 and not os.system('gem install /var/www/nailgun/gems/gems/ohai*.gem') == 0:
      exit(1)
    self.raw_data = json.loads(commands.getoutput('ohai'))

  def pkglocalprovider(self):
    if self.getfamily() == "debian":
      return "dpkg -i"
    elif self.getfamily() == "redhat":
      return "rpm -ivh"

  def pkgdefaultprovider(self):
    if self.getfamily() == "debian":
      return "apt-get -y --assume-yes install"
    elif self.getfamily() == "redhat":
      return "yum -y install"
  
  def getpkgarch(self):
    if re.search('64', self.raw_data['kernel']['machine'], re.IGNORECASE):
      if self.getfamily() == "debian":
        return "amd64"
      elif self.getfamily() == "redhat":
        return "x86_64"
    elif re.search('i[0-9]86', self.raw_data['kernel']['machine'], re.IGNORECASE):
      if self.getfamily() == "debian":
        return "i686"
      elif self.getfamily() == "redhat":
        return "i386"

  def getpkgextension(self):
    if self.getfamily() == "debian":
      return "deb"
    elif self.getfamily() == "redhat":
      return "rpm" 

  def getfamily(self):
    if re.search('ubuntu', self.raw_data['platform'], re.IGNORECASE) or re.search('debian', self.raw_data['platform'], re.IGNORECASE) or re.search('debian', self.raw_data['platform_family'], re.IGNORECASE):
      return "debian"
    elif re.search('centos', self.raw_data['platform'], re.IGNORECASE) or re.search('redhat', self.raw_data['platform'], re.IGNORECASE) or re.search('rhel', self.raw_data['platform_family'], re.IGNORECASE):
      return "redhat"
    else:
      return "debian"

  def localinstall(self, pkg):
    install_cmd=self.pkglocalprovider() + ' ' + file_dir + pkg + '*' + self.getpkgarch() + '*.' + self.getpkgextension()
    os.system(install_cmd)

  def defaultinstall(self, pkg):
    install_cmd=self.pkgdefaultprovider() + ' ' + pkg
    os.system(install_cmd)


class Buildins():
  def __init__(self, executor):
    self.platform = Platform()
    self.executor = executor
    if os.path.isfile('/etc/fuel-uuid'):
      self.hostname = 'localhost'
    else:
      self.hostname = self.platform.raw_data['hostname']
    #print(self.hostname)

  def simplecmd(self, timeout, cmd):
    self.executor.run_cmd(cmd, timeout=int(timeout), setsid=True)

  def localinstall(self, pkg):
    self.platform.localinstall(pkg)

  def defaultinstall(self, pkg):
    self.platform.defaultinstall(pkg)


class Nodes():
  def __init__(self, executor):
    self.raw_data = json.loads(commands.getoutput('fuel --json node'))
    self.nodes = []
    self.roles = []
    self.executor = executor
    # i dunno how to do it properly, but when __del__ is executed there is no global vars and functions
    self.tmp_dir = tmp_dir
    self.target_dir = target_dir
    os.system('cp ' + __file__ + ' ' + file_dir)
    for n in self.raw_data:
      if n['fqdn'] != None:
        self.nodes.append(n['fqdn'].split('.')[0])
      else:
        self.nodes.append(n['ip'])
      for r in n['roles']:
        if not r in self.roles:
          self.roles.append(r)
      #distribute self and mine data
      os.system('scp -q -o "StrictHostKeyChecking no" -r ' + self.tmp_dir + ' ' + n['fqdn'] + ':' + re.sub('[^/]*/$','',self.tmp_dir))

  def clean(self):
    #gather all logs from all nodes
    for n in self.nodes:
      #print "Cleaning", n
      self.get_fromrole('all',self.target_dir)
      os.system('ssh -t -o "StrictHostKeyChecking no" ' + n + ' rm -rf ' + self.tmp_dir)
    ts = time.time()
    print 'Result will be available at /tmp/troublestack_' + str(ts) + '.tar.bz2'
    os.system('tar cjf /tmp/troublestack_' + str(ts) + '.tar.bz2 ' + self.target_dir)
    os.system('rm -rf ' + self.tmp_dir)

  def runon_role(self, cmd, role='all', async=False, timeout=120):
    nodes = self.role2nodes(role)
    self.runon_list(nodes=nodes,cmd=cmd,async=async,timeout=timeout)

  def _simplecmd(self, node, cmd, async=False, timeout=120):
    torun = 'ssh -t -o "StrictHostKeyChecking no" ' + node + ' \'' + file_dir + __file__ + ' simplecmd ' + str(timeout) + ' "' + cmd + '"\''
    if timeout == 0:
      return self.executor.run_cmd(torun, timeout=timeout, logged=True, async=async)
    else:
      return self.executor.run_cmd(torun, timeout=timeout + 10, logged=True, async=async)

  def _waitpids(self, pids):
    while len(pids) != 0:
      for pid in pids:
        if not self.executor.check_for_pid(pid):
          pids.remove(pid)
      time.sleep(1)

  def _localinstall(self, node, pkg, async=False):
    torun = 'ssh -t -o "StrictHostKeyChecking no" ' + node + ' \'' + file_dir + __file__ + ' localinstall ' + ' "' + pkg + '"\''
    return self.executor.run_cmd(torun, logged=True, async=async)

  def _defaultinstall(self, node, pkg, async=False):
    torun = 'ssh -t -o "StrictHostKeyChecking no" ' + node + ' \'' + file_dir + __file__ + ' defaultinstall ' + ' "' + pkg + '"\''
    return self.executor.run_cmd(torun, logged=True, async=async)

  def runon_node(self, node, cmd, async=False, timeout=120):
    if not node in self.nodes:
      return False
    else:
      self._simplecmd(node, cmd, async=async, timeout=timeout)

  def runon_list(self, nodes, cmd, async=False, timeout=120):
    pids = []
    for node in nodes:
      pids.append(self._simplecmd(node, cmd, async=True, timeout=120))
    if not async:
      #we have to wait when all process will be complete
      self._waitpids(pids)

  def localinstall_role(self, role, pkg):
    pids = []
    nodes = self.role2nodes(role)
    for node in nodes:
      pids.append(self._localinstall(node, pkg, async=True))
    self._waitpids(pids)

  def defaultinstall_role(self, role, pkg):
    pids = []
    nodes = self.role2nodes(role)
    for node in nodes:
      pids.append(self._defaultinstall(node, pkg, async=True))
    self._waitpids(pids)

  def localinstall(self, node, pkg):
    if not node in self.nodes:
      return False
    else:
      self._localinstall(node, pkg, async=False)

  def defaultinstall(self, node, pkg):
    if not node in self.nodes:
      return False
    else:
      self._defaultinstall(node, pkg, async=False)

  def role2nodes(self, role):
    nodes = []
    for n in self.raw_data:
      if role in n['roles'] or role == 'all':
        if n['fqdn'] != None:
          nodes.append(n['fqdn'].split('.')[0])
        else:
          nodes.append(n['ip'])
    return nodes
        

  def run_one2one(self, cmd_from, cmd_to, role_from='all', role_to='all', async=False, timeout=120):
    #will run command cmd_from on each node from role_from role with $1 param set to each node from role role_to and on each node from role_from with $1 set to paired node
    #e.g. run_one2one(cmd_from='ping',cmd_to='tcpdump -n -i any icmp and host', role_from='all',role_to='all',timeout=60)

    pids = []
    nodes_from = self.role2nodes(role_from)
    nodes_to = self.role2nodes(role_to)
    for node_from in nodes_from:
      for node_to in nodes_to:
        if node_to == node_from:
          continue
        cmd_to_run = cmd_to + ' ' + node_from
        cmd_from_run = cmd_from + ' ' + node_to
        pids.append(self._simplecmd(node_from, cmd_from_run, async=True, timeout=timeout))
        pids.append(self._simplecmd(node_to, cmd_to_run, async=True, timeout=timeout))
      if not async:
        self._waitpids(pids)

  def get_fromnode(self, node, target, async=False):
    local_target = re.sub('[^a-zA-Z0-9]', '_', target)
    try:
      os.mkdir(target_dir + '/' + node)
    except:
      pass
    return self.executor.run_cmd('scp -q -o "StrictHostKeyChecking no" -r ' + node + ':' + target + ' ' + target_dir + '/' + node + '/' + local_target, async=async, timeout=0, logged=True )

  def get_fromrole(self, role, target):
    pids = []
    nodes = self.role2nodes(role)
    for node in nodes:
      pids.append(self.get_fromnode(node,target,async=True))
    self._waitpids(pids)



def testpool(pool):
  #sync
  ##timeout 0
  pool.runon_node(node='node-9', cmd="sleep 10", timeout=0, async=False)
  ##timeout > sleep
  pool.runon_node(node='node-9', cmd="sleep 5", timeout=999, async=False)
  ##timeout < sleep
  pool.runon_node(node='node-9', cmd="sleep 999", timeout=5, async=False)

  #async
  ##timeout 0
  pool.runon_node(node='node-9', cmd="sleep 10", timeout=0, async=True)
  ##timeout > sleep
  pool.runon_node(node='node-9', cmd="sleep 5", timeout=999, async=True)
  ##timeout < sleep
  pool.runon_node(node='node-9', cmd="sleep 999", timeout=5, async=True)

  #buildins
  pool.localinstall(node='node-9', pkg='atop')
  pool.defaultinstall(node='node-9', pkg='tcpdump')

  ##one2one with timeout and output
  pool.run_one2one(cmd_from='ping',cmd_to='tcpdump -n -i any host', role_from='all',role_to='all',timeout=30)
  ##one2one with timeout > sleep
  pool.run_one2one(cmd_from='sleep 10 ; echo',cmd_to='sleep 15; echo', role_from='all',role_to='all',timeout=999)
  ##one2one with timeout < sleep
  pool.run_one2one(cmd_from='sleep 999 ; echo',cmd_to='sleep 999; echo', role_from='all',role_to='all',timeout=30)

  #getfromrole
  pool.get_fromrole('all','/etc/hosts')

executor = Executor()

if len(sys.argv) == 1:
#i'm controller
  extract()
  pool = Nodes(executor)
  #testpool(pool)
  #sys.exit(0)

  contoller_mod_dir = file_dir + '/controller/'
  for file in os.listdir(contoller_mod_dir):
    execfile(contoller_mod_dir+file)

  roles_dir = file_dir + '/checks/'
  for role in os.listdir(roles_dir):
    if not os.path.isdir(roles_dir + '/' + role):
      continue
    for file in os.listdir(roles_dir + '/' + role):
      torun = roles_dir + '/' + role + '/' + file
      pool.runon_role(role=role, cmd=torun, async=False, timeout=900)

  #pool.localinstall(node='node-9', pkg='atop')
  #pool.defaultinstall(node='node-9', pkg='tcpdump')
  #pool.localinstall(node='node-9', pkg='atop')
  #pool.runon_role(role='all', cmd='atop -w ' + target_dir + '/atop.log 1 500', async=True, timeout=600, logged=False)
  #pool.runon_list(nodes=[ 'node-9', 'node-10' ], cmd="tcpdump -n -i any", timeout=10, async=True)
  #pool.get_fromnode('node-9', '/etc/hosts')
  #pool.get_fromrole('all', '/tmp')
else:
#i'm target
  b = Buildins(executor)
  #print sys.argv
  #call = getattr(b,sys.argv[1])
  #import pdb; pdb.set_trace()
  #call(sys.argv[2:])
  if sys.argv[1] == 'simplecmd':
    b.simplecmd(sys.argv[2],sys.argv[3])
  if sys.argv[1] == 'localinstall':
    b.localinstall(sys.argv[2])
  if sys.argv[1] == 'defaultinstall':
    b.defaultinstall(sys.argv[2])

sys.exit()
