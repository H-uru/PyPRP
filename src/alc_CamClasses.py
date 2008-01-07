#
# $Id: alc_CamClasses.py 843 2007-11-04 01:19:29Z Trylon $
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
from alc_LogicClasses import *
from alcGObjects import *
from alcConvexHull import *
from alc_VolumeIsect import *
from alc_AlcScript import *

import alcconfig, alchexdump



################# Rework of the camera classes ###################

class plCameraModifier1(hsKeyedObject):    # actually descends from plSingleModifer, but doesn't use those read/write functions
    class CamTrans:
        def __init__(self,to=UruObjectRef()):
            self.fTransTo = to
            self.fCutPos = 0 # boolean
            self.fCutPOA = 0 # boolean
            self.fIgnore = 0 # boolean
            self.fAccel = 60.0
            self.fDecel = 60.0
            self.fVelocity = 60.0
            self.fPOAAccel = 60.0
            self.fPOADecel = 60.0
            self.fPOAVelocity = 60.0

        def read(self,stream):
            self.fTransTo.read(stream)
            self.fCutPos = stream.ReadBool()
            self.fCutPOA = stream.ReadBool()
            self.fIgnore = stream.ReadBool()
            self.fVelocity = stream.ReadFloat()
            self.fAccel = stream.ReadFloat()
            self.fDecel = stream.ReadFloat()
            self.fPOAVelocity = stream.ReadFloat()
            self.fPOAAccel = stream.ReadFloat()
            self.fPOADecel = stream.ReadFloat()

        def write(self,stream):
            self.fTransTo.write(stream)
            stream.WriteBool(self.fCutPos)
            stream.WriteBool(self.fCutPOA)
            stream.WriteBool(self.fIgnore)
            stream.WriteFloat(self.fVelocity)
            stream.WriteFloat(self.fAccel)
            stream.WriteFloat(self.fDecel)
            stream.WriteFloat(self.fPOAVelocity)
            stream.WriteFloat(self.fPOAAccel)
            stream.WriteFloat(self.fPOADecel)        

        def import_obj(self,obj,count):
            pass

        def export_obj(self,obj,prp):
            pass
   
    Flags = \
    { \
        "kRefBrain"         : 0, \
        "kRefCut"           : 1, \
        "kRefTrack"         : 2, \
        "kRefCallbackMsg"   : 3  \
    }
   
    def __init__(self,parent,name="unnamed",type=0x009B):
        hsKeyedObject.__init__(self,parent,name,type)
        #format
        self.fBrain=UruObjectRef()

        self.fTrans = [] #CamTrans Fields
        
        #Ending is almost always like this:
        self.fFOVw = 45.0 # Field of View
        self.fFOVh = 33.75 #
        
        self.fMessageQueue = []
        self.fFOVInstructions = []
        
        self.fAnimated = False
        self.fStartAnimOnPush = False
        self.fStopAnimOnPop = False
        self.fResetAnimOnPop = False

    def _Find(page,name):
        return page.find(0x009B,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x009B,name,1)
    FindCreate = staticmethod(_FindCreate)

        
    def changePageRaw(self,sid,did,stype,dtype):
        hsKeyedObject.changePageRaw(self,sid,did,stype,dtype)
    
    def read(self,stream,size):
        start = stream.tell()
        hsKeyedObject.read(self,stream)
        
        self.fBrain.read(stream)
        
        count = stream.Read32()
        for i in range(count):
            cam = plCameraModifier1.CamTrans()
            cam.read(stream) # not like this in Plasma, but makes it easier here :)
            self.fTrans.append(cam)
        
        self.fFOVw = stream.ReadFloat()
        self.fFOVh = stream.ReadFloat()
        
        count = stream.Read32()
        # we now should read in a message queue, which is hard because of incomplete message implementations
        
        
        try:
 
            for i in range(count):
                Msg = PrpMessage.FromStream(stream)
                self.fMessageQueue.add(Msg.data)
    
            for msg in self.fMessageQueue:
                msg.fSender.read(stream)
            
            # read in queue of plCameraMSgs
            self.fFOVInstructions = []
            count = stream.Read32()
            for i in range(count):
                Msg = PrpMessage.FromStream(stream)
                self.fFOVInstructions.append(FovMsg.data)

        except ValueError, detail:
            print "/---------------------------------------------------------"
            print "|  WARNING:"
            print "|   Got Value Error:" , detail, ":"
            print "|   Skipping message arrays of plCameraModifier1..."
            print "|   -> Skipping %i bytes ahead " % ( (start + size -4) - stream.tell())
            print "|   -> Total object size: %i bytes"% (size)
            print "\---------------------------------------------------------\n"
            
            stream.seek(start + size - 4) #reposition the stream to read in the last 4 bytes
            
        self.fAnimated = stream.ReadBool()
        self.fStartAnimOnPush = stream.ReadBool()
        self.fStopAnimOnPop = stream.ReadBool()
        self.fResetAnimOnPop = stream.ReadBool()
    
    def write(self,stream):
        hsKeyedObject.write(self,stream)
        
        self.fBrain.write(stream)
        
        stream.Write32(len(self.fTrans))
        for cam in self.fTrans:
            cam.write(stream)
            
        stream.WriteFloat(self.fFOVw)
        stream.WriteFloat(self.fFOVh)
        

        stream.Write32(len(self.fMessageQueue))
        for msg in self.fMessageQueue:
            PrpMessage.ToStream(stream,msg)

        for msg in self.fMessageQueue:
            msg.fSender.write(stream)
        
        stream.Write32(len(self.fFOVInstructions))
        for msg in self.fFOVInstructions:
            PrpMessage.ToStream(stream,msg)
        
        stream.WriteBool(self.fAnimated);
        stream.WriteBool(self.fStartAnimOnPush);
        stream.WriteBool(self.fStopAnimOnPop);
        stream.WriteBool(self.fResetAnimOnPop);
    


    def import_obj(self,obj):
        root = self.getRoot()
        
        # calculate the camera lens (blender has 32 mm camera)
        radian_fFOVh = self.fFOVh / (360/(2*math.pi))
        
        lens = 32/(2*math.tan(radian_fFOVh/2))
        
        # now set the blender lens property
        obj.data.setLens(lens)
             
        c = 0
        for cam in self.fTrans:
            cam.import_obj(obj,c)
            c = c+1

        cbrain = root.findref(self.fBrain)
        cbrain.data.import_obj(obj)

        pass

    def export_obj(self,obj,prp):
        print "Exporting Camera Modifier Object"
    
        # --- Find the camera's script object ----
        objscript = AlcScript.objects.Find(obj.name)

        # --------- FOV --------------
        if(obj.data.getType() == 0): # check for perspective camera
            lens = obj.data.getLens()
            print "Calculating FOV for lens is %i mm" % lens
            
            self.fFOVh = 2 * math.atan(32/(2*lens)) * (360/(2*math.pi))
            
            self.fFOVw = self.fFOVh / 0.750 # I divide by 0.750 becaus I hope it's more accurate than multiplying by 1.33
        else:
            #default them to default values (45:33.75):
            print "Camera is not perpective - please changeit to perspective"
            pass
        
        # -------- Camera Transitions ---------
        cam = plCameraModifier1.CamTrans()
        self.fTrans.append(cam)

        # -------- Camera Brains --------

        # get brain type from logic property first
        cambraintype = getTextPropertyOrDefault(obj,"cambrain","fixed")

        # load it in from AlcScript (overrides logic properties)
    
        scriptbrain = FindInDict(objscript,"camera.brain.type","fixed")
        scriptbrain = str(scriptbrain).lower()
        if scriptbrain in ["fixed","circle","avatar","firstperson"]:
            cambraintype = scriptbrain

        print " Camera Brain: %s" % cambraintype

        # determine the camera brain
        if(cambraintype == "fixed"):
            # fixed camera brain
            cambrain = prp.find(0x009F,str(self.Key.name),1)
        elif(cambraintype == "circle"):
            # Circle camera brain
            cambrain = prp.find(0x00C2,str(self.Key.name),1)
        elif(cambraintype == "avatar"):
            # Avatar camera brain
            cambrain = prp.find(0x009E,str(self.Key.name),1)
        elif(cambraintype == "firstperson"):
            # First Person Camera Brain
            cambrain = prp.find(0x00B3,str(self.Key.name),1)
        else:
            # simple and default camera brain
            cambrain = prp.find(0x0099,str(self.Key.name),1)

        cambrain.data.export_obj(obj,prp)
        self.fBrain = cambrain.data.getRef()
        
    def _Import(scnobj,prp,obj):
        # Lights
        for c_ref in  scnobj.data1.vector:
            if c_ref.Key.object_type in [0x009B,]:
                cam=prp.findref(c_ref)
                cam.data.import_obj(obj)
                obj.layers=[5,]
                break

    Import = staticmethod(_Import)
        


