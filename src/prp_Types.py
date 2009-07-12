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

# Uru Types

import struct,cStringIO
from prp_HexDump import *


class ptLog:
    def __init__(self,handle,filename,mode="w"):
        self.file=file(filename,mode)
        self.handle=handle


    def write(self,x):
        self.handle.write(x)
        self.file.write(x)


    def flush():
        self.handle.flush()
        self.file.flush()


    def close(self):
        self.file.close()


#Flags
KAgeData = 0
KAgeSDLHook = 2
KAgeTextures = 1

class xPageId:
    def __init__(self):
        self.num=0
        self.seq=0
        self.type=0
        self.flags=0


    def setSeq(self,seq):
        self.seq=seq


    def getSeq(self):
        return self.seq


    def setNum(self,num):
        self.num=num


    def getNum(self):
        return self.num


    def setType(self,type):
        self.type=type
        if type in [0x00,0x04,0x10]:
            self.flags=KAgeData
        elif type==0x08:
            if self.num==-2: # or self.num==0x1F:
                self.flags=KAgeSDLHook
            elif self.num==-1: # or self.num==0x20:
                self.flags=KAgeTextures
            else:
                raise RuntimeError, "page error"


    def getType(self):
        if self.flags in [KAgeSDLHook,KAgeTextures]:
            self.type=0x08
        else:
            if self.seq<0:
                self.type=0x04
            else:
                if self.type not in [0x00,0x08,0x10]:
                    self.type=0x00
        return self.type


    def setFlags(self,flags):
        self.flags=flags


    def getFlags(self):
        return self.flags


    def setRaw(self,pid,type,agePrefix):
        self.type=type
        a = pid & 0xFF
        b = pid >> 8
        if not self.type in [0x00,0x04,0x08,0x10]:
            raise RuntimeError, "unknown page type"
        if self.type==0x04:
            assert(b & 0xFFFF00 == 0xFFFF00)
            b = b & 0x0000FF
            b = b * -1
            a = a-1
            self.flags = KAgeData
        elif self.type in [0x00,0x10]:
            # In case the page number is greater than 223,
            # the 'carry' bit bleeds into the sequence number
            # (i.e. age prefix).  So, to get the correct page number
            # from the pid, we need to check the extracted sequence
            # from the pid against the known age prefix and increase the
            # page number accordingly
            newPid = pid - (agePrefix << 8)
            a = newPid - 0x21
            b = agePrefix
            self.flags = KAgeData
        elif self.type==0x08:
            b = b-1
            if a == 0x20:
                a = -1
                self.flags=KAgeTextures
            elif a== 0x1F:
                a = -2
                self.flags=KAgeSDLHook
            else:
                raise RuntimeError, "unknown page id"
        self.seq = b
        self.num = a


    def getRaw(self):
        b=abs(self.seq)
        a=0
        tail=0
        flags=self.getFlags()
        if flags==KAgeSDLHook:
            a=0x1F
            b=b+1
            self.type=0x08
        elif flags==KAgeTextures:
            a=0x20
            b=b+1
            self.type=0x08
        else:
            if self.seq<0:
                a=0x01
                tail=0xFFFF0000L
                self.type=0x04
            else:
                a=0x21
                #sefl.type=0x00
            a=a+self.num
        page_id=(a + (b<<8) + tail)
        return page_id


    def setPage(self,seq,page=0,flags=KAgeData,type=None):
        if flags==None:
            flags=KAgeData
        self.setType(0)
        self.setSeq(seq)
        self.setNum(page)
        self.setFlags(flags)
        if type!=None:
            self.setType(type)
        self.getType()


