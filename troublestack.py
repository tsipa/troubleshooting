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

class Alarm(Exception):
    pass

def alarm_handler(signum, frame):
    raise Alarm

def run_cmd(cmd, timeout=0, logged=True, async=False):
  if async:
    pid = os.fork()
  if (async and pid == 0) or not async:
    logfile = re.sub('[^a-zA-Z0-9]', '_', cmd)
    if logged:
      logfd = open(target_dir + logfile, 'w')
    else:
      logfd = open('/dev/null', 'w')
    print "going to run", cmd, "with timeout", timeout, " async =", async, " logged =", logged
    running = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=logfd, shell=True, preexec_fn=os.setsid)
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(int(timeout))
    try:
      errcode = running.wait()
      signal.alarm(0)
      logfd.write(str(cmd) + ' exit with ' + str(errcode))
    except Alarm:
      logfd.write(str(cmd) + ' exceed timeout ' + str(timeout))
      os.killpg(running.pid, signal.SIGTERM)
      signal.alarm(10)
      try:
        running.wait()
        signal.alarm(0)
      except Alarm:
        os.killpg(running.pid, signal.SIGKILL)
        logfd.write(str(cmd) + ' was killed with -9')
        signal.alarm(0)
    logfd.close()
    if async:
      os._exit(0)
  else:
    return pid


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
    if not os.system(install_cmd) == 0:
      print install_cmd, 'failed'

  def defaultinstall(self, pkg):
    install_cmd=self.pkgdefaultprovider() + ' ' + pkg
    if not os.system(install_cmd) == 0:
      print install_cmd, 'failed'


class Buildins():
  def __init__(self):
    self.platform = Platform()
    if os.path.isfile('/etc/fuel-uuid'):
      self.hostname = 'localhost'
    else:
      self.hostname = self.platform.raw_data['hostname']
    #print(self.hostname)

  def simplecmd(self, timeout, cmd):
    run_cmd(cmd, timeout=timeout)

  def localinstall(self, pkg):
    self.platform.localinstall(pkg)

  def defaultinstall(self, pkg):
    self.platform.defaultinstall(pkg)


class Nodes():
  def __init__(self):
    self.raw_data = json.loads(commands.getoutput('fuel --json node'))
    self.nodes = []
    self.roles = []
    self.to_wait = {}
    self.to_kill = []
    # i dunno how to do it properly, but when __del__ is executed there is no global vars and functions
    self.tmp_dir = tmp_dir
    os.system('cp ' + __file__ + ' ' + file_dir)
    for n in self.raw_data:
      self.nodes.append(n['fqdn'].split('.')[0])
      for r in n['roles']:
        if not r in self.roles:
          self.roles.append(r)
      #distribute self and mine data
      os.system('scp -q -o "StrictHostKeyChecking no" -r ' + self.tmp_dir + ' ' + n['fqdn'] + ':' + re.sub('[^/]*/$','',self.tmp_dir))

  def __del__(self):

    #wait while all running processes with limited timeout will end
    if len(self.to_wait) != 0:
      print 'Waiting for pids:', self.to_wait
    while len(self.to_wait) != 0:
      for pid in self.to_wait.keys():
        try:
          os.waitpid(pid,os.WNOHANG)
          os.kill(pid,0)
          if time.time() > self.to_wait[pid]:
            del self.to_wait.pop[pid]
            self.to_kill.append(pid)
        except:
          del self.to_wait[pid]
      time.sleep(1)

    #kill all unlimited processes
    print 'Going to kill with SIGTERM pids:', self.to_kill
    for pid in self.to_kill:
      try:
        print "killing", pid
        os.killpg(pid, signal.SIGTERM)
      except:
        pass

    #kill all processes forcefully
    time.sleep(5)
    for pid in self.to_kill:
      try:
        print "getting", pid
        os.waitpid(pid,os.WNOHANG)
        os.kill(pid,0)
        print "got", pid
      except:
        self.to_kill.remove(pid)
        pass

    print 'Going to kill with SIGKILL pids:', self.to_kill
    for pid in self.to_kill:
      try:
        os.killpg(pid, signal.SIGKILL)
      except:
        pass
    

    #gather all logs from all nodes
    #for n in self.nodes:
    #  os.system('ssh -o "StrictHostKeyChecking no" ' + n + ' rm -rf ' + self.tmp_dir)


  def runon_roles(self, cmd, role='ALL', async=False, timeout=120):
    pass

  def runon_node(self, node, cmd, async=False, timeout=120):
    if not node in self.nodes:
      return False
    else:
      if timeout == 0:
        pid = run_cmd('ssh -o "StrictHostKeyChecking no" ' + node + ' \'' + file_dir + __file__ + ' simplecmd ' + str(timeout) + ' "' + cmd + '"\'', timeout=timeout, logged=False, async=async)
        if async:
          self.to_kill.append(pid)
      else:
        pid = run_cmd('ssh -o "StrictHostKeyChecking no" ' + node + ' \'' + file_dir + __file__ + ' simplecmd ' + str(timeout) + ' "' + cmd + '"\'', timeout=timeout + 10, logged=False, async=async)
        if async:
          print "cmd =",cmd,"pid =",pid,"time =",time.time() + timeout + 10
          self.to_wait[pid] = time.time() + timeout + 10

  def localinstall(self, node, pkg):
    if not node in self.nodes:
      return False
    else:
      run_cmd('ssh -o "StrictHostKeyChecking no" ' + node + ' \'' + file_dir + __file__ + ' localinstall ' + ' "' + pkg + '"\'', logged=False)

  def defaultinstall(self, node, pkg):
    if not node in self.nodes:
      return False
    else:
      run_cmd('ssh -o "StrictHostKeyChecking no" ' + node + ' \'' + file_dir + __file__ + ' defaultinstall ' + ' "' + pkg + '"\'', logged=False)

  def run_one2one(self, cmd_from, cmd_to, role_from='ALL', role_to='ALL', async=False, timeout=120):
    print "lol"

  def run_one2any(self, cmd_from, cmd_to, role_from='ALL', role_to='ALL', async=False, timeout=120):
    print "lol"

  def get_fromnode(self, node, target):
    pass

  def get_fromrole(self, role, target):
    pass


#me = Platform()
#me.localinstall("atop")

if len(sys.argv) == 1:
#i'm controller
  extract()
  pool = Nodes()
  pool.defaultinstall(node='node-9', pkg='tcpdump')
  pool.localinstall(node='node-9', pkg='atop')
  pool.runon_node(node='node-9', cmd="tcpdump -n -i any", timeout=0, async=True)
else:
#i'm target
  b = Buildins()
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