class plCameraRegionDetector(plDetectorModifier):    
    def __init__(self,parent,name="unnamed",type=0x006F):
        plDetectorModifier.__init__(self,parent,name,type)
        
        self.fMessages = []
        
    def _Find(page,name):
        return page.find(0x006F,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x006F,name,1)
    FindCreate = staticmethod(_FindCreate)

    def changePageRaw(self,sid,did,stype,dtype):
        plDetectorModifier.changePageRaw(self,sid,did,stype,dtype)

    def read(self,stream):
        plDetectorModifier.read(self,stream)
       
        count = stream.Read32()
        self.fMessages = []
        for i in range(count):
            msg = plCameraMsg()
            type = stream.Read16() # read in message type
            msg.read(stream)
            self.fMessages.append(msg)
    
    def write(self,stream):
        plDetectorModifier.write(self,stream)
        
        stream.Write32(len(self.fMessages))
        for msg in self.fMessages:
            stream.Write16(msg.MessageType) # read in message type
            msg.write(stream)
    


    def import_obj(self,obj):
        try:
            obj.removeProperty("regiontype")
        except:
            pass
        obj.addProperty("regiontype","camera")

        objscript = AlcScript.objects.FindOrCreate(obj.name)

        msgscripts = []
        for msg in self.fMessages:
            msgscript = {} 
            StoreInDict(msgscript,"camera",str(msg.fNewCam.Key.name))

            if self.fMessages[0].fCmd[plCameraMsg.ModCmds["kSetAsPrimary"]] == 1:
                StoreInDict(msgscript,"setprimary",True)
            else:
                StoreInDict(msgscript,"setprimary",False)
            
            msgscripts.append(msgscript)
        
        StoreInDict(objscript,"region.camera.cameras",msgscripts)

    def export_obj(self,camerakey,obj,prp):
        print "Exporting Camera Region Detector"
        
        CamMsg = plCameraMsg()
        CamMsg.fNewCam = camerakey
        CamMsg.fBCastFlags |= plMessage.plBCastFlags["kBCastByType"]
        CamMsg.fCmd[plCameraMsg.ModCmds["kRegionPushCamera"]] = 1 # this makes it set the camera
        
        setdefault = getTextPropertyOrDefault(obj,"setDefCam","0")
        if(setdefault != "0" and setdefault != "false" and setdefault != "False"):
            print "Setting camera region to change the default camera region"
            CamMsg.fCmd[plCameraMsg.ModCmds["kSetAsPrimary"]] = 1
        else:
            print "Setting camera region to temporary switch"

        

        
        self.fMessages.append(CamMsg)
    