class Ustr:
    def __init__(self,str=None,version=None):
        if str==None:
            str=""
        if version==None:
            version=1
        self.name=str
        self.version=version
        #version 0 - normal str
        #version 1 - auto (normal/inverted)
        #version 5 - inverted
        #version 6 - myst5


    def setType(self,type):
        self.version=type


    def __repr__(self):
        return self.name


    def __str__(self):
        return self.__repr__()


    def __cmp__(self,other):
        if other==None:
            return False
        return self.name==other.name


    def read(self,buf,type=1):
        """ Returns a string from an Urustring"""
        if type!=1:
            self.version=type
        size = buf.Read16()
        if self.version!=6:
            inverted = (size & 0xF000)==0xF000
            size = size & 0x0FFF
            if inverted:
                self.version=5
            else:
                self.version=0

        if size>1024:
            print "%08X %08X" %(size,buf.tell())
            hexdump(buf.read(100))
            raise RuntimeError, "sanity check on Urustring failed!, invalid file, or is corrupted!?"
            return
        str = buf.read(size)
        str2=""
        if self.version==5:
            for i in range(len(str)):
                c,=struct.unpack("B",str[i])
                str2=str2 + struct.pack("B",c ^ 0xFF)
        elif self.version==6:
            key="mystnerd"
            for i in range(len(str)):
                c,=struct.unpack("B",str[i])
                k,=struct.unpack("B",key[i % 8])
                str2=str2 + struct.pack("B",c ^ k)
        else:
            str2=str
        self.name=str2
        #print str2
        return self.name


    def write(self,buf,inverted=0):
        if self.version!=6 and inverted:
            self.version=5
        size = len(self.name)
        if size > 0x0FFF:
            raise RuntimeError, "String is too long"
        str=""
        if self.version==5:
            size = size | 0xF000
            for i in range(len(self.name)):
                c,=struct.unpack("B",self.name[i])
                str=str + struct.pack("B",c ^ 0xFF)
        elif self.version==6:
            key="mystnerd"
            for i in range(len(self.name)):
                c,=struct.unpack("B",self.name[i])
                k,=struct.unpack("B",key[i % 8])
                str=str + struct.pack("B",c ^ k)
        else:
            str=self.name
        buf.Write16(size)

        buf.write(str)


    def set(self,name):
        self.name=name


class str32: # Bstr
    def __init__(self,str=None,type=None):
        if str==None:
            str=""
        if type==None:
            type=0
        self.name=str
        self.type=type
        # type 0 - null terminated
        # type 1 - not null terminated


    def __repr__(self):
        return self.name


    def __str__(self):
        return self.__repr__()


    def __cmp__(self,other):
        return self.name==other.name


    def read(self,buf):
        if self.type==0:
            size = buf.Read32()
            str = buf.read(size-1)
            self.name=str
            b = buf.ReadByte()
            assert(b==0)
        else:
            size = buf.Read32()
            str = buf.read(size)
            self.name=str


    def write(self,buf):
        if self.type==0:
            size = len(self.name)
            buf.write(struct.pack("<I",size+1))
            buf.write(self.name)
            buf.write(struct.pack("B",0))
        else:
            size = len(self.name)
            buf.Write32(size)
            buf.write(self.name)


    def set(self,name):
        self.name=name

class wpstr: # wpstr
    def __init__(self,str=None,type=None):
        if str==None:
            str=""
        if type==None:
            type=1  # though we might want support for null terminated strings, the
                    # wpstr doesn't actually need it.
        self.name=str
        self.type=type
        # type 0 - null terminated
        # type 1 - not null terminated

    def __repr__(self):
        return self.name


    def __str__(self):
        return self.__repr__()


    def __cmp__(self,other):
        return self.name==other.name


    def read(self,buf):
        if self.type==0:
            size = buf.Read16()
            str = buf.read(size-1)
            self.name=str
            b = buf.ReadByte()
            assert(b==0)
        else:
            size, = struct.unpack("<H",buf.read(4))
            str = buf.read(size)
            self.name=str


    def write(self,buf):
        if self.type==0:
            size = len(self.name)
            buf.write(struct.pack("<H",size+1))
            buf.write(self.name)
            buf.write(struct.pack("B",0))
        else:
            size = len(self.name)
            buf.Write16(size)
            buf.write(self.name)


    def set(self,name):
        self.name=name


