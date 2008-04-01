#
# $Id: alc_AnimClasses.py 658 2006-09-30 21:52:09Z AdamJohnso $
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
    try:
        from Blender import Mesh
        from Blender import Lamp
    except Exception, detail:
        print detail
except ImportError:
    pass

import md5, random, binascii, cStringIO, copy, Image, math, struct, StringIO, os, os.path, pickle
from alcurutypes import *
from alcdxtconv import *
from alchexdump import *
from alc_GeomClasses import *
from alc_Functions import *
from alcConvexHull import *
from alc_AbsClasses import *
from alc_VolumeIsect import *
from alc_CamClasses import *
from alc_ObjClasses import *
from alc_AlcScript import *

###Dynamic Decal###
class plDynaDecalMgr(plSynchedObject):
    def __init__(self,parent,name="unnamed",type=0x00E6):
        plSynchedObject.__init__(self,parent,name,type)
        
        self.fMatPreShade = UruObjectRef(self.getVersion())
        self.fMatRTShade = UruObjectRef(self.getVersion())
        self.fTargets = hsTArray()
        self.fPartyObjects = hsTArray()
        self.fMaxNumVerts = 0
        self.fMaxNumIdx = 0
        self.fWaitOnEnable = 0
        self.fIntensity = 0.0
        self.fWetLength = 0.0
        self.fRampEnd = 0.0
        self.fDecayStart = 0.0
        self.fLifeSpan = 0.0
        self.fGridSizeU = 0.0
        self.fGridSizeV = 0.0
        self.fScale = Vertex()
        self.fPartyTime = 0.0
        self.fNotifies = hsTArray()
    
    def _Find(page,name):
        return page.find(0x00E6,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x00E6,name,1)
    FindCreate = staticmethod(_FindCreate)
    
    
    def read(self, buf):
        plSynchedObject.read(self,buf)
        
        self.fMatPreShade.read(buf)
        self.fMatRTShade.read(buf)
        self.fTargets.ReadVector(buf)
        self.fPartyObjects.ReadVector(buf)
        self.fMaxNumVerts = buf.Read32()
        self.fMaxNumIdx = buf.Read32()
        self.fWaitOnEnable = buf.ReadFloat()
        self.fIntensity = buf.ReadFloat()
        self.fWetLength = buf.ReadFloat()
        self.fRampEnd = buf.ReadFloat()
        self.fDecayStart = buf.ReadFloat()
        self.fLifeSpan = buf.ReadFloat()
        self.fGridSizeU = buf.ReadFloat()
        self.fGridSizeV = buf.ReadFloat()
        self.fScale.read(buf)
        self.fPartyTime = buf.ReadFloat()
        self.fNotifies.ReadVector(buf)
    
    
    def write(self,s):
        plSynchedObject.write(self,s)
        
        self.fMatPreShade.write(s)
        self.fMatRTShade.write(s)
        self.fTargets.WriteVector(s)
        self.fPartyObjects.WriteVector(s)
        s.Write32(self.fMaxNumVerts)
        s.Write32(self.fMaxNumIdx)
        s.WriteFloat(self.fWaitOnEnable)
        s.WriteFloat(self.fIntensity)
        s.WriteFloat(self.fWetLength)
        s.WriteFloat(self.fRampEnd)
        s.WriteFloat(self.fDecayStart)
        s.WriteFloat(self.fLifeSpan)
        s.WriteFloat(self.fGridSizeU)
        s.WriteFloat(self.fGridSizeV)
        self.fScale.write(s)
        s.WriteFloat(self.fPartyTime)
        self.fNotifies.WriteVector(s)
    
    
    def import_obj(self, obj):
        script = AlcScript.objects.FindOrCreate(obj.name)
        
        if self.fMatPreShade.flag:
            StoreInDict(script, "decal.preshademat", self.fMatPreShade.Key.name)
        
        if self.fMatRTShade.flag:
            StoreInDict(script, "decal.rtshademat", self.fMatRTShade.Key.name)
        
        targets = []
        for i in range(len(self.fTargets)):
            if self.fTargets[i].flag:
                targets.append("scnobj:" + self.fTargets[i].Key.name)
        StoreInDict(script, "decal.targets", targets)
        
        objects = []
        for i in range(len(self.fPartyObjects)):
            if self.fPartyObjects[i].flag:
                objects.append("scnobj:" + self.fPartyObjects[i].Key.name)
        StoreInDict(script, "decal.objects", objects)
        
        rcvrs = []
        for i in range(len(self.fNotifies)):
            if self.fNotifies[i].flag:
                objects.append("0x%04X:" % self.fNotifies[i].object_type + self.fNotifies[i].Key.name)
        StoreInDict(script, "decal.notifies", rcvrs)
        
        #Cut the crap.
        StoreInDict(script, "decal.maxverts", self.fMaxNumVerts)
        StoreInDict(script, "decal.maxidx", self.fMaxNumIdx)
        StoreInDict(script, "decal.waitenable", self.fWaitOnEnable)
        StoreInDict(script, "decal.intensity", self.fIntensity)
        StoreInDict(script, "decal.wetlen", self.fWetLength)
        StoreInDict(script, "decal.rampend", self.fRampEnd)
        StoreInDict(script, "decal.decaystart", self.fDecayStart)
        StoreInDict(script, "decal.lifespan", self.fLifeSpan)
        StoreInDict(script, "decal.sizeu", self.fGridSizeU)
        StoreInDict(script, "decal.sizev", self.fGridSizeV)
        StoreInDict(script, "decal.partytime", self.fPartyTime)


