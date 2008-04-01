#
# $Id: alcprpparse.py 874 2007-12-15 21:47:39Z trylon $
#
#    Copyright (C) 2005-2008  Alcugs PyPRP Project Team and 2008 GoW PyPRP Project Team
#    See the file AUTHORS for more info about the team
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    Please see the file COPYING for the full license.
#    Please see the file DISCLAIMER for more details, before doing nothing.
#

import time, sys, glob
from os.path import *
from alcurutypes import *
from alcspecialobjs import *
from alcprpfile import *
from alcprpasm import *
from alcresmanager import *
import shutil

def parse_prp(filename):
    log=ptLog(sys.stdout,filename + ".log","w")
    std=sys.stdout
    sys.stdout=log
    print("Parsing %s ..." % filename)
    basepath = dirname(filename)
    prp = PrpFile()
    f=file(filename,"rb")
    prp.read(f)
    f.close()
    del prp
    sys.stdout=std
    log.close()


def my_extract_prp(filename):
    log=ptLog(sys.stdout,filename + ".log","w")
    std=sys.stdout
    sys.stdout=log
    print("Extracting %s ..." % filename)
    extract_prp(filename)
    sys.stdout=std
    log.close()

#Main Code
for a in glob.glob("*.prp"):
    parse_prp(a)