class plCameraBrain1(hsKeyedObject):    

    Flags = {
        "kCutPos"                   : 0,
        "kCutPosOnce"               : 1, 
        "kCutPOA"                   : 2, 
        "kCutPOAOnce"               : 3, 
        "kAnimateFOV"               : 4,
        "kFollowLocalAvatar"        : 5, 
        "kPanicVelocity"            : 6, 
        "kRailComponent"            : 7, 
        "kSubject"                  : 8,
        "kCircleTarget"             : 9, 
        "kMaintainLOS"              : 10, 
        "kZoomEnabled"              : 11, 
        "kIsTransitionCamera"       : 12,
        "kWorldspacePOA"            : 13, 
        "kWorldspacePos"            : 14, 
        "kCutPosWhilePan"           : 15, 
        "kCutPOAWhilePan"           : 16,
        "kNonPhys"                  : 17, 
        "kNeverAnimateFOV"          : 18, 
        "kIgnoreSubworldMovement"   : 19, 
        "kFalling"                  : 20,
        "kRunning"                  : 21, 
        "kVerticalWhenFalling"      : 22, 
        "kSpeedUpWhenRunning"       : 23, 
        "kFallingStopped"           : 24,
        "kBeginFalling"             : 25 
    }
    def __init__(self,parent,name="unnamed",type=0x0099):
        hsKeyedObject.__init__(self,parent,name,type)
        #format
        self.fFlags=hsBitVector()
        
        self.fPOAOffset = Vertex(0.0,0.0,6.0)

        self.fSubjectKey=UruObjectRef()
        self.fRail=UruObjectRef()
        
        self.fAccel = 30
        self.fDecel = 30
        self.fVelocity = 30 
        self.fPOAAccel = 30
        self.fPOADecel = 30
        self.fPOAVelocity = 30 
        self.fXPanLimit = 0
        self.fZPanLimit = 0
        self.fZoomRate = 0
        self.fZoomMin = 0
        self.fZoomMax = 0
                
    def _Find(page,name):
        return page.find(0x0099,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0099,name,1)
    FindCreate = staticmethod(_FindCreate)

    def changePageRaw(self,sid,did,stype,dtype):
        hsKeyedObject.changePageRaw(self,sid,did,stype,dtype)
        self.fSubjectKey.changePageRaw(sid,did,stype,dtype)
        self.fRail.changePageRaw(sid,did,stype,dtype)


    def read(self,stream):
        hsKeyedObject.read(self,stream)

        self.fPOAOffset.read(stream)
        self.fSubjectKey.read(stream)
        self.fRail.read(stream)
        self.fFlags.read(stream)

        self.fAccel = stream.ReadFloat()
        self.fDecel = stream.ReadFloat()
        self.fVelocity = stream.ReadFloat()
        self.fPOAAccel = stream.ReadFloat()
        self.fPOADecel = stream.ReadFloat()
        self.fPOAVelocity = stream.ReadFloat()
        self.fXPanLimit = stream.ReadFloat()
        self.fZPanLimit = stream.ReadFloat()
        self.fZoomRate = stream.ReadFloat()
        self.fZoomMin = stream.ReadFloat()
        self.fZoomMax = stream.ReadFloat()

    def write(self,stream):
        hsKeyedObject.write(self,stream)

        self.fPOAOffset.write(stream)
        self.fSubjectKey.write(stream)
        self.fRail.write(stream)
        self.fFlags.write(stream)

        stream.WriteFloat(self.fAccel)
        stream.WriteFloat(self.fDecel)
        stream.WriteFloat(self.fVelocity)
        stream.WriteFloat(self.fPOAAccel)
        stream.WriteFloat(self.fPOADecel)
        stream.WriteFloat(self.fPOAVelocity)
        stream.WriteFloat(self.fXPanLimit)
        stream.WriteFloat(self.fZPanLimit)
        stream.WriteFloat(self.fZoomRate)
        stream.WriteFloat(self.fZoomMin)
        stream.WriteFloat(self.fZoomMax)


    def import_obj(self,obj):
        obj.addProperty("POA_X",float(self.fPOAOffset.x))    
        obj.addProperty("POA_Y",float(self.fPOAOffset.y))    
        obj.addProperty("POA_Z",float(self.fPOAOffset.z))    

        if(str(self.fRail.Key.name) != ""):
            obj.addProperty("RailCamera",str(self.fRail.Key.name)) 
       

    def export_obj(self,obj,prp):
        print "Exporting CameraBrain1"
        # -------- Initialize default settings
        self.fFlags[plCameraBrain1.Flags["kFollowLocalAvatar"]] = 1
        self.fFlags[plCameraBrain1.Flags["kCutPos"]] = 0
        self.fFlags[plCameraBrain1.Flags["kCutPOA"]] = 0
        
        # ------ Obtain the AlcScript Object ------
        objscript = AlcScript.objects.Find(obj.name)
        # ------ Process ------
        # AlcScript: camera.brain.poa = "<float X>,<float Y>,<float Z>"
        poa = str(FindInDict(objscript,"camera.brain.poa","0,0,0"))
        try:
            X,Y,Z, = poa.split(',')
            self.fPOAOffset = Vertex(float(X),float(Y),float(Z))
        except ValueError, detail:
            print "  Error parsing camera.brain.poa (Value:",poa,") : ",detail

        # AlcScript: camera.brain.followavatar = [ "false", "true" (Default)]
        follow = str(FindInDict(objscript,"camera.brain.followavatar","0,0,0"))
        if follow.lower() == "false":
            self.fFlags[plCameraBrain1.Flags["kFollowLocalAvatar"]] = 0
        else:
            self.fFlags[plCameraBrain1.Flags["kFollowLocalAvatar"]] = 1
        
        # AlcScript: camera.brain.cutposition= [ "once", "true", "false" (Default)]
        brain_cutpos = str(FindInDict(objscript,"camera.brain.cutposition","false"))
        if brain_cutpos == "true":
            self.fFlags[plCameraBrain1.Flags["kCutPos"]] = 1
            self.fFlags[plCameraBrain1.Flags["kCutPosOnce"]] = 0
        elif brain_cutpos == "once":
            self.fFlags[plCameraBrain1.Flags["kCutPos"]] = 0
            self.fFlags[plCameraBrain1.Flags["kCutPosOnce"]] = 1
        else:
            self.fFlags[plCameraBrain1.Flags["kCutPos"]] = 0
            self.fFlags[plCameraBrain1.Flags["kCutPosOnce"]] = 0
        
        # AlcScript: camera.brain.cutpoa = [ "once", "true", "false" (Default)]
        brain_cutpoa = str(FindInDict(objscript,"camera.brain.cutpoa","false"))
        if brain_cutpoa == "true":
            self.fFlags[plCameraBrain1.Flags["kCutPOA"]] = 1
            self.fFlags[plCameraBrain1.Flags["kCutPOAOnce"]] = 0
        elif brain_cutpoa == "once":
            self.fFlags[plCameraBrain1.Flags["kCutPOA"]] = 0
            self.fFlags[plCameraBrain1.Flags["kCutPOAOnce"]] = 1
        else:
            self.fFlags[plCameraBrain1.Flags["kCutPOA"]] = 0
            self.fFlags[plCameraBrain1.Flags["kCutPOAOnce"]] = 0
                

        
