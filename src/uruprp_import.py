#!BPY
#
# $Id: uruprp_import.py 861 2007-11-05 23:03:39Z trylon $
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

"""
Name: 'PyPRP'
Blender: 237
Group: 'Import'
Submenu: 'Full age (.age)' i_age
Submenu: 'Single prp (.prp)' i_prp
Tooltip: 'GoW PyPRP Importer'
"""

#temporany removed options
#Submenu: 'Raw span (.raw)' i_raw_span

__author__ = "GoW PyPRP Team"
__url__ = ("blender", "elysiun",
"Author's homepage, http://www.guildofwriters.com")
__version__ = "GoW PRP Exporter"

__bpydoc__ = """\
This script attempts to import scenes from the PRP format
used in URU.
"""

import alcconfig
alcconfig.startup()

import Blender, time, sys, os
from os.path import *
from alcresmanager import *
from alcurutypes import *


def import_age(agename,basepath,pagename=None,version=5):
    # Initialize AlcScript
    AlcScript.Init()

    if pagename!=None:
        print "Importing page %s from age %s" %(pagename,agename)
    else:
        print "Importing age %s" %agename
    rmgr=alcResManager(basepath)
    rmgr.preload(None,agename)
#    try:
#        os.mkdir(basepath + "/" + agename)
#    except OSError:
#        pass
    #rmgr.import_book(agename)
    age=rmgr.findAge(agename,1,None,version)
    if age==None:
        raise "Cannot find %s.age on %s" %(agename,basepath)
        
    if age.getSeq() < 100:
        # We are trying to import a cyan age - show a dialog asking the user to agree not to use cyan's IP
        dlg = AgreementDialog()
        result = dlg.Show()
        if result == -1 or result == 0:
            dlg.ShowDeclineInfo()
            raise RuntimeError,"You cannot import a Cyan age without agreeing not to use their material"

    iniobj=alcFindBlenderText("init")
    initxt=age.getInit()
    iniobj.clear()
    iniobj.write(initxt)
    if pagename==None:
        for page in age.pages:
            page.import_all()
    else:
        age.import_page("Textures")
        age.import_page(pagename)

    rmgr.import_book(agename)
    # Write out AlcScript to Blender
    AlcScript.StoreToBlender()

def import_prp(filename,basepath):
    was = basename(filename[:-4])
    w = was.split("_")
    v = was.split("_District_")
    if ((len(v) > 1) and (v[1]!=None)):
        agename=v[0]
        pagename=v[1]
        version=5
    else: 
        agename=w[0]
        pagename=was[len(agename) + 1:]
        version=6
    import_age(agename,basepath,pagename,version)


##def import_raw_mesh(filename):
##    print("Importing %s ..." % filename)
##    buf=file(filename,"rb");
##    span_info=plDrawableSpans();
##    span_info.read(buf)
##    buf.close()
##    span_info.import_all()


def open_file(filename):
    try:
        import psyco
        psyco.profile()
    except ImportError:
        print "Psyco not available to PyPRP..."
    start=time.clock()
    log=ptLog(sys.stdout,filename + ".log","w")
    std=sys.stdout
    sys.stdout=log
    print("Importing %s ..." % filename)
    args = __script__['arg']
    print("Args are %s " % args)
    w = args.split("_")
    print w
    ext="." + w[1]
    basepath = dirname(filename)
    if filename.find(ext,-4) == -1:
        raise RuntimeError,"Unsuported file %s, expecting an %s file" %(filename,ext)
    if w[1]=="age":
        agename = basename(filename[:-4])
        if w[0]=="i":
            import_age(agename,basepath)
        else:
            raise RuntimeError,"Unimplemented option %s" %(args)
    elif w[1]=="prp":
        if w[0]=="i":
            import_prp(filename,basepath)
        else:
            raise RuntimeError,"Unimplemented option %s" %(args)
    else:
        raise RuntimeError,"Unimplemented option %s" %(args)
    stop=time.clock()
    print("done in %.2f seconds" % (stop-start))
    sys.stdout=std
    log.close()


def do_main():
    args = __script__['arg']
    w = args.split("_")
    try:
        fname = "Import " + w[2] +  " ."  + w[1]
    except IndexError:
        fname = "Import . " + w[1]
    Blender.Window.FileSelector(open_file,fname)


#Main code
do_main()

