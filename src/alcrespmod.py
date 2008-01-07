#
# $Id: alcrespmod.py 859 2007-11-04 20:13:11Z trylon $
#
#    Copyright (C) 2005  Alcugs pyprp Project Team
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

# Help library

try:
    import Blender
except ImportError:
    pass

import struct, array, StringIO, random, binascii

from alcurutypes import *
from alc_GeomClasses import *
from alcConvexHull import *
from alcGObjects import *
from alc_AbsClasses import *
from alc_Messages import *
import alcconfig

##########################################
## Note from Trylon (trylon@hbyte.net): ##
## This file is far from finished       ##
##########################################


#TYPE 007C - ResponderModifier
#{plResponderModifier}:{plSynchedObject}

#BASE
#DWORD 0
#BYTE GroupCount // 1 to 11
#respmodGroup[GroupCount]
#BYTE Default // the default group, usually 0
#BYTE bool // usually 1
#BYTE Unknown // usually 1, but 0, 2, and 5 seen
#
    
class plResponderModifier(hsKeyedObject):    #//UNFINISHED
    def __init__(self,parent,name="unnamed",type=0x007C):
        hsKeyedObject.__init__(self,parent,name,type)
        #format
        # Begin plSynchedObject Base Part
        self.flags=0x00000010 #U32 flags 
        self.StringCount = 1 # U16 one string
        self.SdlLink = wpstr("Responder")
        # End plSynchedObject Base Part
        self.dword0 = 0 #U32
        self.respmodGroup = [] # array of respmodGroups
        self.default = 0 #BYTE - The default group
        self.bool = 1 # BYTE
        self.byte0 = 1 # BYTE - Unknown, can be 1, 0, 2 and 5
        # temporary import fix
        self.hasrawdata = 0

    
    def changePageRaw(self,sid,did,stype,dtype):
        hsKeyedObject.changePageRaw(self,sid,did,stype,dtype)
        for group in self.respmodGroup:
            group.changePageRaw(sid,did,stype,dtype)
    

    def read(self,buf,size):
        # just read in rawdata for now, until all message types are implemented with read support
        hasrawdata = 1 # tell that we should write raw data, not object data
        st=buf.tell()
        hsKeyedObject.read(self,buf)
        obj_offset = buf.tell()
        size=size-(buf.tell()-st)
        self.rawdata=cStringIO.StringIO()
        self.rawdata.write(buf.read(size))
        self.rawdata.seek(0)

        endofdata = buf.tell()
        # now see if we can read in some of the data
        buf.seek(obj_offset)
        
    
        # put it to the end to be in the safe side
        buf.seek(endofdata)
    
    def write(self,buf):
        hsKeyedObject.write(self,buf)
        if(self.hasrawdata):
            self.rawdata.seek(0)
            buf.write(self.rawdata.read())
            pass
        else:
                
            buf.write(struct.pack("I",self.flags))
            buf.write(struct.pack("H",self.StringCount))
            self.SdlLink.write(buf)
                     
            buf.write(struct.pack("I",self.dword0))
            buf.write(struct.pack("B",len(self.respmodGroup)))
            for group in self.respmodGroup:
                group.write(buf)
            buf.write(struct.pack("B",self.default))
            buf.write(struct.pack("B",self.bool))
            buf.write(struct.pack("B",self.byte0))


    def dump(self):
        print "BEGIN ResponderModifier %s " % self.Key.name
        print "END RepsonderModifier"
   

#[
# BYTE Unknown // 0 to 7
# BYTE State // State this group applies to? 0 to 10
# BYTE ActionCount
# Actions[ActionCount]
# BYTE TrailerCount // 0 to 7
# WORD Trailer[TrailerCount] // looks like 2 bytes or a flag
#] x

class respmodGroup: #//UNFINISHED
    def __init__(self):
        self.byte0 = 0 # can be 0 to 7 - assuming 0
        self.state = 0 # BYTE - can be 0 to 10
        self.actions = [] # respmodAction array
        self.trailer = [] # WORD array


    def read(self,buf):
        self.byte0 = struct.unpack("B",buf.read(1))
        self.state = struct.unpack("B",buf.read(1))
        size, = struct.unpack("I",buf.read(4))
        for i in range(size):
            o = respModAction(self.getVersion())
            o.read(buf)
            self.actions.append(o)
        size, = struct.unpack("B",buf.read(1))
        for i in range(size):
            b = struct.unpack("B",buf.read(1))
            self.trailer.append(b)
        pass

    
    def write(self,buf):
        buf.write(struct.pack("B",self.byte0))
        buf.write(struct.pack("B",self.state))
        # write the actioncount
        buf.write(struct.pack("B",len(self.actions)))
        for action in self.actions:
            action.write(buf)
        buf.write(struct.pack("B",len(self.trailer)))
        for word in self.trailer:
            buf.write(struct.pack("B",word))             
        pass


    def dump(self):
        print "BEGIN ResponderModifierGroup %s " % self.Key.name
        print "END ResponderModifierGroup"

    
    def changePageRaw(self,sid,did,stype,dtype):
        for action in self.actions:
            action.changePageRaw(sid,did,stype,dtype)


# [
#  WORD ActionSubType // see below
#  URUOBJECTREF parent	 // Always matches the name of this ResponderModifier 
#                         //(changed URUOBJECTDESC to URUOBJECTREF @ Jan 2 '06 -- Trylon)
#  DWORD RefCount
#  URUOBJECTDESC Refs[RefCount] // 1 11 2D 43 6D 77 79 7C A8 B2 C1 C2
#  DWORD 0
#  DWORD 0
#  DWORD Flags // usually 00000800
#  plMessage - depending on actionSubType.
#  BYTE Marker // -1 to 7 higher numbers are rare
# ] x 