class plCameraBrain1_Fixed(plCameraBrain1):    
    def __init__(self,parent,name="unnamed",type=0x009F):
        plCameraBrain1.__init__(self,parent,name,type)
        
        # set the Camerabrain1 floats to match defaults for this brain type
        self.fAccel = 30
        self.fDecel = 30
        self.fVelocity = 30 
        self.fPOAAccel = 30
        self.fPOADecel = 30
        self.fPOAVelocity = 30 
        self.fXPanLimit = 0
        self.fZPanLimit = 0
        self.fZoomRate = 0
        self.fZoomMin = 0
        self.fZoomMax = 0

        #format
        self.fTargetPoint=UruObjectRef()
        
    def _Find(page,name):
        return page.find(0x009F,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x009F,name,1)
    FindCreate = staticmethod(_FindCreate)

    def changePageRaw(self,sid,did,stype,dtype):
        plCameraBrain1.changePageRaw(self,sid,did,stype,dtype)
        self.fTargetPoint.changePageRaw(sid,did,stype,dtype)

    def read(self,stream):
        plCameraBrain1.read(self,stream)
        self.fTargetPoint.read(stream)

    def write(self,stream):
        plCameraBrain1.write(self,stream)
        self.fTargetPoint.write(stream)

    def import_obj(self,obj):
        plCameraBrain1.import_obj(self,obj)
        obj.addProperty("cambrain","fixed")
        obj.addProperty("Fixedcam_target",str(self.fTargetPoint.Key.name))
        

    def export_obj(self,obj,prp):
        plCameraBrain1.export_obj(self,obj,prp)
        print "Exporting CameraBrain1_Fixed"
        # ------ Obtain the AlcScript Object ------
        objscript = AlcScript.objects.Find(obj.name)
        # ------ Conintue if it's set ------

        # AlcScript: camera.brain.target = string
        target = str(FindInDict(objscript,"camera.brain.target",""))
        # do something with that...