class plDynaFootMgr(plDynaDecalMgr):
    def __init__(self,parent,name="unnamed",type=0x00E8):
        plDynaDecalMgr.__init__(self,parent,name,type)
        pass
    
    def _Find(page,name):
        return page.find(0x00E8,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x00E8,name,1)
    FindCreate = staticmethod(_FindCreate)
    
    def import_obj(self, obj):
        plDynaDecalMgr.import_obj(self, obj)
        
        script = AlcScript.objects.FindOrCreate(obj.name)
        StoreInDict(script, "decal.type", "DynaFoot")


class plDynaBulletMgr(plDynaDecalMgr):
    def __init__(self,parent,name="unnamed",type=0x00E8):
        plDynaDecalMgr.__init__(self,parent,name,type)
        pass
    
    def _Find(page,name):
        return page.find(0x00EA,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x00EA,name,1)
    FindCreate = staticmethod(_FindCreate)
    
    def import_obj(self, obj):
        plDynaDecalMgr.import_obj(self, obj)
        
        script = AlcScript.objects.FindOrCreate(obj.name)
        StoreInDict(script, "decal.type", "DynaBullet")

###Particle Systems###
class plParticleSystem(plModifier):
    
    EffectType = { \
                  "kEffectForce"        :  0x1, \
                  "kEffectMisc"         :  0x2, \
                  "kEffectConstraint"   :  0x4, \
    }
    
    def __init__(self,parent,name="unnamed",type=0x0008):
        plModifier.__init__(self,parent,name,type)
        
        self.fRef = UruObjectRef(self.getVersion())
        self.fAmbientCtl = None
        self.fDiffuseCtl = None
        self.fOpacityCtl = None
        self.fWidthCtl = None
        self.fHeightCtl = None
        self.fXTiles = 0
        self.fYTiles = 0
        self.fMaxTotal = 0
        self.fMaxEmitters = 0
        self.fPreSim = 0.0
        self.fAccel = Vertex()
        self.fWindMult = 0.0
        self.fNumValidEmitters = 0
        self.fEmitters = []
        self.fForces = hsTArray()
        self.fEffects = hsTArray()
        self.fConstraints = hsTArray()
        self.fPermaLights = hsTArray()
    
    def _Find(page,name):
        return page.find(0x0008,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0008,name,1)
    FindCreate = staticmethod(_FindCreate)

    
    def read(self,buf):
        plModifier.read(self,buf)
        
        self.fRef.read(buf)
        
        self.fAmbientCtl = PrpController(buf.Read16(), self.getVersion())
        self.fDiffuseCtl = PrpController(buf.Read16(), self.getVersion())
        self.fOpacityCtl = PrpController(buf.Read16(), self.getVersion())
        self.fWidthCtl = PrpController(buf.Read16(), self.getVersion())
        self.fHeightCtl = PrpController(buf.Read16(), self.getVersion())
        
        self.fXTiles = buf.Read32()
        self.fYTiles = buf.Read32()
        self.fMaxTotal = buf.Read32()
        self.fMaxTotalEmitters = buf.Read32()
        self.fPreSim = buf.ReadFloat()
        self.fAccel.read(buf)
        self.fWindMult = buf.ReadFloat()
        self.fNumValidEmitters = buf.Read32()
        
        for i in range(self.fNumValidEmitters):
            buf.Read16() #Garbage -- Class ID
            pem = plParticleEmitter()
            pem.read(buf)
            self.fEmitters.append(pem)
        
        self.fForces.ReadVector(buf)
        self.fEffects.ReadVector(buf)
        self.fConstraints.ReadVector(buf)
        self.fPermaLights.ReadVector(buf)


class plParticleEmitter:
    def __init__(self):
        pass
    
    def read(self,buf):
        raise "Can't read plParticleEmitter, yet..."


