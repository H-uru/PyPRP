#
# $Id: alc_Classes.py 876 2007-12-15 22:15:11Z Paradox $
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
from alchexdump import *
from alc_GeomClasses import *
from alc_Functions import *
from alc_AbsClasses import *
from alc_VolumeIsect import *
from alc_AlcScript import *
from alc_Messages import *


import alcconfig, alchexdump
def stripIllegalChars(name):
    name=name.replace("*","_")
    name=name.replace("?","_")
    name=name.replace("\\","_")
    name=name.replace("/","_")
    name=name.replace("<","_")
    name=name.replace(">","_")
    name=name.replace(":","_")
    name=name.replace("\"","_")
    name=name.replace("|","_")
    name=name.replace("#","_")
    name=name.strip()
    return name
    


class plSimpleRegionSensor(plSingleModifier):

    def __init__(self,parent,name="unnamed",type=0x0107):
        plSingleModifier.__init__(self,parent,name,type)
        
        self.fEnterMessage = None
        self.fExitMessage = None

    def _Find(page,name):
        return page.find(0x0107,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0107,name,1)
    FindCreate = staticmethod(_FindCreate)

    def read(self,stream):
        plSingleModifier.read(self,stream)
        
        if stream.ReadBool():
            self.fEnterMsg = PrpMessage.FromStream(stream)
        else:
            self.fEnterMsg = None
        
        if stream.ReadBool():
            self.fExitMsg = PrpMessage.FromStream(stream)
        else:
            self.fExitMsg = None
    
    def write(self,stream):
        plSingleModifier.write(self,stream)
        
        if (self.fEnterMsg != None):
            stream.WriteBool(True)
            PrpMessage.ToStream(stream,self.fEnterMsg)
        else:
            stream.WriteBool(False)

        if (self.fExitMsg != None):
            stream.WriteBool(True)
            PrpMessage.ToStream(stream,self.fExitMsg)
        else:
            stream.WriteBool(False)

#list2
class plSwimRegion(plSimpleRegionSensor):    
    def __init__(self,parent,name="unnamed",type=0x012E):
        plSimpleRegionSensor.__init__(self,parent,name,type)

    def _Find(page,name):
        return page.find(0x012E,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x012E,name,1)
    FindCreate = staticmethod(_FindCreate)

    def changePageRaw(self,sid,did,stype,dtype):
        plSimpleRegionSensor.changePageRaw(self,sid,did,stype,dtype)

    def read(self,stream):
        plSimpleRegionSensor.read(self,stream)
        stream.ReadByte()
        stream.ReadFloat()
        stream.ReadFloat()

    def write(self,stream):
        plSimpleRegionSensor.write(self,stream)
        stream.WriteByte(0)
        stream.WriteFloat(0.0)
        stream.WriteFloat(0.0)
        
    def export_obj(self,obj,scnobj):
    
        self.fEnterMsg = PrpMessage(0x0451,self.getVersion())
        self.fEnterMsg.data.fIsEntering = True
        self.fEnterMsg.data.fSender = scnobj.data.getRef()
        self.fEnterMsg.data.fSwimRegion = self.getRef()
        
        self.fExitMsg = PrpMessage(0x0451,self.getVersion())
        self.fExitMsg.data.fIsEntering = False
        self.fExitMsg.data.fSender = scnobj.data.getRef()
        self.fExitMsg.data.fSwimRegion = self.getRef()
        
        objscript = AlcScript.objects.FindOrCreate(obj.name)
        
    def import_obj(self,obj):
        try:
            obj.removeProperty("regiontype")
        except:
            pass
        obj.addProperty("regiontype","swimdetect")

    def _Export(page,obj,scnobj,name):
        swimdet=plSwimRegion.FindCreate(page,name)
        swimdet.data.export_obj(obj,scnobj)
        scnobj.data.data2.append(swimdet.data.getRef())
    
    Export = staticmethod(_Export)        
        

