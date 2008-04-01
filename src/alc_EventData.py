#
# $Id: alc_EventData.py 455 2006-08-04 20:18:42Z Trylon $
#
#    Copyright (C) 2005-2006  Alcugs pyprp Project Team
#    See the file AUTHORS for more info about the team
#
#    This program is free software you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    Please see the file COPYING for the full license.
#    Please see the file DISCLAIMER for more details, before doing nothing.
#

import struct

from alc_GeomClasses import *
from alcurutypes import *
from alc_AbsClasses import *
from alc_RefParser import *
import alcconfig, alchexdump, alc_GeomClasses


class proEventData:

    eventType = \
    { \
        "kCollision"            :  1, \
        "kPicked"               :  2, \
        "kControlKey"           :  3, \
        "kVariable"             :  4, \
        "kFacing"               :  5, \
        "kContained"            :  6, \
        "kActivate"             :  7, \
        "kCallback"             :  8, \
        "kResponderState"       :  9, \
        "kMultiStage"           : 10, \
        "kSpawned"              : 11, \
        "kClickDrag"            : 12, \
        "kCoop"                 : 13, \
        "kOfferLinkingBook"     : 14, \
        "kBook"                 : 15, \
        "kClimbingBlockerHit"   : 16, \
        "kNone"                 : 17, \
    }
    
    dataType = \
    { \
        "kNumber"               : 1, \
        "kKey"                  : 2, \
        "kNotta"                : 3, \
    }
    
    multiStageEventType = \
    { \
        "kEnterStage"           : 1, \
        "kBeginningOfLoop"      : 2, \
        "kAdvanceNextStage"     : 3, \
        "kRegressPrevStage"     : 4, \
        "kNothing"              : 5, \
    }
    
    def __init__(self):
        self.fEventType = proEventData.eventType["kNone"]        

    def _Create(typenum):
          if   typenum == proEventData.eventType["kCollision"]:
            return proCollisionEventData()
          elif typenum == proEventData.eventType["kPicked"]:
            return proPickedEventData()
          elif typenum == proEventData.eventType["kControlKey"]:
            return proControlKeyEventData()
          elif typenum == proEventData.eventType["kVariable"]:
            return proVariableEventData()
          elif typenum == proEventData.eventType["kFacing"]:
            return proFacingEventData()
          elif typenum == proEventData.eventType["kContained"]:
            return proContainedEventData()
          elif typenum == proEventData.eventType["kActivate"]:
            return proActivateEventData()
          elif typenum == proEventData.eventType["kCallback"]:
            return proCallbackEventData()
          elif typenum == proEventData.eventType["kResponderState"]:
            return proResponderStateEventData()
          elif typenum == proEventData.eventType["kMultiStage"]:
            return proMultiStageEventData()
          elif typenum == proEventData.eventType["kSpawned"]:
            return proSpawnedEventData()
          elif typenum == proEventData.eventType["kClickDrag"]:
            return None
          elif typenum == proEventData.eventType["kCoop"]:
            return proCoopEventData()
          elif typenum == proEventData.eventType["kOfferLinkingBook"]:
            return proOfferLinkingBookEventData()
          elif typenum == proEventData.eventType["kBook"]:
            return proBookEventData()
          elif typenum == proEventData.eventType["kClimbingBlockerHit"]:
            return proClimbingBlockerHitEventData()
          else:
            return None
        
    Create = staticmethod(_Create)
        
    def _ReadFromStream(stream):
        _type = stream.Read32()
        event = proEventData.Create(_type)
        if not event is None:
            event.IRead(stream)
        return event
    
    ReadFromStream = staticmethod(_ReadFromStream)

    def _WriteToStream(stream,event):
        if not event is None:
            stream.Write32(event.fEventType)
            event.IWrite(stream)
        else:
            stream.Write32(proEventData.eventType["kNone"])

    WriteToStream = staticmethod(_WriteToStream)
    
    def IRead(self,stream): 
        pass
    def IWrite(self,stream):
        pass
        
class proActivateEventData(proEventData):
    def __init__(self):
        self.fEventType = proEventData.eventType["kActivate"]        
        self.fActive = False
        self.fActivate = False
        
    def IRead(self,stream):
        self.fActive = stream.ReadBool()
        self.fActivate = stream.ReadBool()
    
    def IWrite(self,stream):
        stream.WriteBool(self.fActive)
        stream.WriteBool(self.fActivate)
    

class proBookEventData(proEventData):
    def __init__(self):
        self.fEventType = proEventData.eventType["kBook"]        
        self.fEvent = 0
        self.fLinkID = 0

    def IRead(self,stream):
        self.fEvent = stream.Read32()
        self.fLinkID = stream.Read32()
    
    def IWrite(self,stream):
        stream.Write32(self.fEvent)
        stream.Write32(self.fLinkID)
    

class proCallbackEventData(proEventData):
    def __init__(self):
        self.fEventType = proEventData.eventType["kCallback"]        
        self.fEventTypeCb = proEventData.eventType["kNone"]        

    def IRead(self,stream):
        self.fEventTypeCb = stream.Read32()
    
    def IWrite(self,stream):
        stream.Write32(self.fEventTypeCb)
    

class proClickDragEventData(proEventData):
    def __init__(self):
        self.fEventType = proEventData.eventType["kClickDrag"]

class proClimbingBlockerHitEventData(proEventData):
    def __init__(self):
        self.fEventType = proEventData.eventType["kClimbingBlockerHit"]        
        self.fBlockerKey = UruObjectRef()

    def IRead(self,stream):
        self.fBlockerKey.read(stream)
    
    
    def IWrite(self,stream):
        self.fBlockerKey.write(stream)
    