class plAnimStage:
    
    NotifyType = {
        "kNotifyEnter": 0x1,
        "kNotifyLoop": 0x2,
        "kNotifyAdvance": 0x4,
        "kNotifyRegress": 0x8
    }
    
    ForwardType = {
        "kForwardNone": 0,
        "kForwardKey": 1,
        "kForwardAuto": 2,
        "kForwardMax": 3
    }
    
    BackType = {
        "kBackNone": 0,
        "kBackKey": 1,
        "kBackAuto": 2,
        "kBackMax": 3
    }
    
    AdvanceType = {
        "kAdvanceNone": 0,
        "kAdvanceOnMove": 1,
        "kAdvanceAuto": 2,
        "kAdvanceOnAnyKey": 3,
        "kAdvanceMax": 4
    }

    RegressType = {
        "kAdvanceNone": 0,
        "kAdvanceOnMove": 1,
        "kAdvanceAuto": 2,
        "kAdvanceOnAnyKey": 3,
        "kAdvanceMax": 4
    }
    
    def __init__(self):
        self.fAnimName = "Unnamed Animation"
        self.fNotify = 0
        self.fForwardType = 0
        self.fBackType = 0
        self.fAdvanceType = 0
        self.fRegressType = 0
        self.fLoops = 0
        self.fDoAdvanceTo = 0
        self.fAdvanceTo = 0
        self.fDoRegressTo = 0
        self.fRegressTo = 0
    
    
    def read(self, s):
        self.fAnimName = s.ReadSafeString()
        self.fNotify = s.ReadByte()
        self.fForwardType = s.Read32()
        self.fBackType = s.Read32()
        self.fAdvanceType = s.Read32()
        self.fRegressType = s.Read32()
        self.fLoops = s.Read32()
        self.fDoAdvanceTo = s.ReadBool()
        self.fAdvanceTo = s.Read32()
        self.fDoRegressTo = s.ReadBool()
        self.fRegressTo = s.Read32()
    
    
    def write(self, s):
        s.WriteSafeString(self.fAnimName)
        s.WriteByte(self.fNotify)
        s.Write32(self.fForwardType)
        s.Write32(self.fBackType)
        s.Write32(self.fAdvanceType)
        s.Write32(self.fRegressType)
        s.Write32(self.fLoops)
        s.WriteBool(self.fDoAdvanceTo)
        s.Write32(self.fAdvanceTo)
        s.WriteBool(self.fDoRegressTo)
        s.Write32(self.fRegressTo)


###ATC Curve###
class PrpEaseCurve:
    def __init__(self,type=None,version=5):
        if (type == None):
            self.type = 0x8000
        else:
            self.type = type
        if(version != 5):
            self.data = None
            raise "Can only read Ease Curves for Uru. Myst 5 NOT SUPPORTED!!!"
        
        self.Key = plKey(5)
        
        if type == 0x0319:
            self.data = plATCEaseCurve(self)
        elif type == 0x031A:
            self.data = plConstAccelEaseCurve(self)
        elif type == 0x031B:
            self.data = plSplineEaseCurve(self)
        elif type == 0x8000: #NULL Creatable ;)
            self.data = None
        else:
            raise "Unexpected plCreatable Object Type [%04X] -- expected a plATCEaseCurve -- Sombody's on crack..." %type
       
    def read(self,buf):
        if self.data != None:
            self.data.read(buf)


    def write(self,buf):
        buf.Write16(self.type)
        if self.data != None:
            self.data.write(buf)


    def getVersion(self):
        return self.version


    def update(self,Key):
        self.Key.update(Key)


    def changePageRaw(self,sid,did,stype,dtype):
        self.Key.changePageRaw(sid,did,stype,dtype)
        if self.data != None:
            self.data.changePageRaw(sid,did,stype,dtype)


class plATCEaseCurve:
    def __init__(self, parent = None, type = 0x0319):
        #Insane Stuff
        self.parent = parent
        if parent == None:
            self.type = type
        else:
            self.type = parent.type
        
        #Plasma Stuff
        self.fMinLength = 0.0
        self.fMaxLength = 0.0
        self.fNormLength = 0.0
        self.fStartSpeed = 0.0
        self.fSpeed = 0.0
        self.fBeginWorldTime = 0.0
    
    
    def read(self, s):
        self.fMinLength = s.ReadFloat()
        self.fMaxLength = s.ReadFloat()
        self.fNormLength = s.ReadFloat()
        self.fStartSpeed = s.ReadFloat()
        self.fSpeed = s.ReadFloat()
        self.fBeginWorldTime = s.ReadDouble()
    
    
    def write(self, s):
        s.WriteFloat(self.fMinLength)
        s.WriteFloat(self.fMaxLength)
        s.WriteFloat(self.fNormLength)
        s.WriteFloat(self.fStartSpeed)
        s.WriteFloat(self.fSpeed)
        s.WriteDouble(self.fBeginWorldTime)