# Next Class is not used, but probably exactly the same as plSwimRegion
class plSwimDetector(plSimpleRegionSensor):    
    def __init__(self,parent,name="unnamed",type= 0x012F):
        plSimpleRegionSensor.__init__(self,parent,name,type)

    def _Find(page,name):
        return page.find(0x012F,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x012F,name,1)
    FindCreate = staticmethod(_FindCreate)

    def changePageRaw(self,sid,did,stype,dtype):
        plSimpleRegionSensor.changePageRaw(self,sid,did,stype,dtype)

    def read(self,stream):
        plSimpleRegionSensor.read(self,stream)
        stream.ReadByte()
        stream.ReadFloat()
        stream.ReadFloat()

    def write(self,stream):
        plSimpleRegionSensor.write(self,stream)
        stream.WriteByte(0)
        stream.WriteFloat(0.0)
        stream.WriteFloat(0.0)        
 
    def export_obj(self,obj,scnobj):
    
        self.fEnterMsg = PrpMessage(0x0451,self.getVersion())
        self.fEnterMsg.data.fBCastFlags |= plMessage.plBCastFlags["kPropagateToModifiers"]
        self.fEnterMsg.data.fIsEntering = True
        self.fEnterMsg.data.fSender = scnobj.data.getRef()
        self.fEnterMsg.data.fSwimRegion = self.getRef()
        
        self.fExitMsg = PrpMessage(0x0451,self.getVersion())
        self.fExitMsg.data.fBCastFlags |= plMessage.plBCastFlags["kPropagateToModifiers"]
        self.fExitMsg.data.fIsEntering = False
        self.fExitMsg.data.fSender = scnobj.data.getRef()
        self.fExitMsg.data.fSwimRegion = self.getRef()
        
        objscript = AlcScript.objects.FindOrCreate(obj.name)
        
    def import_obj(self,obj):
        try:
            obj.removeProperty("regiontype")
        except:
            pass
        obj.addProperty("regiontype","swimdetect")
    def _Export(page,obj,scnobj,name):
        swimdet=plSwimDetector.FindCreate(page,name)
        swimdet.data.export_obj(obj,scnobj)
        scnobj.data.data2.append(swimdet.data.getRef())
    
    Export = staticmethod(_Export)        
 

#list1
class plSwimRegionInterface(plObjInterface):    
    def __init__(self,parent,name="unnamed",type=0x0133):
        plObjInterface.__init__(self,parent,name,type)

        self.fDownBuoyancy = 11.0
        self.fUpBuoyancy = 2.0
        self.fMaxUpwardVel = 5.0


    def _Find(page,name):
        return page.find(0x0133,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0133,name,1)
    FindCreate = staticmethod(_FindCreate)

    def changePageRaw(self,sid,did,stype,dtype):
        plObjInterface.changePageRaw(self,sid,did,stype,dtype)
    
    def read(self,stream):
        plObjInterface.read(self,stream)
        self.fDownBuoyancy = stream.ReadFloat()
        self.fUpBuoyancy = stream.ReadFloat()
        self.fMaxUpwardVel = stream.ReadFloat()


    def write(self,stream):
        plObjInterface.write(self,stream)
        stream.WriteFloat(self.fDownBuoyancy)
        stream.WriteFloat(self.fUpBuoyancy)
        stream.WriteFloat(self.fMaxUpwardVel)

    def import_obj(self,obj):
        try:
            obj.removeProperty("regiontype")
        except:
            pass
        obj.addProperty("regiontype","swim")
        
        objscript = AlcScript.objects.FindOrCreate(obj.name)
        StoreInDict(objscript,"region.swim.style","simple")
        StoreInDict(objscript,"region.swim.buoyancy.up",self.fUpBuoyancy)
        StoreInDict(objscript,"region.swim.buoyancy.down",self.fDownBuoyancy)
        StoreInDict(objscript,"region.swim.maxupwardspeed",self.fMaxUpwardVel)
    
    def export_obj(self,obj):
        objscript = AlcScript.objects.Find(obj.name)

        self.fUpBuoyancy = FindInDict(objscript,"region.swim.buoyancy.up",self.fUpBuoyancy)
        self.fDownBuoyancy = FindInDict(objscript,"region.swim.buoyancy.down",self.fDownBuoyancy)
        self.fMaxUpwadVel = FindInDict(objscript,"region.swim.maxupwardspeed",self.fMaxUpwardVel)

        pass
        
    def _Export(page,obj,scnobj,name):
        #set the coordinate interface
        objscript = AlcScript.objects.Find(obj.name)
        style = FindInDict(objscript,"region.swim.style","simple")
        
        if style.lower() == "circular":
            swim = page.prp.find(0x0134,name,1)
        elif style.lower() == "straight":
            swim = page.prp.find(0x0136,name,1)
        else:
            swim = page.prp.find(0x0133,name,1)
            
        swim.data.export_obj(obj)
        swim.data.parentref = scnobj.data.getRef()
        scnobj.data.data1.append(swim.data.getRef())
    
    Export = staticmethod(_Export)  


