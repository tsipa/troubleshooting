import re
import os
import commands
import json
import tempfile

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

  def install(self, pkg):
    install_cmd=self.pkglocalprovider() + ' ' + tmp_dir + pkg + '*' + self.getpkgarch() + '*.' + self.getpkgextension()
    if not os.system(install_cmd) == 0:
      print install_cmd, 'failed'


class Buildins():
  def __init__(self):
    self.platform = Platform()
    if os.path.isfile('/etc/fuel-uuid'):
      self.hostname = 'localhost'
    else:
      self.hostname = self.platform.raw_data['hostname']
    print(self.hostname)

  def simplecmd(self, *args):
    print 'going to run', args

class Nodes():
  def __init__(self):
    self.raw_data = json.loads(commands.getoutput('fuel --json node'))
    self.nodes = []
    os.system('cp ' + __file__ + ' ' + tmp_dir)
    for n in self.raw_data:
      self.nodes.append(n['fqdn'])
      print 'scp -r ' + tmp_dir + ' ' + n['fqdn'] + ':' + tmp_dir

#me = Platform()
#me.install("atop")

if len(sys.argv) == 1:
#i'm controller
extract()
pool = Nodes()
print pool.nodes
else:
#i'm target
b = Buildins()