class plConstAccelEaseCurve(plATCEaseCurve):
    def __init__(self, parent = None, type = 0x031A):
        plATCEaseCurve.__init__(self, parent, type)
        pass


class plSplineEaseCurve(plATCEaseCurve):
    def __init__(self, parent = None, type = 0x031B):
        plATCEaseCurve.__init__(self, parent, type)
        self.fCoef = []
    
    
    def read(self, s):
        plATCEaseCurve.read(self, s)
        
        for i in range(4):
            self.fCoef[i] = s.ReadFloat()
    
    
    def write(self, s):
        plATCEaseCurve.write(self, s)
        
        for i in range(4):
            s.WriteFloat(self.fCoef[i])
    
###Controllers###
class PrpController:
    def __init__(self,type=None,version=5):
        if (type == None):
            self.ctrlType = 0x8000
        else:
            self.ctrlType = type
        if(version != 5):
            self.data = None
            raise "Can only read Controllers for Uru. Myst 5 NOT SUPPORTED!!!"
        
        self.Key = plKey(5)
        
        if type == 0x022A:
            self.data = plController(self)
        elif type == 0x022B:
            self.data = plLeafController(self)
        elif type == 0x022C:
            self.data = plScaleController(self)
        elif type == 0x022D:
            self.data = plRotController(self)
        elif type == 0x22F:
            self.data = plPosController(self)
        elif type == 0x022F:
            self.data = plScalarController(self)
        elif type == 0x0330:
            self.data = plPoint3Controller(self)
        elif type == 0x0331:
            self.data = plScaleValueController(self)
        elif type == 0x0232:
            self.data = plQuatController(self)
        elif type == 0x0233:
            self.data = plMatrix33Controller(self)
        elif type == 0x0234:
            self.data = plMatrix44Controller(self)
        elif type == 0x0235:
            self.data = plEaseController(self)
        elif type == 0x0236:
            self.data = plSimpleScaleController(self)
        elif type == 0x0237:
            self.data = plSimpleRotController(self)
        elif type == 0x0238:
            self.data = plCompundRotController(self)
        elif type == 0x0239:
            self.data = plSimplePosController(self)
        elif type == 0x023A:
            self.data = plCompoundPosController(self)
        elif type == 0x023B:
            self.data = plTMController(self)
        elif type == 0x8000: #NULL Creatable ;)
            self.data = None
        else:
            raise "Unexpected plCreatable Object Type [%04X] -- expected a plController -- Sombody's on crack..." %type

    def read(self,buf):
        if self.data != None:
            self.data.read(buf)


    def write(self,buf):
        buf.Write16(self.ctrlType)
        if self.data != None:
            self.data.write(buf)

    def getVersion(self):
        return self.version


    def update(self,Key):
        self.Key.update(Key)


    def changePageRaw(self,sid,did,stype,dtype):
        self.Key.changePageRaw(sid,did,stype,dtype)
        if self.data != None:
            self.data.changePageRaw(sid,did,stype,dtype)


class plController:
    def __init__(self,parent=None,type=0x022A):
        self.parent = parent
        if(parent == None):
            self.ctrlType = type
        else:
            self.ctrlType = parent.ctrlType
    
    


class plLeafController(plController):
    def __init__(self,parent=None,type=0x022B):
        plController.__init__(self,parent,type)
        self.i8 = 0
        self.fControllers = []
        self.garbage = 0
    
    def read(self,buf):
        self.i8 = buf.Read32()
        count = buf.Read32()
        for i in range(count):
            ctrl = plEaseController()
            ctrl.read(buf)
        self.garbage = buf.Read32()
    
    
    def write(self,buf):
        buf.Write32(self.i8)
        buf.Write32(len(self.fControllers))
        for i in self.fControllers:
            i.write(buf)
        buf.Write32(self.garbage)


class plScaleController(plController):
    
    Type = { \
            "kNullScaleController"      :  0x00, \
            "kSimpleScaleController"    :  0x01, \
    }
    
    def __init__(self,parent=None,type=0x022C):
        plController.__init__(self,parent,type)
        pass


class plRotController(plController):
    
    Type = { \
             "kNullRotController"       :  0x00, \
             "kSimpleRotController"     :  0x01, \
             "kUnusedRotController"     :  0x02, \
             "kCompoundRotController"   :  0x03, \
    }
    
    def __init__(self,parent=None,type=0x022D):
        plController.__init__(self,parent,type)
        pass


