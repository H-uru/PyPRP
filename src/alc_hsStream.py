#
# $Id: al_hsStream.py 431 2006-04-02 02:10:02Z AdamJohnso $
#
#    Copyright (C) 2005-2006  Alcugs pyprp Project Team
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
    import Blender
except ImportError:
    pass

try:
    import Crypto
    from Crypto.Cipher import AES
    cryptoworks=1
except ImportError:
    cryptoworks=0
    print "WARNING: Python Crypto Toolkit not found!, support for Myst 5 files is disabled!!"

import struct, cStringIO, glob
from alcurutypes import *

class hsStream:
    def __init__(self,fl,mode="rb"):
        self.file = file(fl,mode)
        self.fs = None
        if (mode=="rb"):
            self.fs = cStringIO.StringIO(self.file.read())
            self.file.close()
        elif (mode=="wb"):
            self.fs = self.file
    
    #-Read Functions-#
    def ReadBool(self):
        data, = struct.unpack("<B",self.fs.read(1))
        return bool(data)
    
    
    def ReadSignedByte(self):
        data, = struct.unpack("<b",self.fs.read(1))
        return data

    def ReadByte(self):
        data, = struct.unpack("<B",self.fs.read(1))
        return data
    
    
    def ReadSafeString(self,ver=5):
        u_str = Ustr(None,ver)
        u_str.read(self)
        return str(u_str)
    
    
    def Read16(self):
        data, = struct.unpack("<H",self.fs.read(2))
        return data
    

    def ReadSigned16(self):
        data, = struct.unpack("<h",self.fs.read(2))
        return data

    
    def Read32(self):
        data, = struct.unpack("<I",self.fs.read(4))
        return data

    
    def ReadSigned32(self):
        data, = struct.unpack("<i",self.fs.read(4))
        return data

    
    def ReadFloat(self):
        data, = struct.unpack("<f",self.fs.read(4))
        return data
    
    
    def ReadDouble(self):
        data, = struct.unpack("<d",self.fs.read(8))
        return data
    

    def ReadVector(self):
        vx,vy,vz, = struct.unpack("<fff",self.fs.read(12))
        return Blender.Mathutils.Vector(vx,vy,vz)    


    #-Write Functions-#
    def WriteBool(self,data):
        data = bool(data)
        self.fs.write(struct.pack("<B",data))
    
    def WriteByte(self,data):
        self.fs.write(struct.pack("<B",data))

    def WriteSignedByte(self,data):
        self.fs.write(struct.pack("<b",data))

        
    def WriteSafeString(self,data,ver=5):
        u_str = Ustr(data,ver)
        u_str.write(self,ver)
    
    
    def Write16(self,data):
        self.fs.write(struct.pack("<H",data))

    
    def WriteSigned16(self,data):
        self.fs.write(struct.pack("<h",data))
    
    
    def Write32(self,data):
        self.fs.write(struct.pack("<I",data))
    
    
    def WriteSigned32(self,data):
        self.fs.write(struct.pack("<i",data))
    
    
    def WriteFloat(self,data):
        data = float(data)
        self.fs.write(struct.pack("<f",data))
    
    
    def WriteDouble(self,data):
        self.fs.write(struct.pack("<d",data))
    
    
    def WriteVector(self,data):
        self.fs.write(struct.pack("<fff",data.x,data.y,data.z))


    #Sanity Functions
    def read(self,size,blah=None):
        if blah:
            return self.fs.read(size,blah)
        else:
            return self.fs.read(size)
    
    
    def seek(self,offset,where=None):
        if where:
            self.fs.seek(offset,where)
        else:
            self.fs.seek(offset)
    
    
    def write(self,data):
        self.fs.write(data)
    
    
    def close(self):
        self.fs.close()
    
    
    def tell(self):
        tell = self.fs.tell()
        return tell


class NotWdys(Exception):
    def __init__(self,val):
        pass