# 0206 : 9584 : plAnimCmdMsg
# 020A : 70 : plCameraMsg
# 024A : 533 : plTimerCallbackMsg
# 024F : 1166 : plEnableMsg
# 0255 : 2860 : plSoundMsg
# 02E1 : 83 : plLinkToAgeMsg
# 02E8 : 916 : plNotifyMsg
# 02FD : 36 : plResponderEnableMsg
# 0302 : 488 : plOneShotMsg
# 0330 : 311 : plExcludeRegionMsg
# 038E : 515 : plArmatureEffectStateMsg
# 03BA : 4 : plSubWorldMsg
# 045B : 188 : plSimSuppressMsg

class respmodAction: #//UNFINISHED
    def __init__(self,parentRef=None):
        self.parent = parentRef
        self.ActionSubType = 0 # U32
        self.refs = [] # Refs can be 1 11 2D 43 6D 77 79 7C A8 B2 C1 C2
        self.dword0 = 0
        self.dword1 = 0
        self.flags = 0x00000800 # default - can be different.
        #self.message
        self.marker = -1 # default to -1, -1 to 7 are common.


    def read(self,buf):
        self.ActionSubType = struct.unpack("I",buf.read(4))
        size, = struct.unpack("I",buf.read(4))
        for i in range(size):
            o = UruObjectRef(self.getVersion())
            o.read(buf)
            if not o.Key.object_type in (0x01,0x11,0x2D,0x43,0x6D,0x77,0x79,0x7C,0xA8,0xB2,0xC1,0xC2):
                raise RuntimeError, "Type %04X is not in allow list 2" % o.Key.object_type
            self.refs.append(o)
        self.dword0 = struct.unpack("I",buf.read(4))
        self.dword1 = struct.unpack("I",buf.read(4))
        self.flags = struct.unpack("I",buf.read(4))
        self.message = PrpMessage(self.ActionSubType,self.getVersion())
        self.message.read()
        self.marker = struct.unpack("b",buf.read(1))
        pass
    

    def write(self,buf):
        buf.write(struct.pack("H",self.ActionSubType))
        self.parent.write(buf)
        buf.write(struct.pack("I",len(self.refs)))
        for ref in self.refs:
            ref.write(buf)
        buf.write(struct.pack("I",self.dword0))
        buf.write(struct.pack("I",self.dword1))
        buf.write(struct.pack("I",self.flags))
        self.message.update(self.parent.Key)
        self.message.write(buf)
        buf.write(struct.pack("b",self.marker))
        pass


    def dump(self):
        print "BEGIN ResponderModifierAction %s " % self.Key.name
        print "END ResponderModifierAction"

    
    def changePageRaw(self,sid,did,stype,dtype):
        self.parent.changePageRaw(sid,did,stype,dtype)
        self.message.changePageRaw(sid,did,stype,dtype)

#  if plAnimCmdMsg or plSoundMsg or plNotifyMsg 
#    DWORD CallbackCount
#    [ plEventCallbackMsg
#      WORD Id // 024B
#      BYTE 0
#      DWORD
#      URUOBJECTDESC parent // Matches this object
#      DWORD 0
#      DWORD 0
#      DWORD Flags // 00000800
#      FLOAT
#      DWORD // 1 or 3
#      WORD 0
#      WORD // 0 to 7
#    ] x CallbackCount
#    if plAnimCmdMsg or plSoundMsg 
#      DWORD 1
#      DWORD Flags
#      DWORD[7] // All 0
#      if plAnimCmdMsg
#        URUSTRING Verb
#        URUSTRING Null
#      else (plSoundMsg)
#        WORD 0
#        WORD // 0 to 1B
#        BYTE[15] Null
#    else plNotifyMsg
#      DWORD 0
#      FLOAT 1.0
#      DWORD 0
#      DWORD 1
#      DWORD TypeA
#      if TypeA = 1
#        WORD 1
#        BYTE 0
#      else if TypeA = 8
#        DWORD 1
#  else if plArmatureEffectStateMsg
#    WORD // 0 to 12
#  else if plOneShotMsg 
#    DWORD CommandCount
#    [
#       URUSTRING Command
#       URUOBJECTDESC Target // 007C
#       WORD // 0 to 4
#    ] x CommandCount
#  else if plTimerCallbackMsg
#    DWORD // -1 to 6
#    FLOAT Seconds?
#  else if plEnableMsg
#    DWORD 1
#    DWORD // 1 2 5 6
#    DWORD 0
#  else if plExcludeRegionMsg 
#    DWORD // 0 1
#    BYTE 0
#  else if plResponderEnableMsg or plSimSuppressMsg
#    BYTE // 0 1
#  else if plLinkToAgeMsg
#    WORD Type1 // 2300 or 6300
#    WORD Type2 // 0100 or 0300
#    URUSTRING AgeName
#    if Type2 = 0300
#      URUSTRING AgeName2?
#    BYTE // 0 to 3
#    DWORD 1
#    DWORD 7
#    URUSTRING[4] LinkInfo
#    if Type1 = 6300
#      URUSTRING MoreLinkInfo
#  else if plCameraMsg
#    DWORD Type // 1 or 2
#    if Type = 1
#      DWORD Flags
#      DWORD[2] Null
#      BYTE 0
#      URUOBJECTDESC // SeceneObject or Null
#      DWORD[11] Null
#      WORD 0
#    else
#      DWORD 0
#      DWORD 1
#      DWORD[14] Null
#  else if plSubWorldMsg
#    URUOBJECTDESC // SeceneObject or Null