class plCameraBrain1_Circle(plCameraBrain1_Fixed):
    CircleFlags = {
        "kLagged"               :  0x1,
        "kAbsoluteLag"          :  0x3,
        "kFarthest"             :  0x4,
        "kTargetted"            :  0x8,
        "kHasCenterObject"      : 0x10,
        "kPOAObject"            : 0x20,
        "kCircleLocalAvatar"    : 0x40
    }
    def __init__(self,parent,name="unnamed",type=0x00C2):
        plCameraBrain1_Fixed.__init__(self,parent,name,type)

        # set the Camerabrain1 floats to match defaults for this brain type
        self.fAccel = 10
        self.fDecel = 10
        self.fVelocity = 15 
        self.fPOAAccel = 10
        self.fPOADecel = 10
        self.fPOAVelocity = 15 
        self.fXPanLimit = 0
        self.fZPanLimit = 0
        self.fZoomRate = 0
        self.fZoomMin = 0
        self.fZoomMax = 0

        #format
        self.fCircleFlags = 0
        self.fCircleFlags |= plCameraBrain1_Circle.CircleFlags['kCircleLocalAvatar'] | \
                             plCameraBrain1_Circle.CircleFlags['kFarthest'] 
        
        self.fCenter = Vertex(0.0,0.0,0.0)

        self.fRadius = 0

        
        self.fCenterObject = UruObjectRef()
        self.fPOAObj = UruObjectRef()
        
        self.fCirPerSec = 0.10 # virtually always 0.10
        
    def _Find(page,name):
        return page.find(0x00C2,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x00C2,name,1)
    FindCreate = staticmethod(_FindCreate)

    def changePageRaw(self,sid,did,stype,dtype):
        plCameraBrain1.changePageRaw(self,sid,did,stype,dtype)
        self.fCenterObject.changePageRaw(sid,did,stype,dtype)
        self.fPOAObj.changePageRaw(sid,did,stype,dtype)

    def read(self,stream):
        plCameraBrain1.read(self,stream) # yes, this is correct, it uses the plCameraBrain1 read/write functions

        self.fCircleFlags = stream.Read32()

        self.fCenter.read(stream)

        self.fRadius = stream.ReadFloat()

        self.fCenterObject.read(stream)
        self.fPOAObj.read(stream)

        self.fCirPerSec = stream.ReadFloat()

    def write(self,stream):
        plCameraBrain1.write(self,stream) # yes, this is correct, it uses the plCameraBrain1 read/write functions

        stream.Write32(self.fCircleFlags)
        self.fCenter.write(stream)
        stream.WriteFloat(self.fRadius)
        self.fCenterObject.write(stream)
        self.fPOAObj.write(stream)

        stream.WriteFloat(self.fCirPerSec)
        
        

    def import_obj(self,obj):
        plCameraBrain1.import_obj(self,obj)
        obj.addProperty("cambrain","circle")
        
        obj.addProperty("Circle_flags",alcHex2Ascii(self.fCircleFlags))
        
        obj.data.setClipEnd(self.fRadius)
        obj.data.setMode("showLimits")
     

    def export_obj(self,obj,prp):
        plCameraBrain1.export_obj(self,obj,prp)
        # -------- Export based on blender object -------
        # get the matrices
        LocalToWorld=hsMatrix44()
        m=getMatrix(obj)
        m.transpose()
        LocalToWorld.set(m)

        # convert the clip-end to the Center point of the camera
        if obj.getType() == 'Camera':
            clip_end = obj.data.getClipEnd()
            self.fCenter = Vertex(0,0,0 - clip_end) # camera points to local -Z
            self.fCenter.transform(LocalToWorld)
            self.fRadius = clip_end # always seems to define distance from camera to rotation point

        # -------Continue based on AlcScript object ------
        objscript = AlcScript.objects.Find(obj.name)
        # ------ Conintue if it's set ------
        # AlcScript: camera.brain.distance = ["farthest","closest" (default)]
        dist = str(FindInDict(objscript,"camera.brain.distance","closest"))
        if dist.lower() == "farthest":
            self.fCircleFlags |= plCameraBrain1_Circle.CircleFlags["kFarthest"]
        # AlcScript: camera.brain.circleavatar = ["true" (default),"false"]
        follow = str(FindInDict(objscript,"camera.brain.circleavatar","true"))
        if follow.lower() == "true":
            self.fCircleFlags |= plCameraBrain1_Circle.CircleFlags["kCircleLocalAvatar"]