class plPosController(plController):
    
    Type = { \
             "kNullPosController"       :  0x00, \
             "kSimplePosController"     :  0x01, \
             "kCompoundPosController"   :  0x02, \
    }
    
    def __init__(self,parent=None,type=0x022E):
        plController.__init__(self,parent,type)
        pass


class plScalarController(plLeafController):
    def __init__(self,parent=None,type=0x022F):
        plLeafController.__init__(self,parent,type)
        self.fKeyList = None
    
    
    def read(self,buf):
        plLeafController.read(self,buf)
        if(buf.Read32() != 0):
            self.fKeyList = hsScalarKeyList()
            self.fKeyList.read(buf)
    
    
    def write(self,buf):
        plLeafController.write(self,buf)
        if(self.fKeyList == None):
            buf.Write32(0)
        else:
            buf.Write32(1)
            self.fKeyList.write(buf)


class plPoint3Controller(plLeafController):
    def __init__(self,parent=None,type=0x0230):
        plLeafController.__init__(self,parent,type)
        self.fKeyList = None
    
    
    def read(self,buf):
        plLeafController.read(self,buf)
        if(buf.Read32() != 0):
            self.fKeyList = hsPoint3KeyList()
            self.fKeyList.read(buf)
    
    
    def write(self,buf):
        plLeafController.write(self,buf)
        if(self.fKeyList == None):
            buf.Write32(0)
        else:
            buf.Write32(1)
            self.fKeyList.write(buf)


class plScaleValueController(plLeafController):
    def __init__(self,parent=None,type=0x0231):
        plLeafController.__init__(self,parent,type)
        self.fKeys = []
    
    
    def read(self,buf):
        plLeafController.read(self,buf)
        
        count = buf.Read32()
        for i in range(count):
            key = hsScaleKey()
            key.read(buf)
            self.fKeys.append(key)
    
    
    def write(self,buf):
        plLeafController.write(self,buf)
        
        buf.Write32(len(self.fKeys))
        for key in self.fKeys:
            key.write(buf)


class plQuatController(plLeafController):
    def __init__(self,parent=None,type=0x0232):
        plLeafController.__init__(self,parent,type)
        self.fKeys = []
    
    
    def read(self,buf):
        plLeafController.read(self,buf)
        
        count = buf.Read32()
        for i in range(count):
            quat = hsQuatKey()
            quat.read(buf)
            self.fKeys.append(quat)
    
    
    def write(self,buf):
        plLeafController.write(self,buf)
        
        buf.Write32(len(self.fKeys))
        for quat in self.fKeys:
            quat.write(buf)


class plMatrix33Controller(plLeafController):
    def __init__(self,parent=None,type=0x0233):
        plLeafController.__init__(self,parent,type)
        self.fKeys = []
    
    
    def read(self,buf):
        plLeafController.read(self,buf)
        
        count = buf.Read32()
        for i in range(count):
            key = hsMatrix33Key()
            key.read(buf)
            self.fKeys.append(key)
    
    
    def write(self,buf):
        plLeafController.write(self,buf)
        
        buf.Write32(len(self.fKeys))
        for key in self.fKeys:
            key.write(buf)


class plMatrix44Controller(plLeafController):
    def __init__(self,parent=None,type=0x0234):
        plLeafController.__init__(self,parent,type)
        self.fKeys = []
    
    
    def read(self,buf):
        plLeafController.read(self,buf)
        
        count = buf.Read32()
        for i in range(count):
            key = hsMatrix44Key()
            key.read(buf)
            self.fKeys.append(key)
    
    
    def write(self,buf):
        plLeafController.write(self,buf)
        
        buf.Write32(len(self.fKeys))
        for key in self.fKeys:
            key.write(buf)


class plEaseController(plLeafController):
    def __init__(self,parent=None,type=0x0235):
        plLeafController.__init__(self,parent,type)
        self.fKeyList = None
    
    
    def read(self,buf):
        plLeafController.read(self,buf)
        if(buf.Read32() != 0):
            self.fKeyList = hsEaseKeyList()
            self.fKeyList.read(buf)
    
    
    def write(self,buf):
        plLeafController.write(self,buf)
        if(self.fKeyList == None):
            buf.Write32(0)
        else:
            buf.Write32(1)
            self.fKeyList.write(buf)


class plSimpleScaleController(plScaleController):
    def __init__(self,parent=None,type=0x0236):
        plLeafController.__init__(self,parent,type)
        self.fValue = None
        
    
    def getType(self):
        return plScaleController.Type.kSimpleScaleController
    
    def read(self,buf):
        if(buf.Read32() != 0):
            self.fValue = plScaleValueControlle()
            self.fValue.read(buf)
    
    def write(self,buf):
        if(self.fValue == None):
            buf.Write32(0)
        else:
            buf.Write32(1)
            self.fValue.write(buf)


