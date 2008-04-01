#
# $Id: alcmfsgen.py 841 2007-07-25 02:42:46Z Robert The Rebuilder $
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

import os, time, md5, struct
from os.path import *
#from alcwhatdoyousee import *
from alc_hsStream import *
from alcurutypes import *

try:
    import Crypto
    from Crypto.Hash import SHA
    cryptoworks=1
except ImportError:
    cryptoworks=0
    print "WARNING: Python Crypto Toolkit not found!,\
    You need to install it to be able to generate valid manifest files for Alcugs Dataservers"

class mfsfile:
    def __init__(self,name):
        self.name=name
        self.path=""
        self.type="other"
        #base
        #page (path always "")
        #other
        self.date=""
        self.size=0
        self.compressed=0
        self.md5=""
        self.sha1=""
        ##
        self.fullpath=""


class mfs:
    def __init__(self,seq):
        self.files=[]
        self.seq=seq


    def addFile(self,filename):
        fullpath=filename
        filename=basename(filename)
        for f in self.files:
            if f.name==file:
                return
        f=mfsfile(filename)
        f.fullpath=fullpath
        self.files.append(f)


    def update(self):
        for f in self.files:
            ext=f.name[-4:]
            if ext in [".age",".fni",".csv"]:
                f.type="base"
                f.path="dat"
                f.compressed=0
            elif ext in [".prp",]:
                f.type="page"
                f.path=""
                f.compressed=1
            elif ext in [".ogg",".sdl"]:
                f.type="other"
                if ext in [".ogg"]:
                    f.path="sfx"
                elif ext in [".sdl"]:
                    f.path="sdl"
                f.compressed=0
            elif ext in [".py"]:
                f.type="python"
                f.path=""
            status=os.stat(f.fullpath)
            f.size=status.st_size
            d=time.gmtime(status.st_mtime)
            f.date=time.strftime("%d/%m/%Y %H:%M:%S",d)
            f.mtime=status.st_mtime
            #print "Computing checksum for %s" %f.fullpath
            read=file(f.fullpath,"rb")
            md5obj=md5.new(read.read())
            f.md5=md5obj.hexdigest()
            f.md5bin=md5obj.digest()
            del md5obj
            read.seek(0)
            if cryptoworks:
                f.sha1=SHA.new(read.read()).hexdigest()
            else:
                "Cannot compute SHA checksum, Please install the Python Crypto Toolkit"
            read.close()
            del read


    def writexml(self,path):
        xml=file(path,"w")
        xml.write("<?xml version=\"1.0\"?>\n\n<mfs version=\"1\">\n")
        xml.write("  <sequenceprefix>%i</sequenceprefix>\n" % int(self.seq))
        for f in self.files:
            xml.write("  <file>\n")
            xml.write("    <name>%s</name>\n" % f.name)
            xml.write("    <path>%s</path>\n" % f.path)
            xml.write("    <type>%s</type>\n" % f.type)
            xml.write("    <date>%s</date>\n" % f.date)
            xml.write("    <size>%i</size>\n" % int(f.size))
            xml.write("    <compressed>%i</compressed>\n" % f.compressed)
            xml.write("    <md5>%s</md5>\n" % f.md5)
            xml.write("    <sha1>%s</sha1>\n" % f.sha1)
            xml.write("  </file>\n")
        xml.write("</mfs>\n");
        xml.close()


    def writesum(self,path,old_style=0):
        count = 0
        for f in self.files:
            if f.type in ["page"]:
                count=count+1
        sum=Wdys()
        sum.open(path,"wb")
        sum.write(struct.pack("II",count,0))
        for f in self.files:
            if f.type in ["page"]:
                if f.type=="page" and old_style:
                    name=""
                else:
                    name="dat\\"
                name=name + f.name
                str=Ustr(name,5)
                str.write(sum)
                sum.write(f.md5bin)
                sum.write(struct.pack("II",f.mtime,0))
        sum.close()