class plKey:
    def __init__(self,version=5,agePrefix=0):
        #Format
        self.flag=0 #Byte
        self.page_id=0 #U32
        self.page_type=0 #U16 (Uru) / Byte (m5)
        self.uk=0 #Byte (Uru)
        self.object_type=0 #U16
        self.num=0 #U32 (m5)
        self.name=""
        #uk #Byte (m5)
        self.version=version
        self.agePrefix = agePrefix


    def __str__(self):
        out="%08X,%04X,%04X,%s" % (self.page_id,self.page_type,self.object_type,self.name.__str__())
        if self.version==6:
            out=out + ",i:%04i" %(self.num)
        if self.flag!=0x00:
            out=out + ",f:%02X,u:%02X" %(self.flag,self.uk)
        return out


    def __cmp__(self,other):
        return (self.flag == other.flag and self.page_id==other.page_id \
                and self.page_type==other.page_type and self.object_type==other.object_type \
                and self.name == other.name)


    def read(self,buf):
        #print self.version
        self.flag = buf.ReadByte()
        self.page_id = buf.Read32()
        if self.version==6:
            self.page_type = buf.ReadByte()
        else:
            self.page_type = buf.Read16()
        if self.version==5 and self.flag & 0x02:
            self.uk = buf.ReadByte()
        self.object_type = buf.Read16()
        if self.version==6:
            self.num = buf.Read32()

        self.name = buf.ReadSafeString(self.version)
        #self.name.setType(self.version)
        #self.name.read(buf)
        if (self.flag & 0x04 or self.flag & 0x02) and self.version==6:
            self.uk = buf.ReadByte()
        if self.flag not in (0x00,0x02,0x04):
            print "%08X" % buf.tell()
            raise RuntimeError,"WARNING flag on plKey is %02X %s" % (self.flag,self.name)


    def write(self,buf):
        buf.WriteByte(self.flag)
        buf.Write32(self.page_id)
        if self.version==6:
            buf.Write32(self.page_type)
        else:
            buf.Write16(self.page_type)
        if self.version==5 and self.flag & 0x02:
            buf.WriteByte(self.uk)
        buf.Write16(self.object_type)
        if self.version==6:
            buf.Write32(self.num)
        #Commented out use of WriteSafeString() - it causes problems on load
        #Note@jan-03-2008: safestring should work now
        buf.WriteSafeString(self.name,self.version)
        #self.name.setType(self.version)
        #self.name.write(buf,1)
        if self.version==6 and (self.flag & 0x04 or self.flag & 0x02):
            buf.WriteByte(self.uk)

    def changePage(self,sseq,dseq,spage,dpage,stype,dtype):
        page1 = xPageId()
        page2 = xPageId()
        page1.setSeq(sseq)
        page1.setNum(spage)
        page1.setType(stype)
        page2.setSeq(dseq)
        page2.setNum(dpage)
        page2.setType(dtype)
        self.changePageRaw(page1.getRaw(),page2.getRaw(),stype,dtype)
        self.agePrefix = dseq


    def changePageRaw(self,sid,did,stype,dtype):
        if self.page_type==stype and self.page_id==sid:
            self.page_type=dtype
            self.page_id=did


    def setPage(self,seq,page=0,flags=KAgeData):
        page1 = xPageId()
        page1.setSeq(seq)
        page1.setNum(page)
        page1.setFlags(flags)
        self.page_id=page1.getRaw()
        self.page_type=page1.getType()
        self.agePrefix = seq


    def getxPageId(self):
        page = xPageId()
        page.setRaw(self.page_id,self.page_type,self.agePrefix)
        return page


    def setName(self,name):
        self.name.set(name)


    def update(self,Key):
        self.page_id=Key.page_id
        self.page_type=Key.page_type


    def verify(self,Key):
        return (self.page_id==Key.page_id and self.page_type==Key.page_type)


    def checktype(self,type):
        return (self.object_type==type)


    def setVersion(self,version):
        self.version=version


    def getPageNum(self):
        if self.agePrefix == 0:
            raise RuntimeError,"Age prefix of key was never set!"
        return self.getxPageId().getNum()


