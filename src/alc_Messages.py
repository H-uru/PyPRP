#
# $Id: alc_Messages.py 455 2006-08-04 20:18:42Z Robert The Rebuilder $
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

import struct

from alc_GeomClasses import *
from alcurutypes import *
from alc_RefParser import *
from alc_EventData import *
from alc_AlcScript import *
import alcconfig, alchexdump, alc_GeomClasses


## Currently implemented: 
# Message Type: 0x0219 - plActivatorMsg
# Message Type: 0x038E - plArmatureEffectStateMsg
# Message Type: 0x02E8 - plNotifyMsg
# Message Type: 0x0203 - plRefMsg
# Message Type: 0x0204 - plGenRefMsg
# Message Type: 0x0330 - plExcludeRegionMsg
# Message Type: 0x020A - plCameraMsg
# Message Type: 0x0302 - plOneShotMsg

## Still Needed at the moment:
# Message Type: 0x0206 - plAnimCmdMsg
# Message Type: 0x024A - plTimerCallbackMsg
# Message Type: 0x024F - plEnableMsg
# Message Type: 0x0255 - plSoundMsg
# Message Type: 0x02E1 - plLinkToAgeMsg
# Message Type: 0x02FD - plResponderEnableMsg
# Message Type: 0x03BA - plSubWorldMsg
# Message Type: 0x045B - plSimSuppressMsg

class PrpMessage:
    def __init__(self,type=None,version=None):
        if type == None:
            self.msgtype = 0xFFFF
        else:
            self.msgtype = type
        if version == None:
            self.version = 5
        else:
            self.version = version
        self.data = None
        self.Key = plKey(self.version)
        if self.version == 5:
            #UruTypes
            if   self.msgtype == 0x02E8:
                self.data = plNotifyMsg(self)
            elif self.msgtype == 0x038E:
                self.data = plArmatureEffectStateMsg(self)
            elif self.msgtype == 0x020A:
                self.data = plCameraMsg(self)
            elif self.msgtype == 0x0451:
                self.data = plSwimMsg(self)
            elif self.msgtype == 0x0203:
                self.data = plMessage(self)
            elif self.msgtype == 0x0302:
                self.data = plOneShotMsg(self)
            elif self.msgtype == 0x0255:
                self.data = plSoundMsg(self)
            elif self.msgtype == 0x024F:
                self.data = plEnableMsg(self)
            else:
                raise ValueError, "Unsupported message type %04X %s" % (self.msgtype,MsgKeyToMsgName(self.msgtype))
        elif self.version == 6:
            #Myst 5 types
            raise RuntimeError, "Unsupported Myst 5 message type %04X" % self.msgtype


    def read(self,buf):
        self.data.read(buf)


    def write(self,buf):
        self.data.write(buf)


    def getVersion(self):
        return self.version


    def update(self,Key):
        self.Key.update(Key)


    def changePageRaw(self,sid,did,stype,dtype):
        self.Key.changePageRaw(sid,did,stype,dtype)
        if self.data != None:
            self.data.changePageRaw(sid,did,stype,dtype)
            
    def _FromStream(stream,version=5):
        _type = stream.Read16()                   # read message key type
        msg = PrpMessage(_type,version)    # create correct message object
        
        try:
            msg.data.read(stream)                       # read message 
            return msg
        except TypeError,detail:
            print "Message type: ",MsgKeyToMsgName(_type)
            print "Got TypeError:",detail
            raise RuntimeError,detail
    FromStream = staticmethod(_FromStream)
    
    def _ToStream(stream,msg):
        stream.Write16(msg.msgtype)
        msg.write(stream)

    ToStream = staticmethod(_ToStream)
    
        

class plMessage:
    plBCastFlags = \
    { \
        "kBCastNone"                :     0x0, \
        "kBCastByType"              :     0x1, \
        "kBCastUNUSED_0"            :     0x2, \
        "kPropagateToChildren"      :     0x4, \
        "kBCastByExactType"         :     0x8, \
        "kPropagateToModifiers"     :    0x10, \
        "kClearAfterBCast"          :    0x20, \
        "kNetPropagate"             :    0x40, \
        "kNetSent"                  :    0x80, \
        "kNetUseRelevanceRegions"   :   0x100, \
        "kNetForce"                 :   0x200, \
        "kNetNonLocal"              :   0x400, \
        "kLocalPropagate"           :   0x800, \
        "kNetNonDeterministic"      :   0x200, \
        "kMsgWatch"                 :  0x1000, \
        "kNetStartCascade"          :  0x2000, \
        "kNetAllowInterAge"         :  0x4000, \
        "kNetSendUnreliable"        :  0x8000, \
        "kCCRSendToAllPlayers"      : 0x10000, \
        "kNetCreatedRemotely"       : 0x20000  \
    }

    def __init__(self,parent=None,type=0x0203): # Message type: 0x0203
        if parent == None:
            self.msgtype = 0xFFFF
        else:
            self.msgtype = parent.msgtype
        self.parent = parent
        self.MessageType = type

        self.fSender = UruObjectRef()
        self.fReceivers = []
        self.fTimeStamp = 0.0
        self.fBCastFlags = plMessage.plBCastFlags["kLocalPropagate"]

    def getVersion(self):
        return self.parent.getVersion()

    def read(self, buf):
        pass


    def write(self, buf):
        pass


    def changePageRaw(self,sid,did,stype,dtype):
        pass
    
    def IMsgRead(self,stream):
        self.fSender.read(stream) # uruobjectref
        count = stream.Read32()
        for i in range(count):
            key = UruObjectRef()
            key.read(stream)
            self.fReceivers.append(key)

        self.fTimeStamp = stream.ReadDouble()
        self.fBCastFlags = stream.Read32()
    
    
    def IMsgWrite(self,stream):
        self.fSender.write(stream)
        stream.Write32(len(self.fReceivers))
        for key in self.fReceivers:
            key.write(stream)
        stream.WriteDouble(self.fTimeStamp)
        stream.Write32(self.fBCastFlags)
    
    def export_script(self,script,refparser):
    
    
        receivers = list(FindInDict(script,'receivers',[]))
        refparser.ClearDefaultType()
        refparser.ClearAllowList()

        # receivers don't parse TagString's, since there are no default types....
        # you can use a tag in the RefString though, since the basepath should be set...
        
        for scriptkey in receivers:
            if type(scriptkey) == str:
                ref = refparser.RefString_FindCreateRef(scriptkey)
                if not ref.isNull():
                    self.fReceivers.append(ref)
        
        # for flags, take the plasma flags themselves - but don't really publish those....
        flags = list(FindInDict(script,'bcastflags',[]))

        if len(flags) > 0:
            self.fBCastFlags = 0
        for flag in flags:
            if plMessage.plBCastFlags.has_key(str(flag)):
                self.fBCastFlags |= plMessage.plBCastFlags[str(flag)]
        


class plActivatorMsg(plMessage):    # Message Type: 0x0219 - plActivatorMsg
    def __init__(self,parent=None,type=0x0219):
        plMessage.__init__(self,parent,type)
        self.member28 = 0
        self.member38 = Vertex()
    
    def read(self,buf):
        self.IMsgRead(buf)
        self.member28 = buf.Read32()
        self.member38.read(buf)
    
    
    def write(self,buf):
        self.IMsgWrite(buf)
        buf.Write32(self.member28)
        self.member38.write(buf)

