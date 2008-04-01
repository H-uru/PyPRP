#
# $Id: alcprpasm.py 874 2007-12-15 21:47:39Z trylon $
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

import dircache
import os
from os.path import *
from binascii import *
import StringIO
from alcurutypes import *
from alcprpfile import *
from alcresmanager import *

def extract(what):
    prp = PrpFile()
    f=file(what,"rb")
    prp.read(f)
    f.close()
    m=basename(what).split(".")
    base = dirname(what)
    if len(base)==0:
        out = m[0]
    else:
        out = base + "/" + m[0]
    print out
    try:
        os.mkdir(out)
    except OSError:
        pass
    meta = file(out + "/" + "meta.dat","w")
    meta.write("agename = %s\n" % str(prp.name))
    meta.write("pagename = %s\n" % str(prp.page))
    meta.write("pagetype = %i\n" % prp.page_type)
    a=struct.pack(">I",prp.page_id)
    b=hexlify(a).upper()
    meta.write("pageid = %s\n" %b)
    meta.close()
    for i in prp.idx:
        a=struct.pack(">H",i.type)
        b=hexlify(a).upper()
        cur = out + "/" + b
        try:
            os.mkdir(cur)
        except OSError:
            pass
        for o in i.objs:
            name = str(o.data.Key.name)
            name=name.replace("*","_")
            name=name.replace("?","_")
            name=name.replace("\\","_")
            name=name.replace("/","_")
            name=name.replace("<","_")
            name=name.replace(">","_")
            name=name.replace(":","_")
            name=name.replace("\"","_")
            name=name.replace("|","_")
            name=name.strip()
            print "Writting %s" %name
            f=file(cur + "/" + name + ".raw","wb")
            o.write(f)
            f.close()


def assemble(what,ia=0,fast=0):
    prp = PrpFile()
    ignore = [0x00,]
    m=basename(what)
    base = dirname(what)
    if len(base)==0:
        out = m
    else:
        out = base + "/" + m
    print out
    meta = file(out + "/" + "meta.dat")
    for line in meta.readlines():
        w = line.strip().split("=")
        x = w[0].strip()
        v = w[1].strip()
        if x.lower()=="agename":
            prp.name.set(v)
        if x.lower()=="pagename":
            prp.page.set(v)
        if x.lower()=="pagetype":
            prp.page_type=int(v)
        if x.lower()=="pageid":
            b=unhexlify(v)
            prp.page_id,=struct.unpack(">I",b)
    meta.close()
    if ia:
        if prp.page_type in (0x04,0x00):
            prp.createSceneNode()
    f=dircache.listdir(out)
    for i in f:
        p=out + "/" + i
        if not isdir(p):
            continue
        b=unhexlify(i)
        a,=struct.unpack(">H",b)
        type=a
        if ia:
            if type in ignore:
                continue
        idx = PrpIndex(prp.page_id,prp.page_type,type)
        idx.parent=prp
        if fast:
            type=0xFFFF
        k=dircache.listdir(p)
        for j in k:
            #print p,j
            if j[-4:]!=".raw":
                continue
            f=file(p + "/" + j,"rb")
            buf=StringIO.StringIO()
            buf.write(f.read())
            f.close()
            size=buf.tell()
            #print size
            buf.seek(0)
            #print prp.page_type
            o = PrpObject(prp.page_id,prp.page_type,type)
            o.parent=idx
            o.read(buf,0,size)
            buf.close()
            idx.objs.append(o)
        prp.idx.append(idx)
    if ia:
        if prp.page_type in (0x04,0x00):
            prp.updateSceneNode()
    buf=file(what + ".prp","wb")
    print "writting %s (please wait several minutes)" %what
    prp.write(buf)
    buf.close()


def extract_prp(path):
    basepath = dirname(path)
    filename = basename(path)
    ext = filename[-4:]
    was = filename[:-4]
    if ext==".age":
        agename=was
        pagename=None
        version=5
    elif ext==".prp":
        w = was.split("_")
        agename = w[0]
        if w[1]=="District":
            pagename=was[len(agename) + 1 + len(w[1]) + 1:]
            version=5
        else:
            pagename=was[len(agename) + 1:]
            version=6
    else:
        raise "Unsupported format %s" %ext
    extract_age(agename,basepath,pagename,version)


def extract_age(agename,basepath,pagename=None,version=5):
    if pagename!=None:
        print "Extracting page %s from age %s" %(pagename,agename)
    else:
        print "Extracting age %s" %agename
    #print basepath
    rmgr=alcResManager(basepath)
    rmgr.setFilesystem()
    rmgr.preload()
    try:
        os.mkdir(basepath + "/" + agename)
    except OSError:
        pass
    rmgr.import_book(agename)
    age=rmgr.findAge(agename,1,None,version)
    if age==None:
        raise "Cannot find %s.age on %s" %(agename,basepath)
    if pagename==None:
        for page in age.pages:
            page.import_all()
    else:
        age.import_page(pagename)