class hsKeyedObject:                                 #Type 0x02
    Debug = False
    def __init__(self,parent,name="unnamed",type=0xFFFF):
        self.parent = parent
        self.Key=plKey(self.getVersion(),self.getRoot().age.getSeq())
        self.Key.page_id=self.parent.page_id
        self.Key.page_type=self.parent.page_type
        if (type==0xFFFF):
            raise RuntimeError,"hsKeyedObject::__init__(): no type specified for object %s" %(name)
        self.Key.object_type=type
        self.Key.name = name


    def changePage(self,sseq,dseq,spage,dpage,stype,dtype):
        page1 = xPageId()
        page2 = xPageId()
        page1.setSeq(sseq)
        page1.setNum(spage)
        page1.setType(stype)
        page2.setSeq(dseq)
        page2.setNum(dpage)
        page2.setType(dtype)
        self.changePageRaw(page1.getRaw(),page2.getRaw(),stype,dtype)


    def changePageRaw(self,sid,did,stype,dtype):
        self.Key.changePageRaw(sid,did,stype,dtype)


    def getPageNum(self):
        return self.Key.getPageNum()


    def getRef(self):
        ref = UruObjectRef(self.getVersion())
        ref.Key=self.Key
        ref.flag=1
        return ref

    def getName(self):
        return self.Key.name

    def getResManager(self):
        if self.parent.parent.parent.resmanager!=None:
            return self.parent.parent.parent.resmanager
        else:
            return self.getRoot()


    def getRoot(self):
        # Returns the PrpFile instance
        return self.parent.parent.parent


    def getVersion(self):
        return self.getRoot().getVersion()


    def read(self,buf,really=1,silent=0):

        if not really:
            return
        localType = buf.Read16() #This isn't actually part of hsKeyedObject
        self.Key.setVersion(self.getVersion())
        self.Key.read(buf)
        if (not silent) and hsKeyedObject.Debug:
            print "[%04X] %s" % (self.Key.object_type, self.Key.name)
        assert(localType==self.Key.object_type)


    def write(self,buf,really=1):
        if not really:
            return
        buf.Write16(self.Key.object_type) #This isn't actually part of hsKeyedObject
        self.Key.write(buf)




class hsTArray:
    def __init__(self,AllowedTypes=[],ver=5,checkTypes=False):
        self.size=0
        self.vector=[]
        self.ver=ver
        self.AllowedTypes = AllowedTypes
        self.checkTypes = checkTypes


    def __len__(self):     #See the below comment ;)
        return int(self.size)


    def __getitem__(self, index):
        return self.vector[index]


    def __setitem__(self, index, value):
        self.vector[index]=value


    def append(self,item): #Gotta be smarter than the code :P
        if self.checkTypes and not item.Key.object_type in self.AllowedTypes:
            raise RuntimeError, "Type %04X is not Allowed in this vector." % item.Key.object_type
        self.vector.append(item)
        self.size = len(self.vector)

    def remove(self,item):
        self.vector.remove(item)
        self.size = len(self.vector)


    def changePageRaw(self,sid,did,stype,dtype): # :P
        for v in self.vector:
            v.changePageRaw(sid,did,stype,dtype)


    def ReadVector(self,buf):
        self.size = buf.Read32()
        for i in range(self.size):
            self.ReadRef(buf)

    def ReadRef(self,buf):
        o = UruObjectRef(self.ver)
        o.read(buf)
        if self.checkTypes and len(self.AllowedTypes) > 0 and not o.Key.object_type in self.AllowedTypes:
            raise RuntimeError, "Type %04X is not Allowed in this vector." % o.Key.object_type
        self.vector.append(o)

    def Trash(self):
        self.vector=[]
        self.size=0


    def WriteVector(self, buf):
        buf.Write32(self.size)
        for o in self.vector:
            #o.update(self.Key)
            o.write(buf)


    def read(self, buf):
        return self.ReadVector(buf)


    def write(self, buf):
        return self.WriteVector(buf)

    def update(self,key):
        for o in self.vector:
            o.update(key)

class hsBitVector:
    def __init__(self):
        self.data=[]

    def __len__(self):
        return int(len(self.data) * 32)     # 32 bits per dword in the data


    def clear(self):
        self.data=[]


    def __getitem__(self, index):
        dwordidx = index >> 5 # (Equivalent to index / 32 ) Maximum 32 bits per dword

        if (dwordidx < len(self.data)):
            return (self.data[dwordidx] & (1 << (index & 31))) != 0
        else:
            return False


    def __setitem__(self, index, value):
        if bool(value):
            self.SetBit(index)
        else:
            self.ClearBit(index)

    def ClearBit(self,index):
        dwordidx = index >> 5 # (Equivalent to index / 32 ) Maximum 32 bits per dword

        if dwordidx >= len(self.data): # append another dword if neccesary
            self.data.append(0x00000000)

        self.data[dwordidx] &= ~( 1 << (index & 31)) # (index & 31)  gives the bit index within this dword

    def SetBit(self,index):
        dwordidx = index >> 5 # (Equivalent to index / 32 ) Maximum 32 bits per dword

        if dwordidx >= len(self.data): # append another dword if neccesary
            self.data.append(0x00000000)

        self.data[dwordidx] |= ( 1 << (index & 31)) # (index & 31)  gives the bit index within this dword


    def append(self,bull):
        self.data.append(bull)


    def read(self,buf):
        self.data = []
        count = buf.Read32()
        for i in range(count):
            dword = buf.Read32()
            self.data.append(dword)


    def write(self,buf):
        buf.Write32(len(self.data))
        for i in range(len(self.data)):
            buf.Write32(self.data[i])

    def __repr__(self):
        str = "BitVector: ["
        for i in range(len(self.data)-1,-1,-1):
            str += "%4X"%(self.data[i])
            if i < len(self.data) - 1:
                str += " "
        str += "]"

        return str

    def __str__(self):
        return self.__repr__()


