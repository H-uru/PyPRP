#
# $Id: alcm5crypt.py 539 2006-07-19 17:17:06Z Robert The Rebuilder $
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

try:
    import Crypto
    from Crypto.Cipher import AES
    cryptoworks=1
except ImportError:
    cryptoworks=0
    print "WARNING: Python Crypto Toolkit not found!, support for Myst 5 files is disabled!!"

import struct, cStringIO, glob

class NotM5Crypt(Exception):
    def __init__(self,val):
        pass


class M5Crypt:
    def __init__(self):
        self.buf=""
        self.size=0
        self.off=0
        self.name=""
        self.mode="r"
        key1 = 0xFC2C6B86L
        key2 = 0x952E7BDAL
        key3 = 0xF1713EE8L
        key4 = 0xC7410A13L
        xorkey = 0xCF092676L
        key1 = key1 ^ xorkey
        key2 = key2 ^ xorkey
        key3 = key3 ^ xorkey
        key4 = key4 ^ xorkey
        self.key = struct.pack("IIII",key1,key2,key3,key4)


    def open(self,name,mode="r"):
        if not cryptoworks:
            raise NotM5Crypt
        if mode=="r" or mode=="rb":
            self.mode="r"
            f=file(name,"rb")
            self.buf=cStringIO.StringIO()
            magic, self.size = struct.unpack("II",f.read(8))
            if magic!=0x0D874288:
                f.close()
                raise NotM5Crypt, "That is not a Myst5 encrypted file!"
            off=0
            cb = AES.new(self.key)
            out = cb.decrypt(f.read())
            self.buf.write(out[:self.size])
            off=0
            self.buf.seek(0)
            f.close()
        elif mode=="w" or mode=="wb":
            self.mode="w"
            self.name=name
            self.buf=cStringIO.StringIO()
        else:
            print "Unsuported file mode!"
            raise RuntimeError


    def read(self,size=0):
        if size<=0:
            size=self.size-self.off
        self.off+=size
        if self.off>self.size:
            size-=self.off-self.size
            self.off=self.size
        if size<=0:
            return ""
        return self.buf.read(size)

    def write(self,str):
        self.buf.write(str)
        self.size+=len(str)
        pass

    def flush(self):
        pass

    def close(self):
        if self.mode=="w":
            f=file(self.name,"wb")
            f.write(struct.pack("II",0x0D874288,self.size))
            off=0
            cb = AES.new(self.key)
            for i in range(16-(self.size % 16)):
                self.buf.write(struct.pack("B",0))
            self.buf.seek(0)
            xout = cb.encrypt(self.buf.read())
            f.write(xout)
            self.buf.close()
            f.close()
        else:
            self.buf.close()


def m5decrypt(what):
    magic, size = struct.unpack("II",what.read(8))
    if magic!=0x0D874288:
        raise "That is not a Myst5 encrypted file!"
    key1 = 0xFC2C6B86L
    key2 = 0x952E7BDAL
    key3 = 0xF1713EE8L
    key4 = 0xC7410A13L
    xorkey = 0xCF092676L
    key1 = key1 ^ xorkey
    key2 = key2 ^ xorkey
    key3 = key3 ^ xorkey
    key4 = key4 ^ xorkey
    self.key = struct.pack("IIII",key1,key2,key3,key4)
    cb = AES.new(self.key)
    out = cb.decrypt(what.read())
    return out[:size]


def m5crypt(what,out):
    what.read()
    size = what.tell()
    out.write(struct.pack("II",0x0D874288,size))
    key1 = 0xFC2C6B86L
    key2 = 0x952E7BDAL
    key3 = 0xF1713EE8L
    key4 = 0xC7410A13L
    xorkey = 0xCF092676L
    key1 = key1 ^ xorkey
    key2 = key2 ^ xorkey
    key3 = key3 ^ xorkey
    key4 = key4 ^ xorkey
    self.key = struct.pack("IIII",key1,key2,key3,key4)
    cb = AES.new(self.key)
    for i in range(16-(size % 16)):
        what.write(struct.pack("B",0))
    what.seek(0)
    xout = cb.encrypt(what.read())
    out.write(xout)


##input = glob.glob("*.sdl") + glob.glob("*.node") + glob.glob("*.age") + glob.glob("*.fni") + glob.glob("*.sub") + glob.glob("*.pak")
##
##for infile in input:
##
##    f = file(infile,"rb")
##    out=m5decrypt(f)
##    f.close()
##
##    f2 = file(infile + ".dec","wb")
##    f2.write(out)
##    f2.close()


##input = glob.glob("*.sdl") + glob.glob("*.node") + glob.glob("*.age") + glob.glob("*.fni") + glob.glob("*.sub") + glob.glob("*.pak")
##
##for infile in input:
##    f=M5Crypt()
##    f.open(infile,"r")
##    
##    f2 = file(infile + ".dec","wb")
##    f2.write(f.read())
##    f.close()
##    f2.close()

##
##    f = file(infile,"rb")
##    out=m5decrypt(f)
##    f.close()
##
##    f2 = file(infile + ".dec","wb")
##    f2.write(out)
##    f2.close()

##f = file("out.pak","rb")
##f2 = file("out2.pak","wb")
##
##f3=cStringIO.StringIO()
##f3.write(f.read())
##f.close()
##
##m5crypt(f3,f2)
##
##f3.close()
##f2.close()