class plCameraBrain1_Avatar(plCameraBrain1):    
    def __init__(self,parent,name="unnamed",type=0x009E):
        plCameraBrain1.__init__(self,parent,name,type)

        # set the Camerabrain1 floats to match defaults for this brain type
        self.fAccel = 10
        self.fDecel = 10
        self.fVelocity = 50 
        self.fPOAAccel = 10
        self.fPOADecel = 10
        self.fPOAVelocity = 50 
        self.fXPanLimit = 0
        self.fZPanLimit = 0
        self.fZoomRate = 0
        self.fZoomMin = 0
        self.fZoomMax = 0

        #format
        self.fOffset = Vertex(0,0,0)
        
        
    def _Find(page,name):
        return page.find(0x009E,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x009E,name,1)
    FindCreate = staticmethod(_FindCreate)

    def changePageRaw(self,sid,did,stype,dtype):
        plCameraBrain1.changePageRaw(self,sid,did,stype,dtype)

    def read(self,stream):
        plCameraBrain1.read(self,stream)
        self.fOffset.read(stream)

    def write(self,stream):
        plCameraBrain1.write(self,stream)
        self.fOffset.write(stream)


    def import_obj(self,obj):
        plCameraBrain1.import_obj(self,obj)
        obj.addProperty("cambrain","avatar")
        obj.addProperty("AvCam_X",float(self.fOffset.x))
        obj.addProperty("AvCam_Y",float(self.fOffset.y))
        obj.addProperty("AvCam_Z",float(self.fOffset.z))

    def export_obj(self,obj,prp):
        plCameraBrain1.export_obj(self,obj,prp)
        # -------- Export based on blender object -------
        self.fOffset.x = getFloatPropertyOrDefault(obj,"AvCam_X",self.fOffset.x)
        self.fOffset.y = getFloatPropertyOrDefault(obj,"AvCam_Y",self.fOffset.y)
        self.fOffset.z = getFloatPropertyOrDefault(obj,"AvCam_Z",self.fOffset.z)

        # ------ Obtain the AlcScript Object ------
        script_cam = AlcScript.objects.Find(obj.name)
        # ------ Conintue if it's set ------
        if script_cam != None:
            if script_cam.Contains("brain"):
                if script_cam.brain.Contains("avatar"):
                    pass