class plSimpleRotController(plRotController):
    def __init__(self,parent=None,type=0x0237):
        plRotController.__init__(self,parent,type)
        self.fValue = None
        
    
    def getType(self):
        return plRotController.Type.kSimpleRotController
    
    def read(self,buf):
        if (buf.Read32() != 0):
            self.fValue = plQuatController()
            self.fValue.read(buf)
    
    
    def write(self,buf):
        if (self.fValue != None):
            buf.Write32(1)
            self.fValue.write(buf)
        else:
            buf.Write32(0)


class plCompoundRotController(plRotController):
    def __init__(self,parent=None,type=0x0238):
        plRotController.__init__(self,parent,type)
        self.fXController = None
        self.fYController = None
        self.fZController = None
        
    
    def getType(self):
        return plRotController.Type.kCompoundRotController
    
    def read(self,buf):
        if (buf.Read32() != 0):
            self.fXController = plScalarController()
            self.fXController.read(buf)
        
        if (buf.Read32() != 0):
            self.fYController = plScalarController()
            self.fYController.read(buf)
        
        if (buf.Read32() != 0):
            self.fZController = plScalarController()
            self.fZController.read(buf)
    
    
    def write(self,buf):
        if(self.fXController != None):
            buf.Write32(1)
            self.fXController.write(buf)
        else:
            buf.Write32(0)
        
        if(self.fYController != None):
            buf.Write32(1)
            self.fYController.write(buf)
        else:
            buf.Write32(0)
    
        if(self.fZController != None):
            buf.Write32(1)
            self.fZController.write(buf)
        else:
            buf.Write32(0)


class plSimplePosController(plPosController):
    def __init__(self,parent=None,type=0x0239):
        plPosController.__init__(self,parent,type)
        self.fValue = None
    
    
    def getType(self):
        return plPosController.Type.kSimplePosController
    
    def read(self,buf):
        if (buf.Read32() != 0):
            self.fValue = plPoint3Controller()
            self.fValue.read(buf)
    
    
    def write(self,buf):
        if (self.fValue != None):
            buf.Write32(1)
            self.fValue.write(buf)
        else:
            buf.Write32(0)


class plCompoundPosController(plPosController):
    def __init__(self,parent=None,type=0x023A):
        plPosController.__init__(self,parent,type)
        self.fXController = None
        self.fYController = None
        self.fZController = None
    
    
    def getType(self):
        return plPosController.Type.kCompoundPosController
    
    
    def read(self,buf):
        if (buf.Read32() != 0):
            self.fXController = plScalarController()
            self.fXController.read(buf)
        
        if (buf.Read32() != 0):
            self.fYController = plScalarController()
            self.fYController.read(buf)
        
        if (buf.Read32() != 0):
            self.fZController = plScalarController()
            self.fZController.read(buf)
    
    
    def write(self,buf):
        if(self.fXController != None):
            buf.Write32(1)
            self.fXController.write(buf)
        else:
            buf.Write32(0)
        
        if(self.fYController != None):
            buf.Write32(1)
            self.fYController.write(buf)
        else:
            buf.Write32(0)
    
        if(self.fZController != None):
            buf.Write32(1)
            self.fZController.write(buf)
        else:
            buf.Write32(0)


class plTMController(plController):
    def __init__(self,parent=None,type=0x023B):
        plController.__init__(self,parent,type)
        self.fPosController = None
        self.fRotController = None
        self.fScaleController = None
    
    
    def read(self,buf):
        type = buf.Read32()
        if type == plPosController.Type.kCompoundPosController:
            self.fPosController = plCompoundPosController()
            self.fPosController.read(buf)
        elif type == plPosController.Type.kSimplePosController:
            self.fPosController = plSimplePosController()
            self.fPosController.read(buf)
        
        type = buf.Read32()
        if type == plRotController.Type.kCompoundRotController:
            self.fRotController = plCompoundRotController()
            self.fRotController.read(buf)
        elif type == plRotController.Type.kSimpleRotController:
            self.fRotController = plSimpleRotController()
            self.fRotController.read(buf)
        
        type = buf.Read32()
        if type == plScaleController.Type.kSimpleScaleController:
            self.fScaleController = plSimpleScaleController()
            self.fScaleController.read(buf)
    
    
    def write(self,buf):
        if self.fPosController != None:
            buf.Write32(self.fPosController.getType())
            self.fPosController.write(buf)
        else:
            buf.Write32(plPosController.Type.kNullPosController)
        
        if self.fRotController != None:
            buf.Write32(self.fRotController.getType())
            self.fRotController.write(buf)
        else:
            buf.Write32(plRotController.Type.kNullRotController)
        
        if self.fScaleController != None:
            buf.Write32(self.fScaleController.getType())
            self.fScaleController.write(buf)
        else:
            buf.Write32(plScaleController.Type.kNullScaleController)