#list1
class plSwimCircularCurrentRegion(plSwimRegionInterface):    
    def __init__(self,parent,name="unnamed",type=0x0134):
        plSwimRegionInterface.__init__(self,parent,name,type)
        #format
        self.fRotation          = -4.0 # was self.f1
        self.fPullNearDistSq    =  1.0 # was self.f2
        self.fPullNearVel       =  2.0 # was self.f3
        self.fPullFarDistSq     =  1.0 # was self.f4
        self.fPullFarVel        =  2.0 # was self.f5
        self.fCurrentSO         = UruObjectRef()

    def _Find(page,name):
        return page.find(0x0134,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0134,name,1)
    FindCreate = staticmethod(_FindCreate)

    def changePageRaw(self,sid,did,stype,dtype):
        plSwimRegionInterface.changePageRaw(self,sid,did,stype,dtype)
        self.dummy.changePageRaw(sid,did,stype,dtype)


    def read(self,stream):
        plSwimRegionInterface.read(self,stream)
        self.fRotation = stream.ReadFloat()
        self.fPullNearDistSq = stream.ReadFloat()
        self.fPullNearVel = stream.ReadFloat()
        self.fPullFarDistSq = stream.ReadFloat()
        self.fPullFarVel = stream.ReadFloat()
        self.fCurrentSO.read(stream)


    def write(self,stream):
        plSwimRegionInterface.write(self,stream)
        stream.WriteFloat(self.fRotation)
        stream.WriteFloat(self.fPullNearDistSq)
        stream.WriteFloat(self.fPullNearVel)
        stream.WriteFloat(self.fPullFarDistSq)
        stream.WriteFloat(self.fPullFarVel)
        self.fCurrentSO.write(stream)



    def import_obj(self,obj):
        plSwimRegionInterface.import_obj(self,obj)
        objscript = AlcScript.objects.FindOrCreate(obj.name)
        StoreInDict(objscript,"region.swim.style",'circular')

        StoreInDict(objscript,"region.swim.circular.rotation",self.fRotation)
        StoreInDict(objscript,"region.swim.circular.centerpoint",str(self.fCurrentSO.Key.name))
        StoreInDict(objscript,"region.swim.circular.pullneardist",self.fPullNearDistSq)
        StoreInDict(objscript,"region.swim.circular.pullnearspeed",self.fPullNearVel)
        StoreInDict(objscript,"region.swim.circular.pullfardist",self.fPullFarDistSq)
        StoreInDict(objscript,"region.swim.circular.pullfarspeed",self.fPullFarVel)


    def export_obj(self,obj):
        plSwimRegionInterface.export_obj(self,obj)
        objscript = AlcScript.objects.Find(obj.name)
        root = self.getRoot()

        self.fRotation = FindInDict(objscript,"region.swim.circular.rotation",self.fRotation)
        self.fPullNearDistSq = FindInDict(objscript,"region.swim.circular.pullneardist",self.fPullNearDistSq)
        self.fPullNearVel = FindInDict(objscript,"region.swim.circular.pullnearspeed",self.fPullNearVel)
        self.fPullFarDistSq = FindInDict(objscript,"region.swim.circular.pullfardist",self.fPullFarDistSq)
        self.fPullFarVel = FindInDict(objscript,"region.swim.circular.pullfarspeed",self.fPullFarVel)

        dummyname = FindInDict(objscript,"region.swim.circular.centerpoint",None)
                
        if(dummyname != None):
            # find or create the dummy
            dummyobj = root.find(0x0001,dummyname,0)
            if dummyobj == None:
                raise RuntimeError, "Could not locate a swim center object named %s" % dummyname                     
            self.fCurrentSO = dummyobj.data.getRef()
        else:
            raise RuntimeError, "Could not locate a swim center object named %s" % dummyname                     


