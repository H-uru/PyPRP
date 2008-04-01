#
# $Id: alc_AbsClasses.py 455 2006-04-21 20:18:42Z AdamJohnso $
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

import math, struct
from alchexdump import *
from alcurutypes import *
import alcconfig, alchexdump
#from alc_Messages import *
#from alc_GeomClasses import *

class plSynchedObject(hsKeyedObject):                       #Type 0x28
    Flags = \
    { \
        "kDontDirty"                 :  0x1, \
        "kSendReliably"              :  0x2, \
        "kHasConstantNetGroup"       :  0x4, \
        "kDontSynchGameMessages"     :  0x8, \
        "kExcludePersistentState"    : 0x10, \
        "kExcludeAllPersistentState" : 0x20, \
        "kLocalOnly"                 : 0x28, \
        "kHasVolatileState"          : 0x40, \
        "kAllStateIsVolatile"        : 0x80  \
    }

    def __init__(self,parent,name="unnamed",type=0x28):
        hsKeyedObject.__init__(self,parent,name,type)
        self.fSynchFlags=0
        self.fSDLExcludeList=[]
        self.fSDLVolatileList=[]

    def read(self,stream):
        hsKeyedObject.read(self,stream)
        self.fSynchFlags = stream.Read32()

        if (self.getVersion()==5 and self.fSynchFlags & plSynchedObject.Flags["kExcludePersistentState"]) or \
            (self.getVersion()==6 and not self.fSynchFlags & plSynchedObject.Flags["kHasConstantNetGroup"]): # m5 Flags are possibly different....
            count = stream.Read16()
            for i in range(count):
                s = stream.ReadSafeString(self.getVersion())
                self.fSDLExcludeList.append(s)

        if (self.getVersion()==5 and self.fSynchFlags & plSynchedObject.Flags["kHasVolatileState"]):
            count = stream.Read16()
            for i in range(count):
                s = stream.ReadSafeString(self.getVersion())
                self.fSDLVolatileList.append(s)


    def write(self,stream):
        hsKeyedObject.write(self,stream)
        if len(self.fSDLExcludeList)!=0:
            self.fSynchFlags |= plSynchedObject.Flags["kExcludePersistentState"]

        if len(self.fSDLVolatileList)!=0:
            self.fSynchFlags |= plSynchedObject.Flags["kHasVolatileState"]
            
        stream.Write32(self.fSynchFlags)

        if self.fSynchFlags & plSynchedObject.Flags["kExcludePersistentState"]:
            stream.Write16(len(self.fSDLExcludeList))
            for s in self.fSDLExcludeList:
                stream.WriteSafeString(s, 0)

        if self.fSynchFlags & plSynchedObject.Flags["kHasVolatileState"]:
            stream.Write16(len(self.fSDLVolatileList))
            for s in self.fSDLVolatileList:
                stream.WriteSafeString(s, 0)


    def changePageRaw(self,sid,did,stype,dtype):
        hsKeyedObject.changePageRaw(self,sid,did,stype,dtype)


class plObjInterface(plSynchedObject):                      #Type 0x10
    def __init__(self,parent,name="unnamed",type=None):
        plSynchedObject.__init__(self,parent,name,type)
        self.parentref=UruObjectRef(self.getVersion())
        self.BitFlags=hsBitVector()

    def read(self,stream):
        plSynchedObject.read(self,stream)
        self.parentref.read(stream)
        self.BitFlags.read(stream)


    def write(self,stream):
        plSynchedObject.write(self,stream)
        self.parentref.write(stream)
        self.BitFlags.write(stream)

    def changePageRaw(self,sid,did,stype,dtype):
        plSynchedObject.changePageRaw(self,sid,did,stype,dtype)
        self.parentref.changePageRaw(sid,did,stype,dtype)


class plModifier(plSynchedObject):                          #Type 0x1E
    def __init__(self,parent,name="unnamed",type=None):
        plSynchedObject.__init__(self,parent,name,type)


class plSingleModifier(plModifier):                         #Type 0x1F
    def __init__(self,parent,name="unnamed",type=None):
        plModifier.__init__(self,parent,name,type)
        self.bitVector = hsBitVector()


    def read(self,stream):
        plModifier.read(self,stream)
        self.bitVector.read(stream)
    
    
    def write(self,stream):
        plModifier.write(self,stream)
        self.bitVector.write(stream)

class plMultiModifier(plModifier):                          #Type 0x27
    def __init__(self,parent,name="unnamed",type=None):
        plModifier.__init__(self,parent,name,type)
        self.BitVector=hsBitVector()


    def read(self,stream):
        plModifier.read(self,stream)
        self.BitVector.read(stream)


    def write(self,stream):
        plModifier.write(self,stream)
        self.BitVector.write(stream)


class plAGAnim(plSynchedObject):                #Type 0x6B
    def __init(self,parent,name="unnamed",type=None):
        plSynchedObject.__init__(self,parent,name,type)
        self.AnimName = 0
        self.StartTime = 0
        self.EndTime = 0
        self.AGApp = []
    
    def read(self,stream):
        plSynchedObject.read(self,stream)
        self.AnimName = stream.ReadSafeString()
        self.StartTime = stream.ReadFloat()
        self.StopTime = stream.ReadFloat()
        i = stream.Read32()
        for j in range(i):
            self.AGApp[j] = plAGApplicator()
            self.AGApp[j].read(stream)
    
    def write(self,stream):
        plSynchedObject.write(self,stream)
        stream.WriteSafeString(self.AnimName)
        stream.WriteFloat(self.StartTime)
        stream.WriteFloat(self.StopTime)
        stream.Write32(len(self.AGApp))
        for i in range(len(self.AGApp)):
            self.AGApp[i].write(stream)

class plRegionBase(plObjInterface):             #Type 0x0118
    def __init__(self,parent,name="unnamed",type=None):
        plObjInterface.__init__(self,parent,name,type)