###KeyFrame Classes###
class hsKeyFrame:
    
    kBezController = 0x02
    
    def __init__(self):
        self.fFlags = 0
        self.fFrameNum = 0
        self.fFrameTime = 0.0
    
    
    def read(self,buf):
        self.fFlags = buf.Read32()
        self.fFrameNum = buf.Read32()
        self.fFrameTime = buf.ReadFloat()
    
    
    def write(self,buf):
        buf.Write32(self.fFlags)
        buf.Write32(self.fFrameNum)
        buf.WriteFloat(self.fFrameTime)


class hsMatrix33Key(hsKeyFrame):
    def __init__(self):
        hsKeyFrame.__init__(self)
        self.fValue = hsMatrix33()
    
    
    def read(self,buf):
        hsKeyFrame.read(self,buf)
        self.fValue.read(buf)
    
    
    def write(self,buf):
        hsKeyFrame.write(self,buf)
        self.fValue.write(buf)


class hsMatrix44Key(hsKeyFrame):
    def __init__(self):
        hsKeyFrame.__init__(self)
        self.fValue = hsMatrix44()
    
    
    def read(self,buf):
        hsKeyFrame.read(self,buf)
        self.fValue.read(buf)
    
    
    def write(self,buf):
        hsKeyFrame.write(self,buf)
        self.fValue.write(buf)


class hsPoint3Key(hsKeyFrame):
    def __init__(self):
        hsKeyFrame.__init__(self)
        self.fInTan = Vertex()
        self.fOutTan = Vertex()
        self.fValue = Vertex()
    
    
    def read(self,buf):
        hsKeyFrame.read(self,buf)
        if(self.fFlags & hsKeyFrame.kBezController):
            self.fInTan.read(buf)
            self.fOutTan.read(buf)
        
        self.fValue.read(buf)
    
    
    def write(self,buf):
        hsKeyFrame.write(self,buf)
        if(self.fFlags & hsKeyFrame.kBezController):
            self.fInTan.write(buf)
            self.fOutTan.write(buf)
        
        self.fValue.write(buf)
    

class hsQuatKey(hsKeyFrame):
    def __init__(self):
        hsKeyFrame.__init__(self)
        self.fValue = hsQuat()
    
    
    def read(self,buf):
        hsKeyFrame.read(self,buf)
        self.fValue.read(buf)
    
    
    def write(self,buf):
        hsKeyFrame.write(self,buf)
        self.fValue.write(buf)


class hsScalarKey(hsKeyFrame):
    def __init__(self):
        hsKeyFrame.__init__(self)
        self.fInTan = Vertex()
        self.fOutTan = Vertex()
        self.fValue = 0.0
    
    
    def read(self,buf):
        hsKeyFrame.read(self,buf)
        if(self.fFlags & hsKeyFrame.kBezController):
            self.fInTan.read(buf)
            self.fOutTan.read(buf)
        
        self.fValue = buf.ReadFloat()
    
    
    def write(self,buf):
        hsKeyFrame.write(self,buf)
        if(self.fFlags & hsKeyFrame.kBezController):
            self.fInTan.write(buf)
            self.fOutTan.write(buf)
        
        buf.WriteFloat(self.fValue)


class hsScaleKey(hsKeyFrame):
    def __init__(self):
        hsKeyFrame.__init__(self)
        self.fInTan = Vertex()
        self.fOutTan = Vertex()
        self.fValue = hsScaleValue()
    
    
    def read(self,buf):
        hsKeyFrame.read(self,buf)
        if(self.fFlags & hsKeyFrame.kBezController):
            self.fInTan.read(buf)
            self.fOutTan.read(buf)
        
        self.fValue.read(buf)
    
    
    def write(self,buf):
        hsKeyFrame.write(self,buf)
        if(self.fFlags & hsKeyFrame.kBezController):
            self.fInTan.write(buf)
            self.fOutTan.write(buf)
        
        self.fValue.write(buf)


class hsEaseKeyList:
    def __init__(self):
        self.fKeys = []
    
    def read(self, buf):
        count = buf.Read32()
        for i in range(count):
            key = hsScalarKey()
            key.read(buf)
            self.fKeys.append(key)
    
    
    def write(self, buf):
        buf.Write32(len(self.fKeys))
        for key in self.fKeys:
            key.write(buf)