class plArmatureEffectStateMsg(plMessage):
    Sounds = \
    { \
        "kFootDirt"             :  0, \
        "kFootPuddle"           :  1, \
        "kFootWater"            :  2, \
        "kFootTile"             :  3, \
        "kFootMetal"            :  4, \
        "kFootWoodBridge"       :  5, \
        "kFootRopeLadder"       :  6, \
        "kFootGrass"            :  7, \
        "kFootBrush"            :  8, \
        "kFootHardWood"         :  9, \
        "kFootRug"              : 10, \
        "kFootStone"            : 11, \
        "kFootMud"              : 12, \
        "kFootMetalLadder"      : 13, \
        "kFootWoodLadder"       : 14, \
        "kFootDeepWater"        : 15, \
        "kFootMaintainerGlass"  : 16, \
        "kFootMaintainerStone"  : 17, \
        "kFootSwimming"         : 18, \
        "kMaxSurface"           : 19, \
        "kFootNoSurface"        : 19  \
    }
    
    ScriptNames = \
    { \
        "dirt"              :  0, \
        "puddle"            :  1, \
        "water"             :  2, \
        "tile"              :  3, \
        "metal"             :  4, \
        "woodbridge"        :  5, \
        "ropeladder"        :  6, \
        "grass"             :  7, \
        "brush"             :  8, \
        "hardwood"          :  9, \
        "rug"               : 10, \
        "stone"             : 11, \
        "mud"               : 12, \
        "metalladder"       : 13, \
        "woodladder"        : 14, \
        "deepwater"         : 15, \
        "maintainerglass"   : 16, \
        "maintainerstone"   : 17, \
        "swimming"          : 18, \
    }


    def __init__(self,parent=None,type=0x38E):
        plMessage.__init__(self,parent,type)

        self.fBCastFlags |= plMessage.plBCastFlags["kNetPropagate"]
        self.fBCastFlags |= plMessage.plBCastFlags["kPropagateToModifiers"]

        self.fSurface = plArmatureEffectStateMsg.Sounds["kFootDirt"] # Default sound 
        self.fAddSurface = False
        
    def read(self,stream):
        self.IMsgRead(stream);
        self.fSurface = stream.ReadByte()
        self.fAddSurface = stream.ReadBool()
            
    def write(self,stream):
        self.IMsgWrite(stream)
        stream.WriteByte(self.fSurface)
        stream.WriteBool(self.fAddSurface)

    def export_script(self,script,refparser):
        plMessage.export_script(self,script,refparser)
        
        sfc = str(FindInDict(script,"surface","dirt")).lower()
        
        if not plArmatureEffectStateMsg.ScriptNames.has_key(sfc):
            sfc = "dirt"
        
        self.fSurface = plArmatureEffectStateMsg.ScriptNames[sfc]
        
        self.fAddSurface = bool(str(FindInDict(script,"append",self.fAddSurface)).lower() == "true")


class plNotifyMsg(plMessage):                     # Message Type: 0x02E8
    def __init__(self,parent=None,type=0x02E8):
        plMessage.__init__(self,parent,type)

        self.fBCastFlags |= plMessage.plBCastFlags["kNetPropagate"]

        self.fType = 0
        self.fState = 0
        self.fID = 0
        
        self.fEvents = []


    def read(self,stream):
        self.IMsgRead(stream)
        self.fType = stream.Read32()
        self.fState = stream.ReadFloat()
        self.fID = stream.Read32()
        
        count = stream.Read32()

        for i in range(count):
            event = proEventData.ReadFromStream(stream)
            self.fEvents.append(event)


    def write(self,stream):
        self.IMsgWrite(stream)
        stream.Write32(self.fType)
        stream.WriteFloat(self.fState)
        stream.Write32(self.fID)
        
        stream.Write32(len(self.fEvents))

        for event in self.fEvents:
            proEventData.WriteToStream(stream,event)


class plRefMsg(plMessage):                  # Message Type: 0x0203 - plRefMsg
    def __init__(self,parent=None,type=0x0203):
        plMessage.__init__(self,parent,type)
        if(parent == None):
            ver = 5
        else:
            ver = parent.getVersion()
        self.byte30 = 0
        self.reffed = UruObjectRef(ver)
        self.oldRef = UruObjectRef(ver)
    
    
    def read(self,buf):
        self.IMsgRead(buf)
        self.byte30 = buf.ReadByte()
        self.reffed.read(buf)
        self.oldRef.read(buf)
    
    
    def write(self,buf):
        self.IMsgWrite(buf)
        buf.WriteByte(self.byte30)
        self.reffed.write(buf)
    
    
    def changePageRaw(self,sid,did,stype,dtype):
        self.reffed.changePageRaw(sid,did,stype,dtype)
        self.oldRef.changePageRaw(sid,did,stype,dtype)


class plGenRefMsg(plRefMsg):                # Message Type: 0x0204 - plGenRefMsg
    def __init__(self,parent=None,type=0x0204):
        plRefMsg.__init__(self,parent,type)
        self.byte1 = 0
        self.byte2 = 0
    
    
    def read(self,buf):
        plRefMsg.read(self,buf)
        self.byte1 = buf.ReadByte()
        self.byte2 = buf.ReadByte()
    
    
    def write(self,buf):
        plRefMsg.write(self,buf)
        buf.WriteByte(self.byte1)
        buf.WriteByte(self.byte2)


class plExcludeRegionMsg(plMessage):            # Message Type: 0x0330 
    def __init__(self,parent=None,type=0x0330):
        plMessage.__init__(self,parent,type)
        self.member28 = 0
        self.member2C = 0
    
    
    def read(self,buf):
        self.IMsgRead(buf)
        self.member28 = buf.ReadByte()
        self.member2C = buf.Read32()
    
    def write(self,buf):
        self.IMsgWrite(buf)
        buf.WriteByte(self.member28)
        buf.Write32(self.member2C)
        
