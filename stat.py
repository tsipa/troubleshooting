#!/usr/bin/python

import os, sys, getopt
from stat import *

#print sys.argv
print oct(os.stat(sys.argv[1])[ST_MODE])[-3:]