class hsScalarKeyList(hsEaseKeyList): #They're the same friggen thing.
    pass


class hsPoint3KeyList:
    def __init__(self):
        self.fKeys = []
    
    def read(self, buf):
        count = buf.Read32()
        for i in range(count):
            key = hsPoint3Key()
            key.read(buf)
            self.fKeys.append(key)
    
    
    def write(self, buf):
        buf.Write32(len(self.fKeys))
        for key in self.fKeys:
            key.write(buf)


class hsScaleValue:
    def __init__(self):
        self.fS = Vertex()
        self.fQ = hsQuat()
    
    
    def read(self,buf):
        self.fS.read(buf)
        self.fQ.read(buf)
    
    
    def write(self,buf):
        self.fS.write(buf)
        self.fQ.write(buf)


###OLD--MOVED STUFF###
class plAGApplicator:
    def __init__(self):
        self.bool = 0
        self.str = 0
    
    def read(self,buf):
        self.bool = buf.ReadBool()
        self.str = buf.ReadSafeString()
    
    
    def write(self,buf):
        buf.WriteBool(self.bool)
        buf.WriteSafeString(self.str)


class plAnimTimeConvert:
    plAnimTimeFlags = \
    { \
        "kNone"        : 0x0,  \
        "kStopped"     : 0x1,  \
        "kLoop"        : 0x2,  \
        "kBackwards"   : 0x4,  \
        "kWrap"        : 0x8,  \
        "kNeedsReset"  : 0x10, \
        "kEasingIn"    : 0x20, \
        "kForcedMove"  : 0x40, \
        "kNoCallbacks" : 0x80, \
        "kFlagsMask"   : 0xFF  \
    }
    
    def __init__(self,parent=None,type=0x0254,version = 5):
        self.fFlags = 0
        self.fBegin = 0.0
        self.fEnd = 0.0
        self.fLoopEnd = 0.0
        self.fLoopBegin = 0.0
        self.fSpeed = 1.0
        self.fCurrentAnimTime = 0.0
        self.fLastEvalWorldTime = 0.0
        self.fCommandList = [] # plMessages
        self.fStopPoints = []
        self.version = version
    
    def read(self, stream):
        self.fFlags = stream.Read32()
        self.fBegin = stream.ReadFloat()
        self.fEnd = stream.ReadFloat()
        self.fLoopEnd = stream.ReadFloat()
        self.fLoopBegin = stream.ReadFloat()
        self.fSpeed = stream.ReadFloat()
        self.fEaseInCurve = PrpEaseCurve(stream.Read16(), self.getVersion())
        self.fEaseInCurve.read(stream)
        self.fEaseOutCurve = PrpEaseCurve(stream.Read16(), self.getVersion())
        self.fEaseOutCurve.read(stream)
        self.fSpeedEaseCurve = PrpEaseCurve(stream.Read16(), self.getVersion())
        self.fSpeedEaseCurve.read(stream)
        self.fCurrentAnimTime = stream.ReadFloat()
        self.fLastEvalWorldTime = stream.ReadDouble()
        
        count = stream.Read32()

        # we now should read in a message queue, which is hard because of incomplete message implementations
        
        
        try:
            for i in range(count):
                Msg = PrpMessage.FromStream(stream)
                self.fCommandList.add(Msg.data)

        except ValueError, detail:
            print "/---------------------------------------------------------"
            print "|  WARNING:"
            print "|   Got Value Error:" , detail, ":"
            print "|   While reading message arrays of plAnimTimeConvert..."
            print "|   Unknown message type not implemented."
            print "|   ABORTING!!!"
            print "\---------------------------------------------------------\n"
            raise RuntimeError, "Unknown message type not implemented"
        
        count = stream.Read32()
        for i in range(count):
            self.fStopPoints.append(stream.ReadFloat())
    
    def write(self, stream):
        stream.Write32(self.fFlags)
        stream.WriteFloat(self.fBegin)
        stream.WriteFloat(self.fEnd)
        stream.WriteFloat(self.fLoopEnd)
        stream.WriteFloat(self.fLoopBegin)
        stream.WriteFloat(self.fSpeed)
        
        stream.Write16(0x8000)
        stream.Write16(0x8000)
        stream.Write16(0x8000)
        
        stream.WriteFloat(self.fCurrentAnimTime)
        stream.WriteDouble(self.fLastEvalWorldTime)
        
        stream.Write32(0)
        
        stream.Write32(len(self.fStopPoints))
        for i in self.fStopPoints:
            stream.WriteFloat(i)

    def getVersion(self):
        return self.version
