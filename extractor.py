


import base64
import tempfile
import os
import re
tmp_dir = '/tmp/troublestack/'
target_dir = tmp_dir + '/target/'
file_dir = tmp_dir + '/files/'
def extract():
  try:
    os.system('rm -rf ' + tmp_dir)
    os.mkdir(tmp_dir)
  except:
    pass
  try:
    os.mkdir(target_dir)
  except:
    pass
  for f in basefile.keys():
    dir = tmp_dir + re.sub('[^/]*$', '', f)
    try:
      os.makedirs(dir)
    except:
      pass
    fd = os.fdopen(os.open(tmp_dir + f, os.O_WRONLY | os.O_CREAT, int(basefile[f]['mode'], 8)), 'w')
    fd.write(base64.b64decode(basefile[f]['content']))
    fd.close()
