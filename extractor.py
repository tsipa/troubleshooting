


import base64
for f in basefile.keys():
  fd = open('/tmp/'+f, 'w')
  fd.write(base64.b64decode(basefile[f]))
  fd.close()