class plCameraMsg(plMessage):                   # Message Type: 0x020A - plCameraMsg
    ModCmds = \
    { \
        "kSetSubject"                           :  0, \
        "kCameraMod"                            :  1, \
        "kSetAsPrimary"                         :  2, \
        "kTransitionTo"                         :  3, \
        "kPush"                                 :  4, \
        "kPop"                                  :  5, \
        "kEntering"                             :  6, \
        "kCut"                                  :  7, \
        "kResetOnEnter"                         :  8, \
        "kResetOnExit"                          :  9, \
        "kChangeParams"                         : 10, \
        "kWorldspace"                           : 11, \
        "kCreateNewDefaultCam"                  : 12, \
        "kRegionPushCamera"                     : 13, \
        "kRegionPopCamera"                      : 14, \
        "kRegionPushPOA"                        : 15, \
        "kRegionPopPOA"                         : 16, \
        "kFollowLocalPlayer"                    : 17, \
        "kResponderTrigger"                     : 18, \
        "kSetFOV"                               : 19, \
        "kAddFOVKeyFrame"                       : 20, \
        "kStartZoomIn"                          : 21, \
        "kStartZoomOut"                         : 22, \
        "kStopZoom"                             : 23, \
        "kSetAnimated"                          : 24, \
        "kPythonOverridePush"                   : 25, \
        "kPythonOverridePop"                    : 26, \
        "kPythonOverridePushCut"                : 27, \
        "kPythonSetFirstPersonOverrideEnable"   : 28, \
        "kPythonUndoFirstPerson"                : 29, \
        "kUpdateCameras"                        : 20, \
        "kResponderSetThirdPerson"              : 31, \
        "kResponderUndoThirdPerson"             : 32, \
        "kNonPhysOn"                            : 33, \
        "kNonPhysOff"                           : 34, \
        "kResetPanning"                         : 35, \
        "kNumCmds"                              : 36  \
    }

    ScriptModCmds = \
    { \
        "setsubject"                           :  0, \
        "cameramod"                            :  1, \
        "setasprimary"                         :  2, \
        "transitionto"                         :  3, \
        "push"                                 :  4, \
        "pop"                                  :  5, \
        "entering"                             :  6, \
        "cut"                                  :  7, \
        "resetonenter"                         :  8, \
        "resetonexit"                          :  9, \
        "changeparams"                         : 10, \
        "worldspace"                           : 11, \
        "createnewdefaultCam"                  : 12, \
        "regionpushcamera"                     : 13, \
        "regionpopcamera"                      : 14, \
        "regionpushpoa"                        : 15, \
        "regionpoppoa"                         : 16, \
        "followlocalplayer"                    : 17, \
        "respondertrigger"                     : 18, \
        "setfov"                               : 19, \
        "addfovKeyFrame"                       : 20, \
        "startzoomIn"                          : 21, \
        "startzoomOut"                         : 22, \
        "stopzoom"                             : 23, \
        "setanimated"                          : 24, \
        "pythonoverridepush"                   : 25, \
        "pythonoverridepop"                    : 26, \
        "pythonoverridepushcut"                : 27, \
        "pythonsetfirstpersonoverrideenable"   : 28, \
        "pythonundofirstperson"                : 29, \
        "updatecameras"                        : 20, \
        "respondersetthirdperson"              : 31, \
        "responderundothirdperson"             : 32, \
        "nonphyson"                            : 33, \
        "nonphysoff"                           : 34, \
        "resetpanning"                         : 35, \
    }

    
    def __init__(self,parent=None,type=0x020A):
        plMessage.__init__(self,parent,type)

        self.fCmd = hsBitVector()
        self.fTransTime = 0
        self.fActivated = False
        self.fNewCam = UruObjectRef()
        self.fTriggerer = UruObjectRef()
        self.fConfig = plCameraConfig()
        self.fBCastFlags |= plMessage.plBCastFlags["kBCastByType"]

        self.fCmd.SetBit(plCameraMsg.ModCmds["kRegionPushCamera"])

    def read(self,stream):
        self.IMsgRead(stream)
    
        self.fCmd.read(stream)
        self.fTransTime = stream.ReadDouble()
        self.fActivated = stream.ReadBool()
        self.fNewCam.read(stream)
        self.fTriggerer.read(stream)
        self.fConfig.read(stream)

    def write(self,stream):
        self.IMsgWrite(stream)

        self.fCmd.write(stream)
        stream.WriteDouble(self.fTransTime)
        stream.WriteBool(self.fActivated)
        self.fNewCam.write(stream)
        self.fTriggerer.write(stream)
        self.fConfig.write(stream)

    def export_script(self,script,refparser):
        plMessage.export_script(self,script,refparser)

        configscript = dict(FindInDict(script,"config",{}))
        self.fConfig.export_script(script,refparser)

        newcamref = FindInDict(script,"newcam",None)

        refparser.SetDefaultType("scnobj")
        refparser.SetAllowList([0x0001,])
        self.fNewCam = refparser.MixedRef_FindCreateRef(newcamref)

        trigref = FindInDict(script,"triggerer",None)
        refparser.ClearDefaultType()
        refparser.ClearAllowList()
        self.fTriggerer = refparser.RefString_FindCreateRef(trigref)

        self.fTransTime = float(FindInDict(script,"transitiontime",self.fTransTime))
        self.fActivated = bool(str(FindInDict(script,"activated",str(self.fActivated))).lower() == "true")
        
        cmdlist = FindInDict(script,"cmds",None)
        if type(cmdlist) == list:
            self.fCmd = hsBitVector()
            for cmd in cmdlist:
                if cmd.lower() in plCameraMsg.ScriptModCmds:
                    cidx = plCameraMsg.ScriptModCmds[cmd.lower()]
                    self.fCmd.SetBit(cidx)
    

class plCameraConfig:
    Flags = \
    { \
        "kOffset"   : 0x1, \
        "kSpeeds"   : 0x2, \
        "kFOV"      : 0x4  \
    }
    
    def __init__(self):
        self.fAccel = 0
        self.fDecel = 0
        self.fVel = 0
        self.fFPAccel = 0
        self.fFPDecel = 0
        self.fFPVel = 0
        self.fFOVw = 0
        self.fFOVh = 0
        self.fOffset = alc_GeomClasses.Vertex()
        self.fWorldspace = False
    
    def read(self,stream):
        self.fAccel = stream.ReadFloat()
        self.fDecel = stream.ReadFloat()
        self.fVel = stream.ReadFloat()
        self.fFPAccel = stream.ReadFloat()
        self.fFPDecel = stream.ReadFloat()
        self.fFPVel = stream.ReadFloat()
        self.fFOVw = stream.ReadFloat()
        self.fFOVh = stream.ReadFloat()
        self.fOffset.read(stream)
        self.fWorldspace = stream.ReadBool()
    
    
    def write(self,stream):
        stream.WriteFloat(self.fAccel)
        stream.WriteFloat(self.fDecel)
        stream.WriteFloat(self.fVel)
        stream.WriteFloat(self.fFPAccel)
        stream.WriteFloat(self.fFPDecel)
        stream.WriteFloat(self.fFPVel)
        stream.WriteFloat(self.fFOVw)
        stream.WriteFloat(self.fFOVh)
        self.fOffset.write(stream)
        stream.WriteBool(self.fWorldspace)

    def export_script(self,script,refparser):
        self.fAccel = float(FindInDict(script,"accel",self.fAccel))
        self.fDecel = float(FindInDict(script,"decel",self.fDecel))
        self.fVel = float(FindInDict(script,"velocity",self.fVel))
        self.fFPAccel = float(FindInDict(script,"fpaccel",self.fFPAccel))
        self.fFPDecel = float(FindInDict(script,"fpdecel",self.fFPDecel))
        self.fFPVel = float(FindInDict(script,"fpvelocity",self.fFPVel))
        self.fFOVw = float(FindInDict(script,"fovw",self.fFOVw))
        self.fFOVh = float(FindInDict(script,"fovh",self.fFOVh))
        self.fWorldspace = bool(str(FindInDict(script,"worldspace",str(self.fWorldspace))).lower() == "true")

        offset = str(FindInDict(script,"offset","0,0,0"))
        try:
            X,Y,Z, = offset.split(',')
            self.fOffset = Vertex(float(X),float(Y),float(Z))
        except ValueError, detail:
            print "  Error parsing camera.brain.offset (Value:",offset,") : ",detail


class plSwimMsg(plMessage):
    def __init__(self,parent=None,type=0x0451):
        plMessage.__init__(self,parent,type)
        self.fBCastFlags |= plMessage.plBCastFlags["kPropagateToModifiers"]
        self.fIsEntering = False
        self.fSwimRegion = UruObjectRef()
        
    def read(self,stream):
        self.IMsgRead(stream)
        self.fIsEntering = stream.ReadBool()
        self.fSwimRegion.read(stream)
    
    def write(self,stream):
        self.IMsgWrite(stream);
        stream.WriteBool(self.fIsEntering)
        self.fSwimRegion.write(stream)

    def export_script(self,script,refparser):
        plMessage.export_script(self,script,refparser)
        pass

