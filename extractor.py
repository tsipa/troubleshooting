


import base64
import tempfile
import os
import re
tmp_dir = '/tmp/troublestack/'
target_dir = tmp_dir + '/target/'
file_dir = tmp_dir + '/files/'
def extract():
  try:
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
    fd = open(tmp_dir + f, 'w')
    fd.write(base64.b64decode(basefile[f]))
    fd.close()
