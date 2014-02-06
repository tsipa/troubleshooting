


import base64
import tempfile
import os
tmp_dir = '/tmp/troublestack/'
target_dir = tmp_dir+'/target/'
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
    fd = open(tmp_dir + f, 'w')
    fd.write(base64.b64decode(basefile[f]))
    fd.close()