class plOneShotCallback:
    def __init__(self,parent):
        self.fMarker = ""
        self.fReceiver = UruObjectRef()
        self.fUser = 0 # Int32
        
        self.parent = parent

    def read(self,stream):
        self.fMarker = stream.ReadSafeString()
        self.fReceiver.read(stream)
        self.fUser = stream.Read16()
    
    def write(self,stream):
        stream.WriteSafeString(self.fMarker)
        self.fReceiver.write(stream)
        stream.Write16(self.fUser)

    def export_script(self,script,refparser):
        self.fMarker = str(FindInDict(script,"marker",""))
        ref = FindInDict(script,"receiver","/")
        if ref == "/":
            self.fReceiver = self.parent.parent.fSender
        else:
            refparser.SetDefaultType("respondermod")
            refparser.SetAllowList([]) # Type of OneShotMod
            self.rReceiver = refparser.RefString_FindCreateRef(ref)
        
        self.fUser = int(FindInDict(script,"user",0x00))

class plOneShotCallbacks:
    def __init__(self,parent):
        self.fCallbacks = []
        self.parent = parent
       
    def read(self,stream):
        count = stream.Read32()
        self.fCallbacks = []
        
        for i in range(count):
            cb = plOneShotCallback(self)
            cb.read(stream)
            self.fCallbacks.append(cb)

    def write(self,stream):
        stream.Write32(len(self.fCallbacks))
        
        for cb in self.fCallbacks:
            cb.write()
            
    def export_script(self,script,refparser):
        for cbscript in script:
            cb = plOneShotCallback()
            cb.export_script(cbscript,refparser)
            
class plOneShotMsg(plMessage):
    def __init__(self,parent=None,type=0x0302):
        plMessage.__init__(self,parent,type)
        self.fCallbacks = plOneShotCallbacks(self)
        
    def read(self,stream):
        self.IMsgRead(stream)
        self.fCallbacks.read(stream)
    
    def write(self,stream):
        self.IMsgWrite(stream)
        self.fCallbacks.write(stream)

    def export_script(self,script,refparser):
        plMessage.export_script(self,script,refparser)

        # Quick option to make it easier to set the receivers
        # does the same as setting it the default plmessage way
        refparser.SetDefaultType("oneshotmod")
        refparser.SetAllowList([0x0077]) # Type of OneShotMod

        receivers = list(FindInDict(script,'oneshotreceivers',[]))
        for keystr in receivers:
            # try to parse it as a tag or name if we have an associated sceneobj
            if type(keystr) != dict and type(keystr) != list:

                plref = refparser.MixedRef_FindCreateRef(keystr)
                if not plref.isNull():
                    self.fReceivers.append(plref)
        
        callbacks = list(FindInDict(script,'callbacks',[]))
        self.fCallbacks.export_script(callbacks,refparser)    

        refparser.ClearDefaultType()
        refparser.ClearAllowList()
        
class plMessageWithCallbacks(plMessage):
    def __init__(self,parent=None,type=0x0302):
        plMessage.__init__(self,parent,type)
        self.fCallbacks = []
        
    def read(self,stream):
        self.IMsgRead(stream)
        count = stream.Read32()
        
        for i in range(count):
            msg = PrpMessage.FromStream(stream)
            self.fCallbacks.append(msg)
    def write(self,stream):
        self.IMsgWrite(stream)

        stream.Write32(len(self.fCallbacks))
        for msg in self.fCallbacks:
            PrpMessage.ToStream(stream,msg)


class plSoundMsg(plMessageWithCallbacks):
    ModCmds = \
    { \
        "kPlay"              :  0, \
        "kStop"              :  1, \
        "kSetLooping"        :  2, \
        "kUnSetLooping"      :  3, \
        "kSetBegin"          :  4, \
        "kToggleState"       :  5, \
        "kAddCallbacks"      :  6, \
        "kRemoveCallbacks"   :  7, \
        "kGetStatus"         :  8, \
        "kNumSounds"         :  9, \
        "kStatusReply"       : 10, \
        "kGoToTime"          : 11, \
        "kSetVolume"         : 12, \
        "kSetTalkIcon"       : 13, \
        "kClearTalkIcon"     : 14, \
        "kSetFadeIn"         : 15, \
        "kSetFadeOut"        : 16, \
        "kIsLocalOnly"       : 17, \
        "kSelectFromGroup"   : 18, \
        "kNumCmds"           : 19, \
        "kFastForwardPlay"   : 10, \
        "kFastForwardToggle" : 21 \
    }
    
    FadeType = \
    { \
        "kLinear"       : 0, \
        "kLogarithmic"  : 1, \
        "kExponential"  : 2  \
    }
    
    def __init__(self,parent=None,type=0x0255):
        plMessageWithCallbacks.__init__(self,parent,type)
        self.fCmd = hsBitVector()
        self.fBegin = 0
        self.fEnd = 0
        self.fLoop = True
        self.fPlaying = True
        self.fSpeed = 1
        self.fTime = 0
        self.fIndex = 0
        self.fRepeats = 1
        self.fNameStr = 0
        self.fVolume = 1.0
        self.fFadeType = plSoundMsg.FadeType["kLinear"]
        
    def read(self,stream):
        plMessageWithCallbacks.read(self,stream)

        self.fCmd.read(stream)
        self.fBegin = stream.ReadDouble()
        self.fEnd = stream.ReadDouble()
        self.fLoop = stream.ReadBool()
        self.fPlaying = stream.ReadBool()
        self.fSpeed = stream.ReadFloat()
        self.fTime = stream.ReadDouble()
        self.fIndex = stream.Read32()
        self.fRepeats = stream.Read32()
        self.fNameStr = stream.Read32()
        self.fVolume = stream.ReadFloat()
        self.fFadeType = stream.ReadByte()    
        
    def write(self,stream):
        plMessageWithCallbacks.write(self,stream)

        self.fCmd.write(stream)
        stream.WriteDouble(self.fBegin)
        stream.WriteDouble(self.fEnd)
        stream.WriteBool(self.fLoop)
        stream.WriteBool(self.fPlaying)
        stream.WriteFloat(self.fSpeed)
        stream.WriteDouble(self.fTime)
        stream.Write32(self.fIndex)
        stream.Write32(self.fRepeats)
        stream.Write32(self.fNameStr)
        stream.WriteFloat(self.fVolume)
        stream.WriteByte(self.fFadeType)    

    def export_script(self,script,refparser):
        plMessage.export_script(self,script,refparser)


class plEnableMsg(plMessage):
    ModCmds = \
    { \
        "kDisable"   : 0, \
        "kEnable"    : 1, \
        "kDrawable"  : 2, \
        "kPhysical"  : 3, \
        "kAudible"   : 4, \
        "kAll"       : 5, \
        "kByType"    : 6, \
    }
    def __init__(self,parent=None,type=0x0255):
        plMessage.__init__(self,parent,type)
        self.fBCastFlags |= plMessage.plBCastFlags["kLocalPropagate"]
        self.fCmd = hsBitVector()
        self.fTypes = hsBitVector()
        
    def read(self,stream):
        self.IMsgRead(stream);

        self.fCmd.read(stream)
        self.fTypes.read(stream)   
        
    def write(self,stream):
        self.IMsgWrite(stream);

        self.fCmd.write(stream)
        self.fTypes.write(stream)    

    def export_script(self,script,refparser):
        plMessage.export_script(self,script,refparser)
        
        enable = bool(FindInDict(script,"enable","true"))
        if(enable):
            self.fCmd.SetBit(plEnableMsg.ModCmds["kEnable"])
        else:
            self.fCmd.SetBit(plEnableMsg.ModCmds["kDisable"])
        

