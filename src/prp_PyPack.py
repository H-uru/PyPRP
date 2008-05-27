#    Copyright (C) 2008  Guild of Writers PyPRP Project Team
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
#    Please see the file LICENSE for the full license.

import struct, time, glob, os
import os.path
from prp_Types import *

class alcpyfile:
    def __init__(self):
        self.name=""
        self.data=None


    def setName(self,name):
        self.name=name + "c"


    def read(self,buf):
        size, = struct.unpack("I",buf.read(4))
        self.data=cStringIO.StringIO()
        #print size
        self.data.write(buf.read(size))


    def write(self,buf):
        self.data.read()
        buf.write(struct.pack("I",self.data.tell()))
        self.data.seek(0)
        buf.write(self.data.read())


class alcpypack:
    def __init__(self,version=5):
        self.list=[]
        self.version=version


    def read(self,buf):
        num, = struct.unpack("I",buf.read(4))
        for i in range(num):
            name = Ustr()
            name.setType(self.version)
            name.read(buf)
            off, = struct.unpack("I",buf.read(4))
            cat = buf.tell()
            buf.seek(off)
            file = alcpyfile()
            file.setName(str(name))
            print "Reading %s" %str(name)
            file.read(buf)
            buf.seek(cat)
            self.list.append(file)


    def write(self,buf):
        buf.write(struct.pack("I",len(self.list)))
        size=4
        for i in self.list:
            size=size + 4 + len(i.name) + 2
        for i in self.list:
            name = Ustr()
            name.setType(self.version)
            name.set(i.name)
            name.write(buf)
            buf.write(struct.pack("I",size))
            me = buf.tell()
            buf.seek(size)
            i.write(buf)
            size = buf.tell()
            buf.seek(me)


##f = file("python.pak.dec","rb")
##
##pak = alcpypack()
##pak.read(f)
##f.close()
##
##for i in pak.list:
##    print "writting %s" %i.name
##    f = file("out/%s" %i.name,"wb")
##    f.write(struct.pack("I",0x0A0DF23B))
##    f.write(struct.pack("I",time.time()))
##    i.data.seek(0)
##    f.write(i.data.read())
##    f.close()


####out = file("out.pak","wb")
####
####pkg = alcpypack()
####
####for i in glob.glob("newpak/*.pyc"):
####    print "packing %s" %i
####    f = file(i,"rb")
####    f.read(8)
####    buf = cStringIO.StringIO()
####    buf.write(f.read())
####    f.close()
####    pyf = alcpyfile()
####    pyf.data=buf
####    pyf.name=os.path.basename((i[:len(i)-1]))
####    #print pyf.name
####    pkg.list.append(pyf)
####
####pkg.write(out)
####out.close()