class pRaw(hsKeyedObject):
    def __init__(self,parent,name="unnamed",type=0):
        hsKeyedObject.__init__(self,parent,name,type)
        self.data=None


    def read(self,buf,size):
        st=buf.tell()
        hsKeyedObject.read(self,buf)
        size=size-(buf.tell()-st)
        #self.data=hsStream
        self.data=cStringIO.StringIO()
        self.data.write(buf.read(size))
        self.data.seek(0)


    def write(self,buf):
        hsKeyedObject.write(self,buf)
        self.data.seek(0)
        buf.write(self.data.read())


    def import_all(self, name):
        pass


    def changePageRaw(self,sid,did,stype,dtype):
        hsKeyedObject.changePageRaw(self,sid,did,stype,dtype)
        self.data.seek(0)
        print "change page %08X %08X %04X %04X" %(sid,did,stype,dtype)
        foo = self.data.read(4)
        while foo!="" and len(foo)==4:
            foo, = struct.unpack("<I",foo)
            if foo==sid:
                print "checking %08X %08X" %(foo,sid),
                bar = self.data.read(2)
                if bar=="" or len(bar)!=2:
                    return
                bar, = struct.unpack("<H",bar)
                if bar==stype:
                    self.data.seek(-6,1)
                    self.data.write(struct.pack("<I",did))
                    self.data.write(struct.pack("<H",dtype))
                    print "key changed"
                else:
                    self.data.seek(-5,1)
            else:
                self.data.seek(-3,1)
            foo = self.data.read(4)


class UruObjectRef:
    def __init__(self,version=5):
        self.flag=0
        self.Key=plKey(version)


    def __str__(self):
        return self.Key.__str__()


    def read(self,buf):
        if self.Key.version==6:
            self.Key.read(buf)
            if self.Key.page_id==0xFFFFFFFFL:
                self.flag=0
            else:
                self.flag=1
        else:
            self.flag = buf.ReadByte()
            if self.flag==0x01:
                self.Key.read(buf)
            elif self.flag!=0x00:
                raise RuntimeError,"WARNING, Object Ref flag must be 0x01 or 0x00! - found %02X" %(self.flag)


    def write(self,buf):
        if self.Key.version==6:
            if self.flag==0:
                null=plKey(self.Key.version)
                null.page_id=0xFFFFFFFFL
                null.write(buf)
            else:
                self.Key.write(buf)
        else:
            buf.WriteByte(self.flag)
            if self.flag==0x01:
                self.Key.write(buf)


    def update(self,Key):
        self.Key.update(Key)


    def verify(self,Key):
        if self.flag==0x00:
            return 1
        return self.Key.verify(Key)


    def checktype(self,type):
        if self.flag==0x00:
            return 1
        return self.Key.checktype(type)


    def changePage(self,sseq,dseq,spage,dpage,stype,dtype):
        page1 = xPageId()
        page2 = xPageId()
        page1.setSeq(sseq)
        page1.setNum(spage)
        page1.setType(stype)
        page2.setSeq(dseq)
        page2.setNum(dpage)
        page2.setType(dtype)
        self.changePageRaw(page1.getRaw(),page2.getRaw(),stype,dtype)


    def changePageRaw(self,sid,did,stype,dtype):
        self.Key.changePageRaw(sid,did,stype,dtype)


    def setVersion(self,version):
        self.Key.setVersion(version)


    def isNull(self):
        if self.flag==1:
            return 0
        else:
            return 1