class plCameraBrain1_FirstPerson(plCameraBrain1_Avatar):    
    def __init__(self,parent,name="unnamed",type=0x00B3):
        plCameraBrain1.__init__(self,parent,name,type)

    def _Find(page,name):
        return page.find(0x00B3,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x00B3,name,1)
    FindCreate = staticmethod(_FindCreate)

    def changePageRaw(self,sid,did,stype,dtype):
        plCameraBrain1_Avatar.changePageRaw(self,sid,did,stype,dtype)

    def read(self,stream):
        plCameraBrain1_Avatar.read(self,stream)

    def write(self,stream):
        plCameraBrain1_Avatar.write(self,stream)


    def import_obj(self,obj):
        plCameraBrain1.import_obj(self,obj)
        obj.addProperty("cambrain","firstperson")
        obj.addProperty("FpCam_X",float(self.fOffset.x))
        obj.addProperty("FpCam_Y",float(self.fOffset.y))
        obj.addProperty("FpCam_Z",float(self.fOffset.z))

    def export_obj(self,obj,prp):
        plCameraBrain1.export_obj(self,obj,prp)

        # ------ Obtain the AlcScript Object ------
        objscript = AlcScript.objects.Find(obj.name)
        # ------ Conintue if it's set ------
        # AlcScript: camera.brain.offset = "<float X>,<float Y>,<float Z>"
        offset = str(FindInDict(objscript,"camera.brain.offset","0,0,0"))
        try:
            X,Y,Z, = offset.split(',')
            self.fOffset = Vertex(float(X),float(Y),float(Z))
        except ValueError, detail:
            print "  Error parsing camera.brain.offset (Value:",offset,") : ",detail