class proCollisionEventData(proEventData):
    def __init__(self):
        self.fEventType = proEventData.eventType["kCollision"]        
        self.fHitter = UruObjectRef()
        self.fHittee = UruObjectRef()
        self.fEnter = False
        
    def IRead(self,stream):
        self.fEnter = stream.ReadBool()
        self.fHitter.read(stream)
        self.fHittee.read(stream)
    
    
    def IWrite(self,stream):
        stream.WriteBool(self.fEnter)
        self.fHitter.write(stream) 
        self.fHittee.write(stream) 
    

class proContainedEventData(proEventData):
    def __init__(self):
        self.fEventType = proEventData.eventType["kContained"]        
        self.fContained = UruObjectRef()
        self.fContainer = UruObjectRef()
        self.fEntering = False
        
    def IRead(self,stream):
        self.fContained.read(stream)
        self.fContainer.read(stream)
        self.fEntering = stream.ReadBool()
    
    
    def IWrite(self,stream):
        self.fContained.write(stream) 
        self.fContainer.write(stream) 
        stream.WriteBool(self.fEntering)
    

class proControlKeyEventData(proEventData):
    def __init__(self):
        self.fEventType = proEventData.eventType["kControlKey"]        
        self.fControlKey = 0
        self.fDown = False

    def IRead(self,stream):
        self.fControlKey = stream.Read32()
        self.fDown = stream.ReadBool()
    
    
    def IWrite(self,stream):
        stream.Write32(self.fControlKey)
        stream.WriteBool(self.fDown)
    

class proCoopEventData(proEventData):
    def __init__(self):
        self.fEventType = proEventData.eventType["kCoop"]        
        self.fID = 0
        self.fSerial = 0

    def IRead(self,stream):
        self.fID = stream.Read32()
        self.fSerial = stream.Read16()
    
    
    def IWrite(self,stream):
        stream.Write32(self.fID)
        stream.Write16(self.fSerial)
    

class proFacingEventData(proEventData):
    def __init__(self):
        self.fEventType = proEventData.eventType["kFacing"]        
        self.fFacer = UruObjectRef()
        self.fFacee = UruObjectRef()
        self.dot = 0
        self.enabled = False
        
    def IRead(self,stream):
        self.fFacer.read(stream)
        self.fFacee.read(stream)
        self.dot = stream.ReadFloat()
        self.enabled = stream.ReadBool()
    
    
    def IWrite(self,stream):
        self.fFacer.write(stream) 
        self.fFacee.write(stream) 
        stream.WriteFloat(self.dot)
        stream.WriteBool(self.enabled)
    

class proMultiStageEventData(proEventData):
    def __init__(self):
        self.fEventType = proEventData.eventType["kMultiStage"]        
        self.fAvatar = UruObjectRef()
        self.fStage = 0
        self.fEvent = proEventData.multiStageEventType["kNothing"]

    def IRead(self,stream):
        self.fStage = stream.Read32()
        self.fEvent = stream.Read32()
        self.fAvatar.read(stream)
    
    def IWrite(self,stream):
        stream.Write32(self.fStage)
        stream.Write32(self.fEvent)
        self.fAvatar.write(stream) 
    

class proOfferLinkingBookEventData(proEventData):
    def __init__(self):
        self.fEventType = proEventData.eventType["kOfferLinkingBook"]        
        self.offerer = UruObjectRef()
        self.targetAge = 0
        self.offeree = 0

    def IRead(self,stream):
        self.offerer.read(stream)
        self.targetAge = stream.Read32()
        self.offeree = stream.Read32()
    
    def IWrite(self,stream):
        self.offerer.write(stream) 
        stream.Write32(self.targetAge)
        stream.Write32(self.offeree)
    

class proPickedEventData(proEventData):
    def __init__(self):
        self.fEventType = proEventData.eventType["kPicked"]        
        self.fPicker = UruObjectRef()
        self.fPicked = UruObjectRef()
        self.fEnabled = False
        self.fHitPoint = Vertex() # not really, but close enough :)
        
    def IRead(self,stream):
        self.fPicker.read(stream)
        self.fPicked.read(stream)
        self.fEnabled = stream.ReadBool()
        self.fHitPoint.read(stream)
    
    def IWrite(self,stream):
        self.fPicker.write(stream) 
        self.fPicked.write(stream) 
        stream.WriteBool(self.fEnabled)
        self.fHitPoint.write(stream)

class proResponderStateEventData(proEventData):
    def __init__(self):
        self.fEventType = proEventData.eventType["kResponderState"]        
        self.fState = 0

    def IRead(self,stream):
        self.fState = stream.Read32()
    
    def IWrite(self,stream):
        stream.Write32(self.fState)
    

class proSpawnedEventData(proEventData):
    def __init__(self):
        self.fEventType = proEventData.eventType["kSpawned"]
        self.fSpawner = UruObjectRef()
        self.fSpawnee = UruObjectRef()

    def IRead(self,stream):
        self.fSpawner.read(stream)
        self.fSpawnee.read(stream)
    
    
    def IWrite(self,stream):
        self.fSpawner.write(stream) 
        self.fSpawnee.write(stream) 
    

class proVariableEventData(proEventData):
    def __init__(self):
        self.fEventType = proEventData.eventType["kVariable"]        
        self.fKey = UruObjectRef()
        self.fDataType = 0
        self.fNumber = 0.0

    def IRead(self,stream):
        self.fName = stream.ReadSafeString()
        self.fDataType = stream.Read32()
        self.fNumber = stream.ReadFloat()
        self.fKey.read(stream)
    
    
    def IWrite(self,stream):
        stream.WriteSafeString(self.fName)
        stream.Write32(self.fDataType)
        stream.WriteFloat(self.fNumber)
        self.fKey.write(stream) 
    