#list1
class plSwimStraightCurrentRegion(plSwimRegionInterface):    
    def __init__(self,parent,name="unnamed",type=0x0136):
        plSwimRegionInterface.__init__(self,parent,name,type)
        #format
        self.fNearDist  = 160.0 # Was self.f2
        self.fNearVel   =   2.0 # Was self.f3
        self.fFarDist   = 186.0 # Was self.f4
        self.fFarVel    =   8.0 # Was self.f5
        self.fCurrentSO = UruObjectRef()


    def _Find(page,name):
        return page.find(0x0136,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0136,name,1)
    FindCreate = staticmethod(_FindCreate)

    def changePageRaw(self,sid,did,stype,dtype):
        plSwimRegionInterface.changePageRaw(self,sid,did,stype,dtype)
        self.dummy.changePageRaw(sid,did,stype,dtype)

    def read(self,stream):
        plSwimRegionInterface.read(self,stream)
        self.fNearDist = stream.ReadFloat()
        self.fNearVel = stream.ReadFloat()
        self.fFarDist = stream.ReadFloat()
        self.fFarVel = stream.ReadFloat()
        self.fCurrentSO.read(stream)


    def write(self,stream):
        plSwimRegionInterface.write(self,stream)
        stream.WriteFloat(self.fNearDist)
        stream.WriteFloat(self.fNearVel)
        stream.WriteFloat(self.fFarDist)
        stream.WriteFloat(self.fFarVel)
        self.fCurrentSO.write(stream)


    def import_obj(self,obj):
        plSwimRegionInterface.import_obj(self,obj)
        objscript = AlcScript.objects.FindOrCreate(obj.name)
        StoreInDict(objscript,"region.swim.style",'straight')

        StoreInDict(objscript,"region.swim.straight.centerpoint",str(self.fCurrentSO.Key.name))
        StoreInDict(objscript,"region.swim.straight.neardist",self.fNearDist)
        StoreInDict(objscript,"region.swim.straight.nearspeed",self.fNearVel)
        StoreInDict(objscript,"region.swim.straight.fardist",self.fFarDist)
        StoreInDict(objscript,"region.swim.straight.farspeed",self.fFarVel)


    def export_obj(self,obj):
        plSwimRegionInterface.export_obj(self,obj)
        objscript = AlcScript.objects.Find(obj.name)
        
        root = self.getRoot()
        self.fNearDist = FindInDict(objscript,"region.swim.straight.neardist",self.fNearDist)
        self.fNearVel = FindInDict(objscript,"region.swim.straight.nearspeed",self.fNearVel)
        self.fFarDist = FindInDict(objscript,"region.swim.straight.fardist",self.fFarDist)
        self.fFarVel = FindInDict(objscript,"region.swim.straight.farspeed",self.fFarVel)

        dummyname = FindInDict(objscript,"region.swim.straight.centerpoint",None)
                
        if(dummyname != None):
            # find or create the dummy
            dummyobj = root.find(0x0001,dummyname,0)
            if dummyobj == None:
                raise RuntimeError, "Could not locate a swim center object named %s" % dummyname                     
            self.fCurrentSO = dummyobj.data.getRef()
        else:
            raise RuntimeError, "Could not locate a swim center object named %s" % dummyname                     