class Wdys:
    def __init__(self):
        self.buf=""
        self.size=0
        self.off=0
        self.base=0xC6EF3720L
        self.max=4294967296
        self.crossRef=(0x6C0A5452,0x03827D0F,0x3A170B92,0x16DB7FC2)
        self.name=""
        self.mode="r"


    def open(self,name,mode="r"):
        if mode=="r" or mode=="rb":
            self.mode="r"
            f=file(name,"rb")
            self.buf=cStringIO.StringIO()
            check=f.read(12)
            if check!="whatdoyousee":
                print "Not a WhatDoYouSee file!? Let's try BriceIsSmart..."
                if check!="BriceIsSmart":
                    raise NotWdys, "Not a WhatDoYouSee/BriceIsSmart file... WTF!!!"
            self.size,=struct.unpack("<I",f.read(4)) 
            off=0
            while off<self.size:
                off+=8
                one,two = struct.unpack("<II",f.read(8))
                one,two = self.decodeQuad(one,two)
                self.buf.write(struct.pack("<II",one,two))
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

    def Write16(self,data):
        self.buf.write(struct.pack("<H",data))
        self.size+=2
        pass

    def flush(self):
        pass


    def close(self):
        if self.mode=="w":
            f=file(self.name,"wb")
            f.write("whatdoyousee")
            #self.size=len(self.buf)
            f.write(struct.pack("<I",self.size))
            off=0
            self.buf.write(struct.pack("<II",0,0))
            self.buf.seek(0)
            while off<self.size:
                off+=8
                one,two = struct.unpack("<II",self.buf.read(8))
                one,two = self.encodeQuad(one,two)
                f.write(struct.pack("<II",one,two))
            self.buf.close()
            f.close()
        else:
            self.buf.close()


    def decodeQuad(self,out1,out2):
        base=self.base
        max=self.max
        crossRef=self.crossRef
        for i in range(0x20,0,-1):
            # 1st word
            tmp1 = tmp2 = out1
            tmp1 = (tmp1 >> 5)
            tmp2 = (tmp2 << 4) % max
            tmp1 ^= tmp2
            tmp1 = (tmp1 + out1) % max
            tmp2 = base
            tmp2 = (tmp2 >> 0x0b)
            tmp2 &= 0x03
            tmp2 = crossRef[tmp2]
            tmp2 = (tmp2 + base) % max
            base = (base + 0x61C88647) % max
            tmp1 ^= tmp2
            out2 = (out2 - tmp1)
            if out2<0:
                out2 += max
            # 2nd word
            tmp1 = tmp2 = out2
            tmp1 = (tmp1 >> 5)
            tmp2 = (tmp2 << 4) % max
            tmp1 ^= tmp2
            tmp1 = (tmp1 + out2) % max
            tmp2 = base
            tmp2 &= 0x03
            tmp2 = crossRef[tmp2]
            tmp2 = (tmp2 + base) % max
            tmp1 ^= tmp2
            out1 = (out1 - tmp1)
            if out1<0:
                out1 += max
        return out1,out2


    def encodeQuad(self,out1,out2):
        base=0
        max=self.max
        crossRef=self.crossRef
        for i in range(0x20,0,-1):
            # 2nd word
            tmp1 = tmp2 = out2
            tmp1 = (tmp1 >> 5)
            tmp2 = (tmp2 << 4) % max
            tmp1 ^= tmp2
            tmp1 = (tmp1 + out2) % max
            tmp2 = base
            tmp2 &= 0x03
            tmp2 = crossRef[tmp2]
            tmp2 = (tmp2 + base) % max
            base -= 0x61C88647
            if base<0:
                base += max
            tmp1 ^= tmp2
            out1 = (out1 + tmp1) % max
            # 1st word
            tmp1 = tmp2 = out1
            tmp1 = (tmp1 >> 5)
            tmp2 = (tmp2 << 4) % max
            tmp1 ^= tmp2
            tmp1 = (tmp1 + out1) % max
            tmp2 = base
            tmp2 >>= 0x0b
            tmp2 &= 0x03
            tmp2 = crossRef[tmp2]
            tmp2 = (tmp2 + base) % max
            tmp1 ^= tmp2
            out2 = (out2 + tmp1) % max
        return out1,out2

#hsEncryptedStream
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
        self.key = struct.pack("<IIII",key1,key2,key3,key4)


    def open(self,name,mode="r"):
        if not cryptoworks:
            raise NotM5Crypt
        if mode=="r" or mode=="rb":
            self.mode="r"
            f=file(name,"rb")
            self.buf=cStringIO.StringIO()
            magic, self.size = struct.unpack("<II",f.read(8))
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
            f.write(struct.pack("<II",0x0D874288,self.size))
            off=0
            cb = AES.new(key)
            for i in range(16-(self.size % 16)):
                self.buf.write(struct.pack("<B",0))
            self.buf.seek(0)
            xout = cb.encrypt(self.buf.read())
            f.write(xout)
            self.buf.close()
            f.close()
        else:
            self.buf.close()


def m5decrypt(what):
    magic, size = struct.unpack("<II",what.read(8))
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
    key = struct.pack("IIII",key1,key2,key3,key4)
    cb = AES.new(key)
    out = cb.decrypt(what.read())
    return out[:size]


def m5crypt(what,out):
    what.read()
    size = what.tell()
    out.write(struct.pack("<II",0x0D874288,size))
    key1 = 0xFC2C6B86L
    key2 = 0x952E7BDAL
    key3 = 0xF1713EE8L
    key4 = 0xC7410A13L
    xorkey = 0xCF092676L
    key1 = key1 ^ xorkey
    key2 = key2 ^ xorkey
    key3 = key3 ^ xorkey
    key4 = key4 ^ xorkey
    key = struct.pack("<IIII",key1,key2,key3,key4)
    cb = AES.new(key)
    for i in range(16-(size % 16)):
        what.write(struct.pack("<B",0))
    what.seek(0)
    xout = cb.encrypt(what.read())
    out.write(xout)