def MsgKeyToMsgName(type):
    if   type == 0x0200:
        return "plObjRefMsg"
    elif type == 0x0201:
        return "plNodeRefMsg"
    elif type == 0x0202:
        return "plMessage"
    elif type == 0x0203:
        return "plRefMsg"
    elif type == 0x0204:
        return "plGenRefMsg"
    elif type == 0x0205:
        return "plTimeMsg"
    elif type == 0x0206:
        return "plAnimCmdMsg"
    elif type == 0x0207:
        return "plParticleUpdateMsg"
    elif type == 0x0208:
        return "plLayRefMsg"
    elif type == 0x0209:
        return "plMatRefMsg"
    elif type == 0x020A:
        return "plCameraMsg"
    elif type == 0x020B:
        return "plInputEventMsg"
    elif type == 0x020C:
        return "plKeyEventMsg"
    elif type == 0x020D:
        return "plMouseEventMsg"
    elif type == 0x020E:
        return "plEvalMsg"
    elif type == 0x020F:
        return "plTransformMsg"
    elif type == 0x0210:
        return "plControlEventMsg"
    elif type == 0x0211:
        return "plVaultCCRNode"
    elif type == 0x0212:
        return "plLOSRequestMsg"
    elif type == 0x0213:
        return "plLOSHitMsg"
    elif type == 0x0214:
        return "plSingleModMsg"
    elif type == 0x0215:
        return "plMultiModMsg"
    elif type == 0x0216:
        return "plPlayerMsg"
    elif type == 0x0217:
        return "plMemberUpdateMsg"
    elif type == 0x0218:
        return "plNetMsgPagingRoom"
    elif type == 0x0219:
        return "plActivatorMsg"
    elif type == 0x021A:
        return "plDispatch"
    elif type == 0x021B:
        return "plReceiver"
    elif type == 0x021C:
        return "plMeshRefMsg"
    elif type == 0x021D:
        return "hsGRenderProcs"
    elif type == 0x021E:
        return "hsSfxAngleFade"
    elif type == 0x021F:
        return "hsSfxDistFade"
    elif type == 0x0220:
        return "hsSfxDistShade"
    elif type == 0x0221:
        return "hsSfxGlobalShade"
    elif type == 0x0222:
        return "hsSfxIntenseAlpha"
    elif type == 0x0223:
        return "hsSfxObjDistFade"
    elif type == 0x0224:
        return "hsSfxObjDistShade"
    elif type == 0x0225:
        return "hsDynamicValue"
    elif type == 0x0226:
        return "hsDynamicScalar"
    elif type == 0x0227:
        return "hsDynamicColorRGBA"
    elif type == 0x0228:
        return "hsDynamicMatrix33"
    elif type == 0x0229:
        return "hsDynamicMatrix44"
    elif type == 0x022A:
        return "plController"
    elif type == 0x022B:
        return "plLeafController"
    elif type == 0x022C:
        return "plScaleController"
    elif type == 0x022D:
        return "plRotController"
    elif type == 0x022E:
        return "plPosController"
    elif type == 0x022F:
        return "plScalarController"
    elif type == 0x0230:
        return "plPoint3Controller"
    elif type == 0x0231:
        return "plScaleValueController"
    elif type == 0x0232:
        return "plQuatController"
    elif type == 0x0233:
        return "plMatrix33Controller"
    elif type == 0x0234:
        return "plMatrix44Controller"
    elif type == 0x0235:
        return "plEaseController"
    elif type == 0x0236:
        return "plSimpleScaleController"
    elif type == 0x0237:
        return "plSimpleRotController"
    elif type == 0x0238:
        return "plCompoundRotController"
    elif type == 0x0239:
        return "plSimplePosController"
    elif type == 0x023A:
        return "plCompoundPosController"
    elif type == 0x023B:
        return "plTMController"
    elif type == 0x023C:
        return "hsFogControl"
    elif type == 0x023D:
        return "plIntRefMsg"
    elif type == 0x023E:
        return "plCollisionReactor"
    elif type == 0x023F:
        return "plCorrectionMsg"
    elif type == 0x0240:
        return "plPhysicalModifier"
    elif type == 0x0241:
        return "plPickedMsg"
    elif type == 0x0242:
        return "plCollideMsg"
    elif type == 0x0243:
        return "plTriggerMsg"
    elif type == 0x0244:
        return "plInterestingModMsg"
    elif type == 0x0245:
        return "plDebugKeyEventMsg"
    elif type == 0x0246:
        return "plPhysicalProperties"
    elif type == 0x0247:
        return "plSimplePhys"
    elif type == 0x0248:
        return "plMatrixUpdateMsg"
    elif type == 0x0249:
        return "plCondRefMsg"
    elif type == 0x024A:
        return "plTimerCallbackMsg"
    elif type == 0x024B:
        return "plEventCallbackMsg"
    elif type == 0x024C:
        return "plSpawnModMsg"
    elif type == 0x024D:
        return "plSpawnRequestMsg"
    elif type == 0x024E:
        return "plLoadCloneMsg"
    elif type == 0x024F:
        return "plEnableMsg"
    elif type == 0x0250:
        return "plWarpMsg"
    elif type == 0x0251:
        return "plAttachMsg"
    elif type == 0x0252:
        return "pfConsole"
    elif type == 0x0253:
        return "plRenderMsg"
    elif type == 0x0254:
        return "plAnimTimeConvert"
    elif type == 0x0255:
        return "plSoundMsg"
    elif type == 0x0256:
        return "plInterestingPing"
    elif type == 0x0257:
        return "plNodeCleanupMsg"
    elif type == 0x0258:
        return "plSpaceTree"
    elif type == 0x0259:
        return "plNetMessage"
    elif type == 0x025A:
        return "plNetMsgJoinReq"
    elif type == 0x025B:
        return "plNetMsgJoinAck"
    elif type == 0x025C:
        return "plNetMsgLeave"
    elif type == 0x025D:
        return "plNetMsgPing"
    elif type == 0x025E:
        return "plNetMsgRoomsList"
    elif type == 0x025F:
        return "plNetMsgGroupOwner"
    elif type == 0x0260:
        return "plNetMsgGameStateRequest"
    elif type == 0x0261:
        return "plNetMsgSessionReset"
    elif type == 0x0262:
        return "plNetMsgOmnibus"
    elif type == 0x0263:
        return "plNetMsgObject"
    elif type == 0x0264:
        return "plCCRInvisibleMsg"
    elif type == 0x0265:
        return "plLinkInDoneMsg"
    elif type == 0x0266:
        return "plNetMsgGameMessage"
    elif type == 0x0267:
        return "plNetMsgStream"
    elif type == 0x0268:
        return "plAudioSysMsg"
    elif type == 0x0269:
        return "plDispatchBase"
    elif type == 0x026A:
        return "plServerReplyMsg"
    elif type == 0x026B:
        return "plDeviceRecreateMsg"
    elif type == 0x026C:
        return "plNetMsgStreamHelper"
    elif type == 0x026D:
        return "plNetMsgObjectHelper"
    elif type == 0x026E:
        return "plIMouseXEventMsg"
    elif type == 0x026F:
        return "plIMouseYEventMsg"
    elif type == 0x0270:
        return "plIMouseBEventMsg"
    elif type == 0x0271:
        return "plLogicTriggerMsg"
    elif type == 0x0272:
        return "plPipeline"
    elif type == 0x0273:
        return "plDX8Pipeline"
    elif type == 0x0274:
        return "plNetMsgVoice"
    elif type == 0x0275:
        return "plLightRefMsg"
    elif type == 0x0276:
        return "plNetMsgStreamedObject"
    elif type == 0x0277:
        return "plNetMsgSharedState"
    elif type == 0x0278:
        return "plNetMsgTestAndSet"
    elif type == 0x0279:
        return "plNetMsgGetSharedState"
    elif type == 0x027A:
        return "plSharedStateMsg"
    elif type == 0x027B:
        return "plNetGenericServerTask"
    elif type == 0x027C:
        return "plNetLookupServerGetAgeInfoFromVaultTask"
    elif type == 0x027D:
        return "plLoadAgeMsg"
    elif type == 0x027E:
        return "plMessageWithCallbacks"
    elif type == 0x027F:
        return "plClientMsg"
    elif type == 0x0280:
        return "plClientRefMsg"
    elif type == 0x0281:
        return "plNetMsgObjStateRequest"
    elif type == 0x0282:
        return "plCCRPetitionMsg"
    elif type == 0x0283:
        return "plVaultCCRInitializationTask"
    elif type == 0x0284:
        return "plNetServerMsg"
    elif type == 0x0285:
        return "plNetServerMsgWithContext"
    elif type == 0x0286:
        return "plNetServerMsgRegisterServer"
    elif type == 0x0287:
        return "plNetServerMsgUnregisterServer"
    elif type == 0x0288:
        return "plNetServerMsgStartProcess"
    elif type == 0x0289:
        return "plNetServerMsgRegisterProcess"
    elif type == 0x028A:
        return "plNetServerMsgUnregisterProcess"
    elif type == 0x028B:
        return "plNetServerMsgFindProcess"
    elif type == 0x028C:
        return "plNetServerMsgProcessFound"
    elif type == 0x028D:
        return "plNetMsgRoutingInfo"
    elif type == 0x028E:
        return "plNetServerSessionInfo"
    elif type == 0x028F:
        return "plSimulationMsg"
    elif type == 0x0290:
        return "plSimulationSynchMsg"
    elif type == 0x0291:
        return "plHKSimulationSynchMsg"
    elif type == 0x0292:
        return "plAvatarMsg"
    elif type == 0x0293:
        return "plAvTaskMsg"
    elif type == 0x0294:
        return "plAvSeekMsg"
    elif type == 0x0295:
        return "plAvOneShotMsg"
    elif type == 0x0296:
        return "plSatisfiedMsg"
    elif type == 0x0297:
        return "plNetMsgObjectListHelper"
    elif type == 0x0298:
        return "plNetMsgObjectUpdateFilter"
    elif type == 0x0299:
        return "plProxyDrawMsg"
    elif type == 0x029A:
        return "plSelfDestructMsg"
    elif type == 0x029B:
        return "plSimInfluenceMsg"
    elif type == 0x029C:
        return "plForceMsg"
    elif type == 0x029D:
        return "plOffsetForceMsg"
    elif type == 0x029E:
        return "plTorqueMsg"
    elif type == 0x029F:
        return "plImpulseMsg"
    elif type == 0x02A0:
        return "plOffsetImpulseMsg"
    elif type == 0x02A1:
        return "plAngularImpulseMsg"
    elif type == 0x02A2:
        return "plDampMsg"
    elif type == 0x02A3:
        return "plShiftMassMsg"
    elif type == 0x02A4:
        return "plSimStateMsg"
    elif type == 0x02A5:
        return "plFreezeMsg"
    elif type == 0x02A6:
        return "plEventGroupMsg"
    elif type == 0x02A7:
        return "plSuspendEventMsg"
    elif type == 0x02A8:
        return "plNetMsgMembersListReq"
    elif type == 0x02A9:
        return "plNetMsgMembersList"
    elif type == 0x02AA:
        return "plNetMsgMemberInfoHelper"
    elif type == 0x02AB:
        return "plNetMsgMemberListHelper"
    elif type == 0x02AC:
        return "plNetMsgMemberUpdate"
    elif type == 0x02AD:
        return "plNetMsgServerToClient"
    elif type == 0x02AE:
        return "plNetMsgCreatePlayer"
    elif type == 0x02AF:
        return "plNetMsgAuthenticateHello"
    elif type == 0x02B0:
        return "plNetMsgAuthenticateChallenge"
    elif type == 0x02B1:
        return "plConnectedToVaultMsg"
    elif type == 0x02B2:
        return "plCCRCommunicationMsg"
    elif type == 0x02B3:
        return "plNetMsgInitialAgeStateSent"
    elif type == 0x02B4:
        return "plInitialAgeStateLoadedMsg"
    elif type == 0x02B5:
        return "plNetServerMsgFindServerBase"
    elif type == 0x02B6:
        return "plNetServerMsgFindServerReplyBase"
    elif type == 0x02B7:
        return "plNetServerMsgFindAuthServer"
    elif type == 0x02B8:
        return "plNetServerMsgFindAuthServerReply"
    elif type == 0x02B9:
        return "plNetServerMsgFindVaultServer"
    elif type == 0x02BA:
        return "plNetServerMsgFindVaultServerReply"
    elif type == 0x02BB:
        return "plAvTaskSeekDoneMsg"
    elif type == 0x02BC:
        return "plAvatarSpawnNotifyMsg"
    elif type == 0x02BD:
        return "plNetServerMsgVaultTask"
    elif type == 0x02BE:
        return "plNetMsgVaultTask"
    elif type == 0x02BF:
        return "plAgeLinkStruct"
    elif type == 0x02C0:
        return "plVaultAgeInfoNode"
    elif type == 0x02C1:
        return "plNetMsgStreamableHelper"
    elif type == 0x02C2:
        return "plNetMsgReceiversListHelper"
    elif type == 0x02C3:
        return "plNetMsgListenListUpdate"
    elif type == 0x02C4:
        return "plNetServerMsgPing"
    elif type == 0x02C5:
        return "plNetMsgAlive"
    elif type == 0x02C6:
        return "plNetMsgTerminated"
    elif type == 0x02C7:
        return "plSDLModifierMsg"
    elif type == 0x02C8:
        return "plNetMsgSDLState"
    elif type == 0x02C9:
        return "plNetServerMsgSessionReset"
    elif type == 0x02CA:
        return "plCCRBanLinkingMsg"
    elif type == 0x02CB:
        return "plCCRSilencePlayerMsg"
    elif type == 0x02CC:
        return "plRenderRequestMsg"
    elif type == 0x02CD:
        return "plRenderRequestAck"
    elif type == 0x02CE:
        return "plNetMember"
    elif type == 0x02CF:
        return "plNetGameMember"
    elif type == 0x02D0:
        return "plNetTransportMember"
    elif type == 0x02D1:
        return "plConvexVolume"
    elif type == 0x02D2:
        return "plParticleGenerator"
    elif type == 0x02D3:
        return "plSimpleParticleGenerator"
    elif type == 0x02D4:
        return "plParticleEmitter"
    elif type == 0x02D5:
        return "plAGChannel"
    elif type == 0x02D6:
        return "plMatrixChannel"
    elif type == 0x02D7:
        return "plMatrixTimeScale"
    elif type == 0x02D8:
        return "plMatrixBlend"
    elif type == 0x02D9:
        return "plMatrixControllerChannel"
    elif type == 0x02DA:
        return "plQuatPointCombine"
    elif type == 0x02DB:
        return "plPointChannel"
    elif type == 0x02DC:
        return "plPointConstant"
    elif type == 0x02DD:
        return "plPointBlend"
    elif type == 0x02DE:
        return "plQuatChannel"
    elif type == 0x02DF:
        return "plQuatConstant"
    elif type == 0x02E0:
        return "plQuatBlend"
    elif type == 0x02E1:
        return "plLinkToAgeMsg"
    elif type == 0x02E2:
        return "plPlayerPageMsg"
    elif type == 0x02E3:
        return "plCmdIfaceModMsg"
    elif type == 0x02E4:
        return "plNetServerMsgPlsUpdatePlayer"
    elif type == 0x02E5:
        return "plListenerMsg"
    elif type == 0x02E6:
        return "plAnimPath"
    elif type == 0x02E7:
        return "plClothingUpdateBCMsg"
    elif type == 0x02E8:
        return "plNotifyMsg"
    elif type == 0x02E9:
        return "plFakeOutMsg"
    elif type == 0x02EA:
        return "plCursorChangeMsg"
    elif type == 0x02EB:
        return "plNodeChangeMsg"
    elif type == 0x02EC:
        return "plAvEnableMsg"
    elif type == 0x02ED:
        return "plLinkCallbackMsg"
    elif type == 0x02EE:
        return "plTransitionMsg"
    elif type == 0x02EF:
        return "plConsoleMsg"
    elif type == 0x02F0:
        return "plVolumeIsect"
    elif type == 0x02F1:
        return "plSphereIsect"
    elif type == 0x02F2:
        return "plConeIsect"
    elif type == 0x02F3:
        return "plCylinderIsect"
    elif type == 0x02F4:
        return "plParallelIsect"
    elif type == 0x02F5:
        return "plConvexIsect"
    elif type == 0x02F6:
        return "plComplexIsect"
    elif type == 0x02F7:
        return "plUnionIsect"
    elif type == 0x02F8:
        return "plIntersectionIsect"
    elif type == 0x02F9:
        return "plModulator"
    elif type == 0x02FA:
        return "plInventoryMsg"
    elif type == 0x02FB:
        return "plLinkEffectsTriggerMsg"
    elif type == 0x02FC:
        return "plLinkEffectBCMsg"
    elif type == 0x02FD:
        return "plResponderEnableMsg"
    elif type == 0x02FE:
        return "plNetServerMsgHello"
    elif type == 0x02FF:
        return "plNetServerMsgHelloReply"
    elif type == 0x0300:
        return "plNetServerMember"
    elif type == 0x0301:
        return "plResponderMsg"
    elif type == 0x0302:
        return "plOneShotMsg"
    elif type == 0x0303:
        return "plVaultAgeInfoListNode"
    elif type == 0x0304:
        return "plNetServerMsgServerRegistered"
    elif type == 0x0305:
        return "plPointTimeScale"
    elif type == 0x0306:
        return "plPointControllerChannel"
    elif type == 0x0307:
        return "plQuatTimeScale"
    elif type == 0x0308:
        return "plAGApplicator"
    elif type == 0x0309:
        return "plMatrixChannelApplicator"
    elif type == 0x030A:
        return "plPointChannelApplicator"
    elif type == 0x030B:
        return "plLightDiffuseApplicator"
    elif type == 0x030C:
        return "plLightAmbientApplicator"
    elif type == 0x030D:
        return "plLightSpecularApplicator"
    elif type == 0x030E:
        return "plOmniApplicator"
    elif type == 0x030F:
        return "plQuatChannelApplicator"
    elif type == 0x0310:
        return "plScalarChannel"
    elif type == 0x0311:
        return "plScalarTimeScale"
    elif type == 0x0312:
        return "plScalarBlend"
    elif type == 0x0313:
        return "plScalarControllerChannel"
    elif type == 0x0314:
        return "plScalarChannelApplicator"
    elif type == 0x0315:
        return "plSpotInnerApplicator"
    elif type == 0x0316:
        return "plSpotOuterApplicator"
    elif type == 0x0317:
        return "plNetServerMsgPlsRoutableMsg"
    elif type == 0x0318:
        return "_UNUSED_plPuppetBrainMsg"
    elif type == 0x0319:
        return "plATCEaseCurve"
    elif type == 0x031A:
        return "plConstAccelEaseCurve"
    elif type == 0x031B:
        return "plSplineEaseCurve"
    elif type == 0x031C:
        return "plVaultAgeInfoInitializationTask"
    elif type == 0x031D:
        return "pfGameGUIMsg"
    elif type == 0x031E:
        return "plNetServerMsgVaultRequestGameState"
    elif type == 0x031F:
        return "plNetServerMsgVaultGameState"
    elif type == 0x0320:
        return "plNetServerMsgVaultGameStateSave"
    elif type == 0x0321:
        return "plNetServerMsgVaultGameStateSaved"
    elif type == 0x0322:
        return "plNetServerMsgVaultGameStateLoad"
    elif type == 0x0323:
        return "plNetClientTask"
    elif type == 0x0324:
        return "plNetMsgSDLStateBCast"
    elif type == 0x0325:
        return "plReplaceGeometryMsg"
    elif type == 0x0326:
        return "plNetServerMsgExitProcess"
    elif type == 0x0327:
        return "plNetServerMsgSaveGameState"
    elif type == 0x0328:
        return "plDniCoordinateInfo"
    elif type == 0x0329:
        return "plNetMsgGameMessageDirected"
    elif type == 0x032A:
        return "plLinkOutUnloadMsg"
    elif type == 0x032B:
        return "plScalarConstant"
    elif type == 0x032C:
        return "plMatrixConstant"
    elif type == 0x032D:
        return "plAGCmdMsg"
    elif type == 0x032E:
        return "plParticleTransferMsg"
    elif type == 0x032F:
        return "plParticleKillMsg"
    elif type == 0x0330:
        return "plExcludeRegionMsg"
    elif type == 0x0331:
        return "plOneTimeParticleGenerator"
    elif type == 0x0332:
        return "plParticleApplicator"
    elif type == 0x0333:
        return "plParticleLifeMinApplicator"
    elif type == 0x0334:
        return "plParticleLifeMaxApplicator"
    elif type == 0x0335:
        return "plParticlePPSApplicator"
    elif type == 0x0336:
        return "plParticleAngleApplicator"
    elif type == 0x0337:
        return "plParticleVelMinApplicator"
    elif type == 0x0338:
        return "plParticleVelMaxApplicator"
    elif type == 0x0339:
        return "plParticleScaleMinApplicator"
    elif type == 0x033A:
        return "plParticleScaleMaxApplicator"
    elif type == 0x033B:
        return "plDynamicTextMsg"
    elif type == 0x033C:
        return "plCameraTargetFadeMsg"
    elif type == 0x033D:
        return "plAgeLoadedMsg"
    elif type == 0x033E:
        return "plPointControllerCacheChannel"
    elif type == 0x033F:
        return "plScalarControllerCacheChannel"
    elif type == 0x0340:
        return "plLinkEffectsTriggerPrepMsg"
    elif type == 0x0341:
        return "plLinkEffectPrepBCMsg"
    elif type == 0x0342:
        return "plAvatarInputStateMsg"
    elif type == 0x0343:
        return "plAgeInfoStruct"
    elif type == 0x0344:
        return "plSDLNotificationMsg"
    elif type == 0x0345:
        return "plNetClientConnectAgeVaultTask"
    elif type == 0x0346:
        return "plLinkingMgrMsg"
    elif type == 0x0347:
        return "plVaultNotifyMsg"
    elif type == 0x0348:
        return "plPlayerInfo"
    elif type == 0x0349:
        return "plSwapSpansRefMsg"
    elif type == 0x034A:
        return "pfKI"
    elif type == 0x034B:
        return "plDISpansMsg"
    elif type == 0x034C:
        return "plNetMsgCreatableHelper"
    elif type == 0x034D:
        return "plServerGuid"
    elif type == 0x034E:
        return "plNetMsgRequestMyVaultPlayerList"
    elif type == 0x034F:
        return "plDelayedTransformMsg"
    elif type == 0x0350:
        return "plSuperVNodeMgrInitTask"
    elif type == 0x0351:
        return "plElementRefMsg"
    elif type == 0x0352:
        return "plClothingMsg"
    elif type == 0x0353:
        return "plEventGroupEnableMsg"
    elif type == 0x0354:
        return "pfGUINotifyMsg"
    elif type == 0x0355:
        return "plAvBrain"
    elif type == 0x0356:
        return "plAvBrainUser"
    elif type == 0x0357:
        return "plAvBrainHuman"
    elif type == 0x0358:
        return "plAvBrainCritter"
    elif type == 0x0359:
        return "plAvBrainDrive"
    elif type == 0x035A:
        return "plAvBrainSample"
    elif type == 0x035B:
        return "plAvBrainGeneric"
    elif type == 0x035C:
        return "_UNUSED_plAvBrainPuppet"
    elif type == 0x035D:
        return "plAvBrainLadder"
    elif type == 0x035E:
        return "plInputIfaceMgrMsg"
    elif type == 0x035F:
        return "pfKIMsg"
    elif type == 0x0360:
        return "plRemoteAvatarInfoMsg"
    elif type == 0x0361:
        return "plMatrixDelayedCorrectionApplicator"
    elif type == 0x0362:
        return "plAvPushBrainMsg"
    elif type == 0x0363:
        return "plAvPopBrainMsg"
    elif type == 0x0364:
        return "plRoomLoadNotifyMsg"
    elif type == 0x0365:
        return "plAvTask"
    elif type == 0x0366:
        return "plAvAnimTask"
    elif type == 0x0367:
        return "plAvSeekTask"
    elif type == 0x0368:
        return "UNUSED_plAvBlendedSeekTask"
    elif type == 0x0369:
        return "plAvOneShotTask"
    elif type == 0x036A:
        return "plAvEnableTask"
    elif type == 0x036B:
        return "plAvTaskBrain"
    elif type == 0x036C:
        return "plAnimStage"
    elif type == 0x036D:
        return "plNetClientMember"
    elif type == 0x036E:
        return "plNetClientCommTask"
    elif type == 0x036F:
        return "plNetServerMsgAuthRequest"
    elif type == 0x0370:
        return "plNetServerMsgAuthReply"
    elif type == 0x0371:
        return "plNetClientCommAuthTask"
    elif type == 0x0372:
        return "plClientGuid"
    elif type == 0x0373:
        return "plNetMsgVaultPlayerList"
    elif type == 0x0374:
        return "plNetMsgSetMyActivePlayer"
    elif type == 0x0375:
        return "plNetServerMsgRequestAccountPlayerList"
    elif type == 0x0376:
        return "plNetServerMsgAccountPlayerList"
    elif type == 0x0377:
        return "plNetMsgPlayerCreated"
    elif type == 0x0378:
        return "plNetServerMsgVaultCreatePlayer"
    elif type == 0x0379:
        return "plNetServerMsgVaultPlayerCreated"
    elif type == 0x037A:
        return "plNetMsgFindAge"
    elif type == 0x037B:
        return "plNetMsgFindAgeReply"
    elif type == 0x037C:
        return "plNetClientConnectPrepTask"
    elif type == 0x037D:
        return "plNetClientAuthTask"
    elif type == 0x037E:
        return "plNetClientGetPlayerVaultTask"
    elif type == 0x037F:
        return "plNetClientSetActivePlayerTask"
    elif type == 0x0380:
        return "plNetClientFindAgeTask"
    elif type == 0x0381:
        return "plNetClientLeaveTask"
    elif type == 0x0382:
        return "plNetClientJoinTask"
    elif type == 0x0383:
        return "plNetClientCalibrateTask"
    elif type == 0x0384:
        return "plNetMsgDeletePlayer"
    elif type == 0x0385:
        return "plNetServerMsgVaultDeletePlayer"
    elif type == 0x0386:
        return "plNetCoreStatsSummary"
    elif type == 0x0387:
        return "plCreatableGenericValue"
    elif type == 0x0388:
        return "plCreatableListHelper"
    elif type == 0x0389:
        return "plCreatableStream"
    elif type == 0x038A:
        return "plAvBrainGenericMsg"
    elif type == 0x038B:
        return "plAvTaskSeek"
    elif type == 0x038C:
        return "plAGInstanceCallbackMsg"
    elif type == 0x038D:
        return "plArmatureEffectMsg"
    elif type == 0x038E:
        return "plArmatureEffectStateMsg"
    elif type == 0x038F:
        return "plShadowCastMsg"
    elif type == 0x0390:
        return "plBoundsIsect"
    elif type == 0x0391:
        return "plNetClientCommLeaveTask"
    elif type == 0x0392:
        return "plResMgrHelperMsg"
    elif type == 0x0393:
        return "plNetMsgAuthenticateResponse"
    elif type == 0x0394:
        return "plNetMsgAccountAuthenticated"
    elif type == 0x0395:
        return "plNetClientCommSendPeriodicAliveTask"
    elif type == 0x0396:
        return "plNetClientCommCheckServerSilenceTask"
    elif type == 0x0397:
        return "plNetClientCommPingTask"
    elif type == 0x0398:
        return "plNetClientCommFindAgeTask"
    elif type == 0x0399:
        return "plNetClientCommSetActivePlayerTask"
    elif type == 0x039A:
        return "plNetClientCommGetPlayerListTask"
    elif type == 0x039B:
        return "plNetClientCommCreatePlayerTask"
    elif type == 0x039C:
        return "plNetClientCommJoinAgeTask"
    elif type == 0x039D:
        return "plVaultAdminInitializationTask"
    elif type == 0x039E:
        return "plMultistageModMsg"
    elif type == 0x039F:
        return "plSoundVolumeApplicator"
    elif type == 0x03A0:
        return "plCutter"
    elif type == 0x03A1:
        return "plBulletMsg"
    elif type == 0x03A2:
        return "plDynaDecalEnableMsg"
    elif type == 0x03A3:
        return "plOmniCutoffApplicator"
    elif type == 0x03A4:
        return "plArmatureUpdateMsg"
    elif type == 0x03A5:
        return "plAvatarFootMsg"
    elif type == 0x03A6:
        return "plNetOwnershipMsg"
    elif type == 0x03A7:
        return "plNetMsgRelevanceRegions"
    elif type == 0x03A8:
        return "plParticleFlockMsg"
    elif type == 0x03A9:
        return "plAvatarBehaviorNotifyMsg"
    elif type == 0x03AA:
        return "plATCChannel"
    elif type == 0x03AB:
        return "plScalarSDLChannel"
    elif type == 0x03AC:
        return "plLoadAvatarMsg"
    elif type == 0x03AD:
        return "plAvatarSet"
    elif type == 0x03AE:
        return "plNetMsgLoadClone"
    elif type == 0x03AF:
        return "plNetMsgPlayerPage"
    elif type == 0x03B0:
        return "plVNodeInitTask"
    elif type == 0x03B1:
        return "plRippleShapeMsg"
    elif type == 0x03B2:
        return "plEventManager"
    elif type == 0x03B3:
        return "plVaultNeighborhoodInitializationTask"
    elif type == 0x03B4:
        return "plNetServerMsgAgentRecoveryRequest"
    elif type == 0x03B5:
        return "plNetServerMsgFrontendRecoveryRequest"
    elif type == 0x03B6:
        return "plNetServerMsgBackendRecoveryRequest"
    elif type == 0x03B7:
        return "plNetServerMsgAgentRecoveryData"
    elif type == 0x03B8:
        return "plNetServerMsgFrontendRecoveryData"
    elif type == 0x03B9:
        return "plNetServerMsgBackendRecoveryData"
    elif type == 0x03BA:
        return "plSubWorldMsg"
    elif type == 0x03BB:
        return "plMatrixDifferenceApp"
    else:
        return "Unknown Message"
