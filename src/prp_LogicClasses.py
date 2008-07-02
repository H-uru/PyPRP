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
from prp_Types import *
from prp_DXTConv import *
from prp_HexDump import *
from prp_GeomClasses import *
from prp_Functions import *
from prp_ConvexHull import *
from prp_AbsClasses import *
from prp_VolumeIsect import *
from prp_AlcScript import *
from prp_SwimClasses import *
from prp_Messages import *
from prp_Classes import *
from prp_RefParser import *
from prp_ObjClasses import *
from prp_QuickScripts import *
from prp_AnimClasses import *
import prp_QuickScripts

class AlcLogicHelper:

    def _Export(page,obj,scnobj,name):
        print " [LogicHelper]"
        objscript = AlcScript.objects.Find(obj.name)
        # Export prefefined scripts:

#        AlcLogicHelper.ExportSDL(page,obj,scnobj,name)
#        AlcLogicHelper.ExportClickable(page,obj,scnobj,name)

        # Export the logic....
        logicscript = FindInDict(objscript,'logic',{})
        AlcLogicHelper.ExportLogic(page,logicscript,scnobj)
        pass
    Export = staticmethod(_Export)

    def _ExportSDL(page,obj,scnobj,name):
        pass
    ExportSDL = staticmethod(_ExportSDL)

    def _ExportClickable(page,obj,scnobj,name):
        pass
    ExportClickable = staticmethod(_ExportClickable)


    def _CreateLadderRegions(page,obj):

        # don't process any further until we reviewed this
        # return
        # Reviewed. Updated. Works. -Nadnerb 01/24/08

        # creates a set of ladder regions from the bounding box of an object


        # get the matrix, rotation and scales
        l2wMtx = getMatrix(obj)
        w2lMtx = Blender.Mathutils.Matrix(l2wMtx).invert()

        rotEuler = l2wMtx.rotationPart().toEuler()
        sizeVect = Blender.Mathutils.Vector(obj.size)

        # get the objects bounding box
        bbx = obj.getBoundBox()

        i = 0
        mworld = []
        mlocal = []
        # order the list like this bitwise, and translate to local coords
        # bit nr   2 1 0
        # index = [x,y,z] -> z/x/y = 1 indicates hightest value, 0 indicates lowest value
        for i in [0,1,3,2,4,5,7,6]:
            vworld = Blender.Mathutils.Vector(bbx[i][0],bbx[i][1],bbx[i][2],1)
            vlocal = Blender.Mathutils.Vector(vworld) * w2lMtx

            mworld.append(vworld)
            mlocal.append(vlocal)


        # calculate the objects dimensions and center
        deltaLX = (mlocal[7].x - mlocal[0].x)
        deltaLY = (mlocal[7].y - mlocal[0].y)
        deltaLZ = (mlocal[7].z - mlocal[0].z)
        deltaWX = (mlocal[7].x - mlocal[0].x) * sizeVect.x
        deltaWY = (mlocal[7].y - mlocal[0].y) * sizeVect.y
        deltaWZ = (mlocal[7].z - mlocal[0].z) * sizeVect.z
        ctrLX = mlocal[7].x - (deltaLX /2)
        ctrLY = mlocal[7].y - (deltaLY /2)
        ctrLZ = mlocal[7].z - (deltaLZ /2)

        # calculate the height of the region:

        # define variables
        rgnheight = 6.0 # region height == avatar height
        rgnwidth = deltaWX # region width is width of the bounding box
        rgndepth = 3.0 # region depth is 3 feet (chosen from educated guess - 2 works probably jst as well...)

        ## please do not change the following finely tuned variables, unless you have a very good reason!!!!!
        grabDepth = 0.11 # the amount of space that the avatars hands should penetrate the region, to grab the rungs

        gripOffset = 0.50 - grabDepth # put both regions ths amount into the Y+ axis of the bbox, to have it grip the rungs perfectly
        btmYOffset = 0   # bottom region extra offset from local y+ edge of boundbox (offset in Y+ direction)
        topYOffset = -1.00 - grabDepth # top region offset from local y+ edge of boundbox (offset in Y+ direction)
        btmdepth = rgndepth # Y
        topdepth = rgndepth # optionally we might consider doing rgndepth+deltaWY here.


        # now, we must define a new set of transformation matrices - one for the top region, and one for the bottom region

        # now build up the correct Vertex meshes and facelist
        btmMsh = []
        btmMsh.append([0-(rgnwidth/2),0-(btmdepth/2),0])
        btmMsh.append([0-(rgnwidth/2),0-(btmdepth/2),rgnheight])
        btmMsh.append([0-(rgnwidth/2),(btmdepth/2),0])
        btmMsh.append([0-(rgnwidth/2),(btmdepth/2),rgnheight])
        btmMsh.append([(rgnwidth/2),0-(btmdepth/2),0])
        btmMsh.append([(rgnwidth/2),0-(btmdepth/2),rgnheight])
        btmMsh.append([(rgnwidth/2),(btmdepth/2),0])
        btmMsh.append([(rgnwidth/2),(btmdepth/2),rgnheight])

        topMsh = []
        topMsh.append([0-(rgnwidth/2),0-(topdepth/2),0])
        topMsh.append([0-(rgnwidth/2),0-(topdepth/2),rgnheight])
        topMsh.append([0-(rgnwidth/2),(topdepth/2),0])
        topMsh.append([0-(rgnwidth/2),(topdepth/2),rgnheight])
        topMsh.append([(rgnwidth/2),0-(topdepth/2),0])
        topMsh.append([(rgnwidth/2),0-(topdepth/2),rgnheight])
        topMsh.append([(rgnwidth/2),(topdepth/2),0])
        topMsh.append([(rgnwidth/2),(topdepth/2),rgnheight])

        # now make one face set for both meshes:
        rgnFcs = []
        rgnFcs.append([0,2,6,4])
        rgnFcs.append([5,7,3,1])
        rgnFcs.append([0,1,3,2])
        rgnFcs.append([6,7,5,4])
        rgnFcs.append([4,5,1,0])
        rgnFcs.append([2,3,7,6])

        # now calculate where the centers of the top/btm regions should be **locally**, and transform them to world
        # this is a lot easier than taking rotation and stuff into account, and calculate the centers in
        # world coords directly - nasty thing is that we need to "localize" the top/bottom regions depth (y width)

        # first calculate the bottom region's centerpoint, and make it into a vector
        btmVect = Blender.Mathutils.Vector(ctrLX,ctrLY + (gripOffset/sizeVect.y) + (btmYOffset/sizeVect.y) + (deltaLY/2) + ((btmdepth/sizeVect.y)/2), mlocal[0].z,1) * l2wMtx
        # next calculate the top region's centerpoint, and make it into a vector
        topVect = Blender.Mathutils.Vector(ctrLX,ctrLY + (topYOffset/sizeVect.y) + (deltaLY/2) - ((topdepth/sizeVect.y)/2), mlocal[7].z,1) * l2wMtx

        # now build up the matrices
        # determine the translation matrices
        btmTrlMtx = Blender.Mathutils.TranslationMatrix(btmVect).resize4x4()
        topTrlMtx = Blender.Mathutils.TranslationMatrix(topVect).resize4x4()

        # determine the rotation eulers:
        # default rotation is similar to the objects rotation
        btmEuler = Blender.Mathutils.Euler(rotEuler)
        topEuler = Blender.Mathutils.Euler(rotEuler)

        # rotate the top euler by 180 degrees around local Z
        topEuler.rotate(180, 'z')

        # make rotation matrices from the eulers
        btmRotMtx = btmEuler.toMatrix().resize4x4()
        topRotMtx = topEuler.toMatrix().resize4x4()

        # combine the matrices!

        IdentityMtx3d = Blender.Mathutils.Matrix([1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,0])
        btmMtx = btmRotMtx + btmTrlMtx - IdentityMtx3d
        topMtx = topTrlMtx + topRotMtx - IdentityMtx3d

        # we now have the following:
        # Bottom region:
        # Matrix btmMtx - VertexList btmMsh - FaceList rgnFcs
        #
        # Top region:
        # Matrix topMtx - VertexList topMsh - FaceList rgnFcs


        # calculate climbHeight and climbOffset

        #climbHeight = int(math.ceil((deltaWZ - 5.42)/2))
        climbHeight = int((deltaWZ - 5.42)/2)
        climbOffset = 0

        print "[AutoLadder Script]"
        print "    Calculated Ladder:"
        print "    Bottom Region Matrix:"
        print btmMtx
        print "    Top Region Matrix:"
        print topMtx
        print "    climbHeight: %d" % climbHeight
        print "    Attempting to create objects:"

        # construct the objects:
        SceneNodeRef=page.prp.getSceneNode().data.getRef()
        # create the bottom region:

        # create the sceneobject
        btmScnobj = page.prp.find(0x01,obj.name + "_bottom",1)
        btmScnobj.data.scene=SceneNodeRef
        # set the coordinates
        btmCoori=page.prp.find(0x15,obj.name + "_bottom",1)
        btmScnobj.data.coordinate=btmCoori.data.getRef()
        btmCoori.data.parentref=btmScnobj.data.getRef()
        btmCoori.data.set_matrices(btmMtx)
        # set the simulation and physical
        btmSimi=page.prp.find(0x1C,obj.name + "_bottom",1)
        btmScnobj.data.simulation=btmSimi.data.getRef()
        btmSimi.data.parentref=btmScnobj.data.getRef()
        btmPhysical=page.prp.find(0x3F,obj.name + "_bottom",1)
        btmSimi.data.fPhysical=btmPhysical.data.getRef()
        btmPhysical.data.fScene=SceneNodeRef
        btmPhysical.data.fSceneObject=btmScnobj.data.getRef()
        btmPhysical.data.export_raw(btmMtx,btmMsh,rgnFcs,4,1)
        # set the ladder specific settings
        btmClimbRegion = page.prp.find(0x00B2,obj.name + "_bottom",1)
        if btmClimbRegion != None:
            btmClimbRegion.data.parentref = btmScnobj.data.getRef()
            # calculate the correct settings

            btmClimbRegion.data.export_raw(btmMtx,0,climbHeight,1)
            print "Loops: %d" % climbHeight
            print "GoingUp: 1"

            # End calculate the right settings
            btmScnobj.data.data2.append(btmClimbRegion.data.getRef())


        # create the top region:

        # create the sceneobject
        topScnobj = page.prp.find(0x01,obj.name + "_top",1)
        topScnobj.data.scene=SceneNodeRef
        # set the coordinates
        topCoori=page.prp.find(0x15,obj.name + "_top",1)
        topScnobj.data.coordinate=topCoori.data.getRef()
        topCoori.data.parentref=topScnobj.data.getRef()
        topCoori.data.set_matrices(topMtx)
        # set the simulation and physical
        topSimi=page.prp.find(0x1C,obj.name + "_top",1)
        topScnobj.data.simulation=topSimi.data.getRef()
        topSimi.data.parentref=topScnobj.data.getRef()
        topPhysical=page.prp.find(0x3F,obj.name + "_top",1)
        topSimi.data.fPhysical=topPhysical.data.getRef()
        topPhysical.data.fScene=SceneNodeRef
        topPhysical.data.fSceneObject=topScnobj.data.getRef()
        topPhysical.data.export_raw(topMtx,topMsh,rgnFcs,4,1)

        # set the ladder specific settings
        topClimbRegion = page.prp.find(0x00B2,obj.name + "_top",1)
        if topClimbRegion != None:
            topClimbRegion.data.parentref = topScnobj.data.getRef()
            # calculate the correct settings

            topClimbRegion.data.export_raw(topMtx,0,climbHeight,0)
            print "Loops: %d" % climbHeight
            print "GoingUp: 0"

            # End calculate the right settings
            topScnobj.data.data2.append(topClimbRegion.data.getRef())


    CreateLadderRegions = staticmethod(_CreateLadderRegions)

    def _ExportRegions(page,obj,scnobj,name):
        objscript = AlcScript.objects.Find(obj.name)

        regiontype = FindInDict(objscript,'region.type',"logic")
        regiontype = FindInDict(objscript,'regiontype',regiontype)
        regiontype = getTextPropertyOrDefault(obj,"regiontype",regiontype)

        print " [LogicHelper]"
        if regiontype.lower() == "climbing":
            plAvLadderMod.Export(page,obj,scnobj,name)
        elif regiontype.lower() == "swimdetect":
            plSwimRegion.Export(page,obj,scnobj,name)
        elif regiontype.lower() == "swim":
            plSwimRegionInterface.Export(page,obj,scnobj,name)
        elif regiontype.lower() == "panic":
            plPanicLinkRegion.Export(page,obj,scnobj,name)
        elif regiontype.lower() == "camera":
            plCameraRegionDetector.Export(page,obj,scnobj,name)
        else:
            logicscript = FindInDict(objscript,'logic',{})
            AlcLogicHelper.ExportLogic(page,logicscript,scnobj)

    ExportRegions = staticmethod(_ExportRegions)

    def _IsRegionDynamic(obj):
        objscript = AlcScript.objects.Find(obj.name)

        try:
            regiontype = objscript['regiontype']
        except:
            regiontype = "logic"
        regiontype = getTextPropertyOrDefault(obj,"regiontype",regiontype)


        if regiontype.lower() == "climbing":
            return True # as climbing regions are their own seekpoints
        elif regiontype.lower() == "swimdetect":
            return False
        elif regiontype.lower() == "swim":
            return False
        else:
            return True # as it won't hurt, and may cause problems wiht selfseekanimation quickscript regions
                         # if it's not done

    IsRegionDynamic= staticmethod(_IsRegionDynamic)

    def _ExportLogic(page,script,scnobj):
        # Export of actions is separate in the logic helper
        actions = FindInDict(script,"actions",None)
        if type(actions) == dict: # It should be a list - if it's a dict, make it a list with one entry
            actions = [actions,]
        if type(actions) == list:
            AlcLogicHelper.ExportActions(page,actions,scnobj)
        else:
            print "   No actions in list"
            print actions

        print "   Exporting modifiers"
        # export of modifiers is delegated to the plInterfaceInfoModifier
        logicmods = FindInDict(script,"modifiers",None)
        if type(logicmods) == dict: # It should be a list - if it's a dict, make it a list with one entry
            logicmods = [logicmods,]
        if type(logicmods) == list:
            plInterfaceInfoModifier.Export(page,logicmods,scnobj)
        else:
            print "   No modifiers"
            print logicmods

    ExportLogic = staticmethod(_ExportLogic)

    def _ExportActions(page,script,scnobj):
        print "   Exporting actions"
        if type(script) == list:
            for actscript in script:
                if type(actscript) == dict:
                    hide = bool( str(FindInDict(actscript,'hide','false') ).lower() == 'true')

                    # Get the tag or name....
                    tag = FindInDict(actscript,"tag","")

                    if not tag == "":
                        handle = str(scnobj.data.Key.name) + "_" + str(tag)
                    else:
                        handle = str(scnobj.data.Key.name)

                    # if we have a name, then that one overrides the tag
                    name = FindInDict(actscript,"name",None)
                    if not name is None:
                        handle = name


                    # Now parse the action data
                    _type = str(FindInDict(actscript,'type','none'))
                    plobj = None
                    if _type == "pythonfile":
                        plobj = plPythonFileMod.FindCreate(page,handle)
                        pscript = FindInDict(actscript,"pythonfile",{})
                        plobj.data.export_script(pscript,scnobj)
                    elif _type == "responder":
                        plobj = plResponderModifier.FindCreate(page,handle)
                        pscript = FindInDict(actscript,"responder",{})
                        plobj.data.export_script(pscript,scnobj)
                    elif _type == "oneshot":
                        # this one has the possibility to save to another scene object
                        # and it must be associated, so we cannot hide it...
                        plobj = plOneShotMod.FindCreate(page,handle)
                        pscript = FindInDict(actscript,"oneshot",{})
                        plobj.data.export_script(pscript,scnobj)
                        plobj = None # assigning to this or another scene object was done in the export
                    elif _type == "sittingmod":
                        pscript = FindInDict(actscript,"sittingmod",{})
                        plobj = plSittingModifier.FindCreate(page, handle)
                        plobj.data.export_script(pscript,scnobj)
                    elif _type == "footmgr":
                        pscript = FindInDict(actscript,"footmgr",{})
                        plobj = plDynaFootMgr.FindCreate(page, handle)
                        plobj.data.export_script(pscript)
                    elif _type == "puddlemgr":
                        pscript = FindInDict(actscript,"puddlemgr",{})
                        plobj = plDynaPuddleMgr.FindCreate(page, handle)
                        plobj.data.export_script(pscript)
                    elif _type == "ripplevsmgr":
                        pscript = FindInDict(actscript,"ripplevsmgr",{})
                        plobj = plDynaRippleVSMgr.FindCreate(page, handle)
                        plobj.data.export_script(pscript)
                    elif _type == "ripplemgr":
                        pscript = FindInDict(actscript,"ripplemgr",{})
                        plobj = plDynaRippleMgr.FindCreate(page, handle)
                        plobj.data.export_script(pscript)
                    if not plobj is None:
                        if not hide:
                            scnobj.data.addModifier(plobj)

    ExportActions = staticmethod(_ExportActions)

    def _RunQuickScript(scripttext,scnobj):
        script = AlcScript(scripttext).GetRootScript()
        AlcLogicHelper.ExportLogic(page,script,scnobj)

    RunQuickScript = staticmethod(_RunQuickScript)


class plInterfaceInfoModifier(plSingleModifier):
    def __init__(self,parent,name="unnamed",type=0x00CB):
        plSingleModifier.__init__(self,parent,name,type)
        #format
        self.fKeyList=hsTArray([0x2D],self.getVersion()) # modifiers Type 2D (LogicModifier)
        ####

        self.LogicModIdx = 0

    def _Find(page,name):
        return page.find(0x00CB,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x00CB,name,1)
    FindCreate = staticmethod(_FindCreate)

    def changePageRaw(self,sid,did,stype,dtype):
        plSingleModifier.changePageRaw(self,sid,did,stype,dtype)
        self.fKeyList.changePageRaw(sid,did,stype,dtype)


    def read(self,stream):
        plSingleModifier.read(self,stream)
        self.fKeyList.read(stream)


    def write(self,stream):
        plSingleModifier.write(self,stream)
        self.fKeyList.update(self.Key)
        self.fKeyList.write(stream)

    def addLogicMod(self,lmod):
        self.fKeyList.append(lmod.data.getRef())


    def export_script(self,script,scnobj):
        if type(script) == list:
            for logicscript in script:
                # find tag
                tag = str(FindInDict(logicscript,"tag",""))
                # Allow the first logicmodifier to go wihtout a tag, but force their index as tag on subsequent
                # logicmods
                if tag == "":
                    if self.LogicModIdx == 0:
                        handle = str(scnobj.data.Key.name)
                    else:
                        handle = str(scnobj.data.Key.name) + "_" + str(self.LogicModIdx)
                else:
                    handle = str(scnobj.data.Key.name) + "_" + str(tag)

                self.LogicModIdx += 1
                # if we have a name, then that one overrides the tag
                name = FindInDict(logicscript,"name",None)
                if not name is None:
                    handle = name

                logicmod = plLogicModifier.FindCreate(self.getRoot(),handle)
                logicmod.data.export_script(logicscript,scnobj)

                self.addLogicMod(logicmod)
                scnobj.data.addModifier(logicmod)

    def _Export(page,script,scnobj):
        print "   Exporting modifiers"
        handle = str(scnobj.data.Key.name)
        intf_infomod = plInterfaceInfoModifier.FindCreate(page,handle)
        intf_infomod.data.export_script(script,scnobj)
        scnobj.data.addModifier(intf_infomod)

    Export = staticmethod(_Export)

class plRandomCommandMod(plSingleModifier):
    def __init__(self,parent,name="unnamed",type=None):
        plSingleModifier.__init__(self,parent,name,type)
        self.fMode = 0x0
        self.fState = 0x0
        self.fMinDelay = 0.0
        self.fMaxDelay = 0.0
    def read(self, stream):
        plSingleModifier.read(self, stream)
        stream.ReadByte(self.fMode)
        stream.ReadByte(self.fState)
        stream.ReadFloat(self.fMinDelay)
        stream.ReadFloat(self.fMaxDelay)
    def write(self, stream):
        plSingleModifier.write(self, stream)
        stream.WriteByte(self.fMode)
        stream.WriteByte(self.fState)
        stream.WriteFloat(self.fMinDelay)
        stream.WriteFloat(self.fMaxDelay)

class plLogicModBase(plSingleModifier):                   #Type 0x4F
    Flags = \
    { \
        "kLocalElement"      : 0, \
        "kReset"             : 1, \
        "kTriggered"         : 2, \
        "kOneShot"           : 3, \
        "kRequestingTrigger" : 4, \
        "kTypeActivator"     : 5, \
        "kMultiTrigger"      : 6  \
    }
    def __init__(self,parent,name="unnamed",type=None):
        plSingleModifier.__init__(self,parent,name,type)
        self.MsgCount = 0x00000000
        self.fCommandList = [] # plMessages
        self.fNotify = PrpMessage(0x02E8,self.getVersion())
        self.fFlags = hsBitVector()
        self.fDisabled = False

    def read(self,buf):
        plSingleModifier.read(self,buf)
        count = buf.Read32()
        for i in range(count):
            cmd = PrpMessage.FromStream(buf)
            self.fCommandList.append(cmd)

        self.fNotify = PrpMessage.FromStream(buf)
        self.fFlags.read(buf)
        self.fDisabled = buf.ReadBool()

    def write(self,buf):
        plSingleModifier.write(self,buf)
        buf.Write32(len(self.fCommandList))

        for cmd in self.fCommandList:
            PrpMessage.ToStream(buf,cmd)

        PrpMessage.ToStream(buf,self.fNotify)
        self.fFlags.write(buf)
        buf.WriteBool(self.fDisabled)

class plLogicModifier(plLogicModBase):

    ScriptFlags = \
    { \
        "localelement"      : 0, \
        "reset"             : 1, \
        "triggered"         : 2, \
        "oneshot"           : 3, \
        "requestingtrigger" : 4, \
        "typeactivator"     : 5, \
        "multitrigger"      : 6  \
    }

    Cursors = \
    { \
        "kNoChange"         :  0, \
        "kCursorUp"         :  1, \
        "kCursorLeft"       :  2, \
        "kCursorRight"      :  3, \
        "kCursorDown"       :  4, \
        "kCursorPoised"     :  5, \
        "kCursorClicked"    :  6, \
        "kCursorUnClicked"  :  7, \
        "kCursorHidden"     :  8, \
        "kCursorOpen"       :  9, \
        "kCursorGrab"       : 10, \
        "kCursorArrow"      : 11, \
        "kNullCursor"       : 12  \
    }

    ScriptCursors = \
    { \
        "nochange"   :  0, \
        "up"         :  1, \
        "left"       :  2, \
        "right"      :  3, \
        "down"       :  4, \
        "poised"     :  5, \
        "clicked"    :  6, \
        "unclicked"  :  7, \
        "hidden"     :  8, \
        "open"       :  9, \
        "grab"       : 10, \
        "arrow"      : 11, \
    }


    def __init__(self,parent,name="unnamed",type=0x002D):
        plLogicModBase.__init__(self,parent,name,type)
        #format
        self.fConditionList = hsTArray([0x32,0x37,0x3E,0xA6],self.getVersion(),True)
        self.fMyCursor = 1 #U32 - 1 or 5 defaults to 1

    def _Find(page,name):
        return page.find(0x002D,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x002D,name,1)
    FindCreate = staticmethod(_FindCreate)

    def changePageRaw(self,sid,did,stype,dtype):
        plLogicModBase.changePageRaw(self,sid,did,stype,dtype)

    def read(self,stream):
        plLogicModBase.read(self,stream)
        self.fConditionList.read(stream)
        self.fMyCursor = stream.Read32()

    def write(self,stream):
        plLogicModBase.write(self,stream)
        self.fConditionList.write(stream)
        stream.Write32(self.fMyCursor)

    def addCondition(self,obj):
        self.fConditionList.append(obj.data.getRef())

    def addReceiver(self,mod):
        print "  Appending Receiver:",mod.data.getRef()
        self.fNotify.data.fReceivers.append(mod.data.getRef())

    def export_script(self,script,scnobj):

        if type(script) == dict:
            print "  [LogicModifier %s]"%(str(self.Key.name))
            # Handle flags first:
            flags = FindInDict(script,"flags",None)
            if type(flags) == list:
                self.fFlags.clear()
                print "   Initial self.fFlags is:",self.fFlags
                # set the flags in the list
                for flag in flags:
                    if plLogicModifier.ScriptFlags.has_key(str(flag).lower()):
                        self.fFlags[plLogicModifier.ScriptFlags[str(flag)]] = 1
                        print "   Got flag: %s - %X"%(str(flag),plLogicModifier.ScriptFlags[str(flag)])
                        print "   self.fFlags is now:",self.fFlags
            else:
                # set default flags...
                self.fFlags[plLogicModBase.Flags["kMultiTrigger"]] = 1

            # logicmod settings next
            cursor = str(FindInDict(script,"cursor","up"))
            if plLogicModifier.ScriptCursors.has_key(cursor.lower()):
                self.fMyCursor = plLogicModifier.ScriptCursors[cursor.lower()]

            # followed by conditions
            print "   Conditions:"
            conditions = list(FindInDict(script,"conditions",[]))
            for condscript in conditions:
                plConditionalObject.Export(self.getRoot(),condscript,scnobj,self.parent)

            # next detectors
            print "   Activators:"
            activators = list(FindInDict(script,"activators",[]))
            for activatorscript in activators:
                plDetectorModifier.Export(self.getRoot(),activatorscript,scnobj,self.parent)

            # and finally by actions

            print "   Actions:"
            actions = list(FindInDict(script,"actions",[]))

            print actions
            uniqueindex = 1
            for actscript in actions:
                _type = FindInDict(actscript,"type",None)

                if not _type is None:
                    action_type = str(_type)
                    print "  Action is of type",action_type

                    ref = str(FindInDict(actscript,"ref",None))
                    refparser = ScriptRefParser(self.getRoot(),str(scnobj.data.Key.name))


                    plobj = None
                    if action_type == "pythonfile":
                        # plPythonFileMod
                        print "Locating python file reference '%s'"%(ref)
                        refparser.SetDefaultType(0x00A2)
                        refparser.SetAllowList([0x00A2,])
                        plobj = refparser.MixedRef_FindCreate(ref)
                    elif action_type == "responder":
                        # plResponderModifier
                        print "Locating responder mod reference '%s'"%(ref)
                        refparser.SetDefaultType(0x007C)
                        refparser.SetAllowList([0x007C,])
                        plobj = refparser.MixedRef_FindCreate(ref)
                    elif action_type == "sittingmod":
                        # plSittingModifier
                        print "Locating sitting mod reference '%s'"%(ref)
                        refparser.SetDefaultType(0x00AE)
                        refparser.SetAllowList([0x00AE,])
                        plobj = refparser.MixedRef_FindCreate(ref)
                    elif action_type == "oneshot":
                        print "Creating Responder modifier to oneshot reference '%s'"%(ref)
                        # plOneShotMod
                        refparser.SetDefaultType(0x0077)
                        refparser.SetAllowList([0x0077,])

                        oneshotmod = refparser.MixedRef_FindCreate(ref) # ensure existence of this mod
                        plobj = plResponderModifier.FindCreate(self.getRoot(),str(scnobj.data.Key.name) + "_PyPRP_" +str(uniqueindex))
                        uniqueindex += 1

                        # build up the respondermodifier from a small piece of alcscript:

                        txt  = "states:\n"
                        txt += "  - cmds:\n"
                        txt += "      - type: oneshotmsg\n"
                        txt += "        params:\n"
                        txt += "            receivers:\n"
                        txt += "              - oneshotmod:" + str(oneshotmod.data.Key.name) + "\n"
                        txt += "        waiton: -1\n"
                        txt += "    nextstate: 0\n"
                        txt += "    waittocmd: 0\n"
                        txt += "curstate: 0\n"
                        txt += "flags:\n"
                        txt += "  - detecttrigger\n"

                        plobj.data.export_script(AlcScript(txt).GetRootScript(),scnobj)
                        # Also add this new respondermodifier to the scene node..
                        scnobj.data.addModifier(plobj)

                    if not plobj is None:
                        # add it as receiver to self
                        self.addReceiver(plobj)



#################
##             ##
##  Detectors  ##
##             ##
#################
class plDetectorModifier(plSingleModifier):                 #Type 0x24
    def __init__(self,parent,name="unnamed",type=None):
        plSingleModifier.__init__(self,parent,name,type)
        #Format
        if (self.getVersion()==6):
            self.fReceivers = hsTArray([],6)
        else:
            self.fReceivers = hsTArray([0x002D],5)
        self.fRemoteMod = UruObjectRef(self.getVersion())
        self.fProxyKey = UruObjectRef(self.getVersion())

    def read(self,buf):
        plSingleModifier.read(self,buf)
        self.fReceivers.ReadVector(buf)
        self.fRemoteMod.read(buf)
        self.fProxyKey.read(buf)

    def write(self,buf):
        plSingleModifier.write(self,buf)
        self.fReceivers.update(self.Key)
        self.fReceivers.WriteVector(buf)
        self.fRemoteMod.write(buf)
        self.fProxyKey.write(buf)


    def changePageRaw(self,sid,did,stype,dtype):
        plSingleModifier.changePageRaw(self,sid,did,stype,dtype)
        self.logic.changePageRaw(sid,did,stype,dtype)
        self.fRemoteMod.changePageRaw(sid,did,stype,dtype)
        self.fProxyKey.changePageRaw(sid,did,stype,dtype)

    def addReceiver(self,mod):
        self.fReceivers.append(mod.data.getRef())

    def addRemoteMod(self,mod):
        self.fRemoteMod = mod.data.getRef()

    def addProxyKey(self,key):
        self.fProxyKey = key.data.getRef()

    def export_script(self,script,scnobj,logicmod,activatorCO=None):
        self.addReceiver(logicmod)

        # check where we should add ourself..
        remote = FindInDict(script,"remote",None)
        hide = bool( str(FindInDict(script,'hide','false') ).lower() == 'true')

        if not hide:
            if not remote is None and str(remote) != "":
                # if a name was given, usethat one to Find (or Create) the scene object ofthe seek point
                ext_scnobj = plSceneObject.FindCreate(self.getRoot(),remote)

                ext_scnobj.data.addModifier(self.parent)
            else:
                # else, add it to the "scene object" (which can occasinally be an ActivatorCondObj)
                scnobj.data.addModifier(self.parent)

        if not activatorCO is None:
            activatorCO.data.addModifier(self.parent)

    def _Export(page,script,scnobj,logicmod,activatorCO=None):
        # gets the script dictionary for one decectormodifier from plLogicModifier
        if type(script) == dict:
            _type = str(FindInDict(script,"type",None)).lower()

            # allow for tag to the object
            tag = FindInDict(script,"tag",None)
            if tag is None:
                handle = str(logicmod.data.Key.name)
            else:
                handle = str(logicmod.data.Key.name) + "_" + str(tag)

            # or even let a "name" property override that...
            name = FindInDict(script,"name",None)
            if not name is None:
                handle = str(name)

            print "    Found Activator %s of type:"%(handle), _type


            detmod = None
            if _type == "objectinvolume":
                detmod = plObjectInVolumeDetector.FindCreate(page,handle)
            elif _type == "objectinvolumeandfacing":
                detmod = plObjectInVolumeAndFacingDetector.FindCreate(page,handle)
            elif _type == "picking":
                detmod = plPickingDetector.FindCreate(page,handle)

            if not detmod == None:
                # Add the logicmodifier to the new class
                detmod.data.export_script(script,scnobj,logicmod,activatorCO)
    Export = staticmethod(_Export)



class plPickingDetector(plDetectorModifier):                    #Type 0x002B
    def __init__(self,parent,name="unnamed",type=0x002B):
        #Gotta figure out how to pass the correct type from M5
        #self.getVersion() & plDectorModifier.getVersion() puke :\
        plDetectorModifier.__init__(self,parent,name,type)

    def _Find(page,name):
        return page.find(0x002B,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x002B,name,1)
    FindCreate = staticmethod(_FindCreate)

    def export_script(self,script,scnobj,logicmod,activatorCO=None):
        plDetectorModifier.export_script(self,script,scnobj,logicmod,activatorCO)


class plCollisionDetector(plDetectorModifier):              #Type 0x2C
    Type = \
    { \
        "kTypeEnter"    :  0x1, \
        "kTypeExit"     :  0x2, \
        "kTypeAny"      :  0x4, \
        "kTypeUnEnter"  :  0x8, \
        "kTypeUnExit"   : 0x10, \
        "kTypeBump"     : 0x20  \
    }

    ScriptType = \
    { \
        "enter"    :  0x1, \
        "exit"     :  0x2, \
        "any"      :  0x4, \
        "unenter"  :  0x8, \
        "unexit"   : 0x10, \
        "bump"     : 0x20  \
    }

    def __init__(self,parent,name="unnamed",type=None):
        plDetectorModifier.__init__(self,parent,name,type)
        self.fType = 0

    def read(self,buf):
        plDetectorModifier.read(self,buf)
        self.fType = buf.ReadByte()

    def write(self,buf):
        plDetectorModifier.write(self,buf)
        buf.WriteByte(self.fType)

    def export_script(self,script,scnobj,logicmod,activatorCO=None):
        plDetectorModifier.export_script(self,script,scnobj,logicmod,activatorCO)
        types = list(FindInDict(script,"triggers",[]))

        if len(types) > 0:
            self.fType = 0
            for _type in types:
                if plCollisionDetector.ScriptType.has_key(_type.lower()):
                    self.fType |= plCollisionDetector.ScriptType[_type.lower()]

class plObjectInVolumeDetector(plCollisionDetector):
    def __init__(self,parent,name="unnamed",type=0x007B):
        plCollisionDetector.__init__(self,parent,name,type)

    def _Find(page,name):
        return page.find(0x007B,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x007B,name,1)
    FindCreate = staticmethod(_FindCreate)

    def read(self,stream):
        plCollisionDetector.read(self,stream)

    def write(self,stream):
        plCollisionDetector.write(self,stream)

    def import_obj(self,obj):
        pass

    def export_script(self,script,scnobj,logicmod,activatorCO=None):
        plCollisionDetector.export_script(self,script,scnobj,logicmod,activatorCO)
        # create an VolumeSensorConditionalObject - if no name specified, use own name

        volsens = str(FindInDict(script,"volumesensor","/"))

        if volsens is None:
            vsenshandle = str(self.Key.name)
        else:
            vsenshandle = ScriptRefParser.TagString_ParseName(volsens,str(logicmod.data.Key.name))

        vsobj = plVolumeSensorConditionalObject.Find(self.getRoot(),vsenshandle)
        if not vsobj is None:
            self.addReceiver(vsobj)
        # if the logicmod adds a volumesensor too, it will make one with the same name, so it will link here...

class plObjectInVolumeAndFacingDetector(plObjectInVolumeDetector): # type 0x00E7
    def __init__(self,parent,name="unnamed",type=0x00E7):
        plObjectInVolumeDetector.__init__(self,parent,name,type)
        self.fFacingTolerance = 0.1 # probably in radians, so give a bit of an edge
        self.fNeedWalkingForward = False # let's default to no walking forward needed

    def _Find(page,name):
        return page.find(0x00E7,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x00E7,name,1)
    FindCreate = staticmethod(_FindCreate)

    def read(self,stream):
        plObjectInVolumeDetector.read(self,stream)
        self.fFacingTolerance = stream.ReadFloat()
        self.fNeedWalkingForward = stream.ReadBool()


    def write(self,stream):
        plObjectInVolumeDetector.write(self,stream)
        stream.WriteFloat(self.fFacingTolerance)
        stream.WriteBool(self.fNeedWalkingForward)


    def export_script(self,script,scnobj,logicmod,activatorCO=None):
        plObjectInVolumeDetector.export_script(self,script,scnobj,logicmod,activatorCO)
        if str(FindInDict(script,"needwalkfwd","false")).lower() == True:
            self.fNeedWalkingForward = True
        else:
            self.fNeedWalkingForward = True

        self.fFacingTolerance = float(FindInDict(script,"facingtolerance",self.fFacingTolerance))

class plPanicLinkRegion(plCollisionDetector):
    def __init__(self,parent,name="unnamed",type=0x00FC):
        plCollisionDetector.__init__(self,parent,name,type)
        self.fPlayLinkOutAnim = True

    def _Find(page,name):
        return page.find(0x00FC,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x00FC,name,1)
    FindCreate = staticmethod(_FindCreate)

    def changePageRaw(self,sid,did,stype,dtype):
        plCollisionDetector.changePageRaw(self,sid,did,stype,dtype)


    def read(self,stream):
        plCollisionDetector.read(self,stream)
        self.fPlayLinkOutAnim = stream.ReadBool()

    def write(self,stream):
        plCollisionDetector.write(self,stream)
        stream.WriteBool(self.fPlayLinkOutAnim)

    def import_obj(self,obj):
        # The only thing this thing does is set the regiontype property
        try:
            obj.removeProperty("regiontype")
        except:
            pass

        obj.addProperty("regiontype","paniclink")
        pass

    def export_obj(self,obj):
        pass

    def _Export(page,obj,scnobj,name):
        #set the coordinate interface
        plrgn=plPanicLinkRegion.FindCreate(page,name)
        plrgn.data.export_obj(obj)
        scnobj.data.data2.append(plrgn.data.getRef())

    Export = staticmethod(_Export)



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
            msg = PrpMessage.FromStream(stream,self.getVersion())
            self.fMessages.append(msg)

    def write(self,stream):
        plDetectorModifier.write(self,stream)

        stream.Write32(len(self.fMessages))
        for msg in self.fMessages:
            PrpMessage.ToStream(stream,msg)



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
            StoreInDict(msgscript,"camera",str(msg.data.fNewCam.Key.name))

            if self.fMessages[0].data.fCmd[plCameraMsg.ModCmds["kSetAsPrimary"]] == 1:
                StoreInDict(msgscript,"setprimary",True)
            else:
                StoreInDict(msgscript,"setprimary",False)

            msgscripts.append(msgscript)

        StoreInDict(objscript,"region.camera.cameras",msgscripts)

    def export_obj(self,obj,scnobj):
        print "  [CameraRegionDetector %s]"%(str(self.Key.name))
        objscript = AlcScript.objects.Find(obj.name)

        messages = list(FindInDict(objscript,"region.camera.messages"))

        for camscript in messages:
            # Create a new camera message
            msg = PrpMessage(0x020A,self.getVersion())

            refparser = ScriptRefParser(self.getRoot(),"",False,[])
            msg.data.export_script(camscript,refparser)

            self.fMessages.append(msg)

    def _Export(page,obj,scnobj,name):
        #set the coordinate interface
        plcamdetect=plCameraRegionDetector.FindCreate(page,name)
        plcamdetect.data.export_obj(obj,scnobj)
        scnobj.data.addModifier(plcamdetect)

    Export = staticmethod(_Export)

class plSubWorldRegionDetector(plDetectorModifier):
    def __init__(self,parent=None,name="unnamed",type=0x00F3):
        plDetectorModifier.__init__(self,parent,name,type)
        self.fSub = UruObjectRef()
        self.fOnExit = 0
    def _Find(page,name):
        return page.find(0x00F3,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x00F3,name,1)
    FindCreate = staticmethod(_FindCreate)
    
    def export_obj(self,obj):
        objscript = AlcScript.objects.Find(obj.name)
        self.fOnExit = FindInDict(objscript, "region.onexit", self.fOnExit)
        ref = FindInDict(objscript,'region.subworld',None)
        if ref:
            sceneObj = prp_ObjClasses.plSceneObject.FindCreate(self.getRoot(),ref)
            self.fSub = sceneObj.data.getRef()

    def _Export(page, obj, scnobj, name):
        SubWorldRegionDetector = plSubWorldRegionDetector.FindCreate(page, name)
        SubWorldRegionDetector.data.export_obj(obj)
        # attach to sceneobject
        scnobj.data.addModifier(SubWorldRegionDetector)
    Export = staticmethod(_Export)

    def read(self, s):
        plDetectorModifier.read(self, s)
        self.fSub.read(s)
        self.fOnExit = s.ReadBool()

    def write(self, s):
        plDetectorModifier.write(self, s)
        self.fSub.write(s)
        s.WriteBool(self.fOnExit)

###########################
##                       ##
##  Conditional Objects  ##
##                       ##
###########################

class plConditionalObject(hsKeyedObject):                   #Type 0x2E

    Flags = \
    { \
        "kLocalElement" : 0, \
        "kNOT"          : 1  \
    }

    def __init__(self,parent,name="unnamed",type=0x002E):
        hsKeyedObject.__init__(self,parent,name,type)
        self.bSatisfied = False
        self.fToggle = False

    def _Find(page,name):
        return page.find(0x002E,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x002E,name,1)
    FindCreate = staticmethod(_FindCreate)

    def read(self,buf):
        hsKeyedObject.read(self,buf)
        self.bSatisfied = buf.ReadBool()
        self.fToggle = buf.ReadBool()

    def write(self,buf):
        hsKeyedObject.write(self,buf)
        buf.WriteBool(self.bSatisfied)
        buf.WriteBool(self.fToggle)

    def export_script(self,script,scnobj,logicmod):
        if str(FindInDict(script,"satisfied",str(self.bSatisfied))).lower() == "true":
            self.bSatisfied = True
        else:
            self.bSatisfied = False

        if str(FindInDict(script,"toggle",str(self.fToggle))).lower() == "true":
            self.fToggle = True
        else:
            self.fToggle = False

    def _Export(page,script,scnobj,logicmod):
        # gets the script dictionary for one decectormodifier from plLogicModifier
        if type(script) == dict:
            _type = str(FindInDict(script,"type",None)).lower()

            # allow for id (maybe this should be more accurately called "tag"
            tag = FindInDict(script,"tag",None)
            if tag is None:
                handle = str(logicmod.data.Key.name)
            else:
                handle = str(logicmod.data.Key.name) + "_" + str(tag)

            name = FindInDict(script,"name",None)
            if not name is None:
                handle = str(name)

            print "    Found Condition %s of type:"%(handle), _type

            condobj = None
            if _type == "volumesensor":
                condobj = plVolumeSensorConditionalObject.FindCreate(page,handle)
            elif _type == "facing":
                condobj = plFacingConditionalObject.FindCreate(page,handle)
            elif _type == "activator":
                condobj = plActivatorConditionalObject.FindCreate(page,handle)
            elif _type == "objectinbox":
                condobj = plObjectInBoxConditionalObject.FindCreate(page,handle)

            if not condobj == None:
                # Add the new class to the logicmodifier
                logicmod.data.addCondition(condobj)
                condobj.data.export_script(script,scnobj,logicmod)

    Export = staticmethod(_Export)

class plObjectInBoxConditionalObject(plConditionalObject):
    def __init__(self,parent,name="unnamed",type=0x0037):
        plConditionalObject.__init__(self,parent,name,type)

    def _Find(page,name):
        return page.find(0x0037,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0037,name,1)
    FindCreate = staticmethod(_FindCreate)

    def export_script(self,script,scnobj,logicmod):
        plConditionalObject.export_script(self,script,scnobj,logicmod)

class plVolumeSensorConditionalObject(plConditionalObject):
    Type = \
    { \
        "kTypeEnter" : 0x1,\
        "kTypeExit"  : 0x2 \
    }

    def __init__(self,parent,name="unnamed",type=0x00A6):
        plConditionalObject.__init__(self,parent,name,type)
        #format
        self.fTrigNum=-1 #
        self.fType=1 #
        self.fFirst = False

    def _Find(page,name):
        return page.find(0x00A6,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x00A6,name,1)
    FindCreate = staticmethod(_FindCreate)

    def changePageRaw(self,sid,did,stype,dtype):
        plConditionalObject.changePageRaw(self,sid,did,stype,dtype)


    def read(self,stream):
        plConditionalObject.read(self,stream)

        self.fTrigNum = stream.ReadSigned32()
        self.fType = stream.Read32() # Was "direction"
        self.fFirst = stream.ReadBool()


    def write(self,stream):
        plConditionalObject.write(self,stream)
        stream.WriteSigned32(self.fTrigNum)
        stream.Write32(self.fType)
        stream.WriteBool(self.fFirst)

    def import_obj(self,obj):
        pass

    def export_script(self,script,scnobj,logicmod):
        plConditionalObject.export_script(self,script,scnobj,logicmod)

        if str(FindInDict(script,"direction","exit").lower()) == "enter":
            self.fType = plVolumeSensorConditionalObject.Type["kTypeEnter"]
        else:
            self.fType = plVolumeSensorConditionalObject.Type["kTypeExit"]

        self.fFirst = bool(str(FindInDict(script,"isfirst",str(self.fFirst)).lower()) == "true")

        self.fTrigNum = int(FindInDict(script,"trignum",self.fTrigNum))

    def _FindCreate(page,name):
        plobj = page.find(0x00A6,name,1)
        return plobj
    FindCreate = staticmethod(_FindCreate)


class plActivatorConditionalObject(plConditionalObject):
    def __init__(self,parent,name="unnamed",type=0x0032):
        plConditionalObject.__init__(self,parent,name,type)
        #format
        self.fActivators = hsTArray()

    def _Find(page,name):
        return page.find(0x0032,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0032,name,1)
    FindCreate = staticmethod(_FindCreate)

    def changePageRaw(self,sid,did,stype,dtype):
        plConditionalObject.changePageRaw(self,sid,did,stype,dtype)
        self.fActivators.changePageRaw(sid,did,stype,dtype)

    def read(self,stream):
        plConditionalObject.read(self,stream)
        self.fActivators.ReadVector(stream)

    def write(self,stream):
        plConditionalObject.write(self,stream)
        self.fActivators.update(self.Key)
        self.fActivators.WriteVector(stream)

    def addModifier(self,plobj):
        self.fActivators.append(plobj.data.getRef())

    def export_script(self,script,scnobj,logicmod):
        plConditionalObject.export_script(self,script,scnobj,logicmod)

        activators = list(FindInDict(script,"activators",[]))
        for activatorscript in activators:
            plDetectorModifier.Export(self.getRoot(),activatorscript,scnobj,logicmod,self.parent)


class plFacingConditionalObject(plConditionalObject):
    def __init__(self,parent,name = "unnamed"):
        plConditionalObject.__init__(self,parent,name,0x3E)
        self.fTolerance = -1.0
        self.fDirectional = False

    def _Find(page,name):
        return page.find(0x003E,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x003E,name,1)
    FindCreate = staticmethod(_FindCreate)


    def read(self,stream):
        plConditionalObject.read(self,stream)
        self.fTolerance = stream.ReadFloat()
        self.fDirectional = stream.ReadBool()


    def write(self,stream):
        plConditionalObject.write(self,stream)
        stream.WriteFloat(self.fTolerance)
        stream.WriteBool(self.fDirectional)

    def export_script(self,script,scnobj,logicmod):
        plConditionalObject.export_script(self,script,scnobj,logicmod)

        self.fTolerance = float(FindInDict(script,'tolerance',self.fTolerance))

        if str(FindInDict(script,'directional','false')).lower() == "true":
            self.fDirectional = True
        else:
            self.fDirectional = False


#################
##             ##
##  Modifiers  ##
##             ##
#################
class plMultistageBehMod(plSingleModifier):
    def __init__(self,parent,name="unnamed",type=0x00C1):
        plSingleModifier.__init__(self,parent,name,type)

        self.fStages = []
        self.fFreezePhys = True #this+0x70
        self.fSmartSeek = True #this+0x71
        self.fReverseFBControlsOnRelease = False #this+0x72
        self.fReceivers = hsTArray()


    def read(self, s):
        plSingleModifier.read(self, s)

        self.fFreezePhys = s.ReadBool()
        self.fSmartSeek = s.ReadBool()
        self.fReverseFBControlsOnRelease = s.ReadBool()

        count = s.Read32()
        for i in range(count):
            self.fStages[i] = plAnimStage()
            self.fStages[i].read(s)

        self.fReceivers.ReadVector(s)


    def write(self, s):
        plSingleModifier.write(self, s)

        s.WriteBool(self.fFreezePhys)
        s.WriteBool(self.fSmartSeek)
        s.WriteBool(self.fReverseFBControlsOnRelease)

        s.Write32(len(self.fStages))
        for stage in self.fStages:
            stage.write(s)

        self.fReceivers.WriteVector(s)

class plSittingModifier(plSingleModifier):
    Flags = \
    { \
        "kApproachFront"  :  0x1, \
        "kApproachLeft"   :  0x2, \
        "kApproachRight"  :  0x4, \
        "kApproachRear"   :  0x8, \
        "kApproachMask"   :  0xF, \
        "kDisableForward" : 0x10  \
    }

    def __init__(self,parent,name = "unnamed"):
        plSingleModifier.__init__(self,parent,name,0x00AE)

        self.fMiscFlags = 0
        self.fNotifyKeys = []

    def _Find(page,name):
        return page.find(0x00AE,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x00AE,name,1)
    FindCreate = staticmethod(_FindCreate)

    def read(self,stream):
        plSingleModifier.read(self,stream)

        self.fMiscFlags = stream.ReadByte()
        count = stream.Read32()
        for i in range(count):
            key = UruObjectref()
            key.read(stream)
            self.fNotifyKeys.append(key)

    def write(self,stream):
        plSingleModifier.write(self,stream)

        stream.WriteByte(self.fMiscFlags)
        stream.Write32(len(self.fNotifyKeys))
        for key in self.fNotifyKeys:
            key.write(stream)

    def export_obj(self,obj):
        self.fMiscFlags = 0x1

    def export_script(self, script, scnobj):
        self.fMiscFlags = FindInDict(script, "miscflags", 1)

    def _Export(page,obj,scnobj,name):
        mod= plSittingModifier.FindCreate(page,name)
        mod.data.export_obj(obj)
        scnobj.data.addModifier(mod)

    Export = staticmethod(_Export)


class plOneShotMod(plMultiModifier):
    def __init__(self,parent,name="unnamed",type=0x0077):
        plMultiModifier.__init__(self,parent,name,type)
        self.fAnimName = ""
        self.fSeekDuration = 2.0
        self.fDrivable = False
        self.fReversable = False
        self.fSmartSeek = True
        self.fNoSeek = False

    def _Find(page,name):
        return page.find(0x0077,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0077,name,1)
    FindCreate = staticmethod(_FindCreate)

    def read(self,stream):
        plMultiModifier.read(self,stream)
        self.fAnimName = stream.ReadSafeString()
        self.fSeekDuration = stream.ReadFloat()
        self.fDrivable = stream.ReadBool()
        self.fReversable = stream.ReadBool()
        self.fSmartSeek = stream.ReadBool()
        self.fNoSeek = stream.ReadBool()

    def write(self,stream):
        plMultiModifier.write(self,stream)
        stream.WriteSafeString(self.fAnimName)
        stream.WriteFloat(self.fSeekDuration)
        stream.WriteBool(self.fDrivable)
        stream.WriteBool(self.fReversable)
        stream.WriteBool(self.fSmartSeek)
        stream.WriteBool(self.fNoSeek)

    def export_script(self,script,scnobj=None):
        print "   [OneShotMod %s]"%(str(self.Key.name))
        # allow object to be customized given a given script....


        # check where we should add ourself..
        remote = FindInDict(script,"remote",None)
        if not remote is None and str(remote) != "":
            # if a name was given, usethat one to Find (or Create) the scene object ofthe seek point
            ext_scnobj = plSceneObject.FindCreate(self.getRoot(),remote)

            # in case it won't be exported beyond this, add an empty coordinateinterface...
            # but only if no other coordinateinterface was set...
            if ext_scnobj.data.coordinate.isNull():
                co_itf = plCoordinateInterface.FindCreate(self.getRoot(),remote)
                co_itf.data.parentref=ext_scnobj.data.getRef()
                ext_scnobj.data.coordinate = co_itf.data.getRef()

            ext_scnobj.data.addModifier(self.parent)
        else:
            # else, add it to the given scene object if we have one....
            if not scnobj is None:
                scnobj.data.addModifier(self.parent)


        self.fAnimName = str(FindInDict(script,"animation",""))
        self.fSeekDuration = float(FindInDict(script,'seektime',self.fSeekDuration))
        self.fDrivable   = bool( str(FindInDict(script,'drivable'   ,str(self.fDrivable)   ) ).lower() == 'true')
        self.fReversable = bool( str(FindInDict(script,'reversable' ,str(self.fReversable) ) ).lower() == 'true')
        self.fSmartSeek  = bool( str(FindInDict(script,'smartseek'  ,str(self.fSmartSeek)  ) ).lower() == 'true')
        self.fNoSeek     = bool( str(FindInDict(script,'noseek'     ,str(self.fNoSeek)     ) ).lower() == 'true')


class plPythonFileMod(plMultiModifier):

    def __init__(self,parent,name="unnamed",type=0x00A2):
        plMultiModifier.__init__(self,parent,name,type)

        self.fPythonFile = ""
        self.fReceivers = [] # array of plKey
        self.fParameters = []

    def _Find(page,name):
        return page.find(0x00A2,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x00A2,name,1)
    FindCreate = staticmethod(_FindCreate)


    def read(self,stream):
        plMultiModifier.read(self,stream)

        self.fPythonFile = stream.ReadSafeString()

        self.fReceivers = []
        count = stream.Read32()
        for i in range(count):
            key = UruObjectRef()
            key.read(stream)
            self.fReceivers.append(key)

        count = stream.Read32()
        self.fParameters = []
        for i in range(count):
            parm = plPythonParameter(self.parent)
            parm.read(stream)
            self.fParameters.append(parm)

    def write(self,stream):
        plMultiModifier.write(self,stream)

        stream.WriteSafeString(self.fPythonFile)

        stream.Write32(len(self.fReceivers))
        for key in self.fReceivers:
            key.write(stream)

        stream.Write32(len(self.fParameters))
        for parm in self.fParameters:
            parm.write(stream)

    def addParameter(self,pyparam):
        self.fParameters.append(pyparam)

    def export_script(self,script,scnobj):
        print "   [PythonFileMod %s]"%(str(self.Key.name))
        self.fPythonFile = str(FindInDict(script,"file",""))

        receiverlist = list(FindInDict(script,"receivers",[]))

        refparser = ScriptRefParser(self.getRoot(),str(scnobj.data.Key.name),None,[])
        for keystr in receiverlist:
            ref = refarser.RefString_FindCreateRef(basepage,keystring)
            if not ref.isNull():
                self.fReceivers.append(ref.Key)

        argumentlist = list(FindInDict(script,"parameters",[]))
        index = 1
        for argscript in argumentlist:
            if type(argscript) == dict:
                plPythonParameter.ExportScript(self.parent,argscript,index,scnobj)
                index += 1

class plPythonParameter :
    #version Uru
    ValueType = \
    { \
        "kInt"                  :  1, \
        "kFloat"                :  2, \
        "kBoolean"              :  3, \
        "kString"               :  4, \
        "kSceneObject"          :  5, \
        "kSceneObjectList"      :  6, \
        "kActivatorList"        :  7, \
        "kResponderList"        :  8, \
        "kDynamicText"          :  9, \
        "kGUIDialog"            : 10, \
        "kExcludeRegion"        : 11, \
        "kAnimation"            : 12, \
        "kAnimationName"        : 13, \
        "kBehavior"             : 14, \
        "kMaterial"             : 15, \
        "kGUIPopUpMenu"         : 16, \
        "kGUISkin"              : 17, \
        "kWaterComponent"       : 18, \
        "kSwimCurrentInterface" : 19, \
        "kClusterComponentList" : 20, \
        "kMaterialAnimation"    : 21, \
        "kGrassShaderComponent" : 22, \
        "kNone"                 : 23  \
    }

# Type Table - for use in the read/write functions
    ValueTypeTable = \
    { \
         1: "int", \
         2: "float", \
         3: "bool", \
         4: "str", \
         5: "key", \
         6: "key", \
         7: "key", \
         8: "key", \
         9: "key", \
        10: "key", \
        11: "key", \
        12: "key", \
        13: "str", \
        14: "key", \
        15: "key", \
        16: "key", \
        17: "key", \
        18: "key", \
        19: "key", \
        20: "key", \
        21: "key", \
        22: "key", \
        23: "None" \
    }

 # From the cobbs wiki:
 #   Type  6 refs a type 0x0001-SceneObject
 #   Type  7 refs a type 0x002D-LogicModifier,
 #                  type 0x00A2-PythonFileMod,
 #                  type 0x00AE-SittingModifier,
 #                  type 0x00C4-AnimEventModifier, or
 #                  type 0x00F5-NPCSpawnMod
 #   Type  8 refs a type 0x007C-ResponderModifier
 #   Type  9 refs a type 0x00AD-DynamicTextMap
 #   Type 10 refs a type 0x0098-GUIDialogMod
 #   Type 11 refs a type 0x00A4-ExcludeRegionModifier
 #   Type 12 refs a type 0x006D-AGMasterMod, or
 #                  type 0x00A8-MessageForwarder
 #   Type 14 refs a type 0x0077-OneShotMod, or
 #                  type 0x00C1-MultiStageBehMod
 #   Type 15 refs a type 0x0004-MipMap (HSM)
 #   Type 18 refs a type 0x00FB-WaveSet7
 #   Type 19 refs a type 0x0134-SwimCircularCurrentRegion, or
 #                  type 0x0136-SwimStraightCurrentRegion
 #   Type 20 refs a type 0x012B-ClusterGroup
 #   Type 21 refs a type 0x0043-LayerAnimation

# This list is used to determine which object types are related to what kinds of value:


    # next list translates script names (lowercase)  to blocks of type-specific information
    ScriptValueType = \
    { \
        "int"                   : {"typenum":  1, "type": "int"     }, \
        "float"                 : {"typenum":  2, "type": "float"   }, \
        "bool"                  : {"typenum":  3, "type": "bool"    }, \
        "string"                : {"typenum":  4, "type": "str"     }, \
        "sceneobject"           : {"typenum":  5, "type": "key",     "defaultkeytype": 0x0001, "allowlist": [0x0001,] }, \
        "sceneobjectlist"       : {"typenum":  6, "type": "keylist", "defaultkeytype": 0x0001, "allowlist": [0x0001,] }, \
        "activator"             : {"typenum":  7, "type": "key",     "defaultkeytype": 0x002D,  "allowlist": [0x002D,0x00A2,0x00AE,] }, \
        "activatorlist"         : {"typenum":  7, "type": "keylist", "defaultkeytype": 0x002D,  "allowlist": [0x002D,0x00A2,0x00AE,] }, \
        "responder"             : {"typenum":  8, "type": "key",     "defaultkeytype": 0x007C, "allowlist": [0x007C,] }, \
        "responderlist"         : {"typenum":  8, "type": "keylist", "defaultkeytype": 0x007C, "allowlist": [0x007C,] }, \
#       "dynamictext"           : {"typenum":  9, "type": "key",     "defaultkeytype": 0x00AD, "allowlist": [0x00AD,] }, \
#       "guidialog"             : {"typenum": 10, "type": "key",     "defaultkeytype": 0x0098, "allowlist": [0x0098,] }, \
#       "excluderegion"         : {"typenum": 11, "type": "key",     "defaultkeytype": 0x00A4, "allowlist": [0x00A4,] }, \
#       "animation"             : {"typenum": 12, "type": "key",     "defaultkeytype": None,   "allowlist": [0x006D,0x00A8,] }, \
        "animationname"         : {"typenum": 13, "type": "str"}, \
# Duplicate is to allow for english spelling:
        "behaviour"             : {"typenum": 14, "type": "key",     "defaultkeytype": 0x0077,  "allowlist": [0x0077,] }, \
        "behavior"              : {"typenum": 14, "type": "key",     "defaultkeytype": 0x0077,  "allowlist": [0x0077,] }, \
        "material"              : {"typenum": 15, "type": "key",     "defaultkeytype": 0x0004, "allowlist": [0x0004,], "tag": "texture",  }, \
#       "guipopupmenu"          : {"typenum": 16, "type": "key",     "defaultkeytype": None,   "allowlist": [0x0119,] }, \
#       "guiskin"               : {"typenum": 17, "type": "key",     "defaultkeytype": None,   "allowlist": [0xFFFF,] }, \
#       "watercomponent"        : {"typenum": 18, "type": "key",     "defaultkeytype": 0x00FB, "allowlist": [0x00FB,] }, \
        "swimcurrentinterface"  : {"typenum": 19, "type": "key",     "defaultkeytype": None,   "allowlist": [0x0136,0x0134,] }, \
#       "clustercomponentlist"  : {"typenum": 20, "type": "keylist", "defaultkeytype": 0x012B, "allowlist": [0x012B,] }, \
#       "materialanimation"     : {"typenum": 21, "type": "key",     "defaultkeytype": 0x0043, "allowlist": [0x0043,] }, \
#       "grassshadercomponent"  : {"typenum": 22, "type": "key",     "defaultkeytype": None,   "allowlist": [0xFFFF] }, \
        "none"                  : {"typenum": 23, "type": "none" } \
    }

    def __init__(self,parent):
        self.parent = parent
        self.fID = 0
        self.fValueType = plPythonParameter.ValueType["kNone"]
        self.fObjectKey = UruObjectRef(self.parent.data.getVersion())

        self.fValue = None

    def read(self,stream):

        self.fValueType = plPythonParameter.ValueType["kNone"]
        self.fID = stream.Read32()
        self.fValueType = stream.Read32()

        if plPythonParameter.ValueTypeTable[self.fValueType] == "int":
            self.fValue = stream.Read32()

        elif plPythonParameter.ValueTypeTable[self.fValueType] == "bool":
            self.fValue = bool(stream.Read32())

        elif plPythonParameter.ValueTypeTable[self.fValueType] == "float":
            self.fValue = stream.ReadFloat()

        elif plPythonParameter.ValueTypeTable[self.fValueType] == "str":
            size = stream.Read32()
            self.fValue = stream.read(size)

        elif plPythonParameter.ValueTypeTable[self.fValueType] == "key":
            self.fObjectKey.read(stream)

    def write(self,stream):

        stream.Write32(self.fID)
        stream.Write32(self.fValueType)

        if plPythonParameter.ValueTypeTable[self.fValueType] == "int":
            stream.Write32(self.fValue)

        elif plPythonParameter.ValueTypeTable[self.fValueType] == "bool":
            stream.Write32(int(self.fValue))

        elif plPythonParameter.ValueTypeTable[self.fValueType] == "float":
            stream.WriteFloat(self.fValue)

        elif plPythonParameter.ValueTypeTable[self.fValueType] == "str":
            stream.Write32(len(str(self.fValue))+1)
            stream.write(str(self.fValue))
            stream.WriteByte(00) # Add terminator character

        elif plPythonParameter.ValueTypeTable[self.fValueType] == "key":
            self.fObjectKey.write(stream)

    def _ExportScript(pyfmod,argscript,index,scnobj):
        _type = str(FindInDict(argscript,"type","none"))
        page = pyfmod.data.getRoot()
        resmgr = page.resmanager

        if plPythonParameter.ScriptValueType.has_key(_type):
            typeinfo = plPythonParameter.ScriptValueType[_type]
            if   typeinfo["type"] == "bool":
                value = bool(str(FindInDict(argscript,"value","false")).lower() == "true")
                param = plPythonParameter(pyfmod)
                param.fValue = value
                param.fID = index
                param.fValueType = typeinfo["typenum"]
                pyfmod.data.addParameter(param)
            elif typeinfo["type"] == "int":
                value = int(FindInDict(argscript,"value","0"))
                param = plPythonParameter(pyfmod)
                param.fValue = value
                param.fID = index
                param.fValueType = typeinfo["typenum"]
                pyfmod.data.addParameter(param)
            elif typeinfo["type"] == "float":
                value = float(FindInDict(argscript,"value","0.0"))
                param = plPythonParameter(pyfmod)
                param.fValue = value
                param.fID = index
                param.fValueType = typeinfo["typenum"]
                pyfmod.data.addParameter(param)
            elif typeinfo["type"] == "str":
                value = str(FindInDict(argscript,"value","0"))
                param = plPythonParameter(pyfmod)
                param.fValue = value
                param.fID = index
                param.fValueType = typeinfo["typenum"]
                pyfmod.data.addParameter(param)
            elif typeinfo["type"] == "none":
                param = plPythonParameter(pyfmod)
                param.fID = index
                param.fValueType = typeinfo["typenum"]
                pyfmod.data.addParameter(param)
            elif typeinfo["type"] == "key":
                ref = FindInDict(argscript,"ref",None)
                plPythonParameter.ExportKey(pyfmod,ref,typeinfo,index,scnobj)
            elif typeinfo["type"] == "keylist":
                param = plPythonParameter(pyfmod)

                refs = list(FindInDict(argscript,"refs",[]))

                for ref in refs:
                    if type(ref) == str:
                        plPythonParameter.ExportKey(pyfmod,ref,typeinfo,index,scnobj)

    ExportScript = staticmethod(_ExportScript)

    def _ExportKey(pyfmod,keystr,typeinfo,index,scnobj):
        page = pyfmod.data.getRoot()
        resmgr = page.resmanager

        # prepare the key...
        param = plPythonParameter(pyfmod)
        param.fID = index
        param.fValueType = typeinfo["typenum"]

        # interpret tags....
        if typeinfo.has_key("tag"):
            if typeinfo["tag"] == "texture":
                # For textures, go to the Textures PRP by default.... unless we export textures to the same prp
                if not prp_Config.export_textures_to_page_prp:
                    page=resmgr.findPrp("Textures")
                    if page==None:
                        raise "    Textures PRP file not found"

        refparser = ScriptRefParser(page,str(scnobj.data.Key.name),typeinfo["defaultkeytype"],typeinfo["allowlist"])
        # and try to find a plasma object accordingly:
        print "    For python file mod %s, index %i we're exporting value type %s, key string %s"%(str(pyfmod.data.Key.name),index,typeinfo["typenum"],keystr)
        param.fObjectKey = refparser.MixedRef_FindCreateRef(keystr)
        print "    Key string boiled down to: ",param.fObjectKey
        pyfmod.data.addParameter(param)

    ExportKey = staticmethod(_ExportKey)


class plResponderModifier(plSingleModifier):

    Flags = \
    { \
        "kDetectTrigger"    : 0x1, \
        "kDetectUnTrigger"  : 0x2, \
        "kSkipFFSound"      : 0x4  \
    }

    ScriptFlags = \
    {
        "detecttrigger"    : 0x1, \
        "detectuntrigger"  : 0x2, \
        "skipffsound"      : 0x4  \
    }

    def __init__(self,parent,name="unnamed",type=0x007C):
        plSingleModifier.__init__(self,parent,name,type)

        self.fSDLExcludeList.append("Responder")

        self.fStates = []
        self.fCurState = 0
        self.fEnabled = True
        self.fFlags = plResponderModifier.Flags["kDetectTrigger"] # default to this, since that's what we'll b using it for

    def _Find(page,name):
        return page.find(0x007C,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x007C,name,1)
    FindCreate = staticmethod(_FindCreate)

    def read(self,stream,size):
        start = stream.tell() # Keep start offset in case of trouble...
        plSingleModifier.read(self,stream)

        count = stream.ReadByte()
        self.fStates = []

        # The try block is to ensure proper reading when we encounter an unknown message type
        # Which ofcourse should happen pretty often until we sort out all neccesary messages....

        try:

            for i in range(count):
                state = plResponderState(self)
                state.read(stream)
                self.fStates.append(state)

        except ValueError, detail:
            print "/---------------------------------------------------------"
            print "|  WARNING:"
            print "|   Got Value Error:" , detail, ":"
            print "|   Skipping state array of plResponderModifier"
            print "|   -> Skipping %i bytes ahead " % ( (start + size - 3) - stream.tell())
            print "|   -> Total object size: %i bytes"% (size)
            print "\---------------------------------------------------------\n"

            stream.seek(start + size - 3) #reposition the stream to read in the last 3 bytes

        state = stream.ReadByte()

        if state >= 0 and state < len(self.fStates):
            self.fCurState = state
        else:
            #Invalid state %d specified, will default to current state", state);
            pass

        self.fEnabled = stream.ReadBool()
        self.fFlags = stream.ReadByte()

    def write(self,stream):
        plSingleModifier.write(self,stream)

        stream.WriteByte(len(self.fStates))

        for state in self.fStates:
            state.write(stream)

        # Check if the current state is actually valid - else, we make it state "0"
        if self.fCurState >= 0 and self.fCurState < len(self.fStates):
            stream.WriteByte(self.fCurState)
        else:
            stream.WriteByte(0)

        stream.WriteBool(self.fEnabled)
        stream.WriteByte(self.fFlags)

    def export_script(self,script,scnobj):
        print "   [ResponderModifier %s]"%(str(self.Key.name))
        plSingleModifier.export_obj(self,scnobj,script)
        statelist = FindInDict(script,"states",[])
        if type(statelist) != list:
            statelist = []

        # loop through the states here - each state can be parsed by the plResponderState
        for statescript in statelist:
            if type(statescript) == dict:
                state = plResponderState(self)
                state.export_script(statescript,scnobj)
                self.fStates.append(state)

        # set the current state
        curstate = FindInDict(script,"curstate",0)
        if curstate >= 0 and curstate < len(self.fStates):
            self.fCurState = curstate

        # if enabled...
        self.fEnabled = bool(str(FindInDict(script,"enabled",str(self.fEnabled))).lower() == "true")

        # pass throug the flags - of no flag parameter is specified, default with kDetectTrigger
        flags = FindInDict(script,"flags",["detecttrigger"])
        if type(flags) == list:
            for flag in flags:
                if plResponderModifier.ScriptFlags.has_key(str(flag).lower()):
                    self.fFlags |= plResponderModifier.ScriptFlags[str(flag).lower()]


class plResponderState:
    def __init__(self,parent):
        self.parent = parent
        self.fCmds = [] # hsTArray<plResponderCmd> fCmds;
        self.fNumCallbacks = 0
        self.fSwitchToState = 0
        self.fWaitToCmd = {}


    def read(self,stream):
        self.fNumCallbacks = stream.ReadByte()
        self.fSwitchToState = stream.ReadByte()

        self.fCmds = []
        count = stream.ReadByte()
        for i in range(count):
            cmd = plResponderCmd(self)
            cmd.read(stream)
            self.fCmds.append(cmd)

        self.fWaitToCmd.clear()
        count = stream.ReadByte()
        for i in range(count):
            wait = stream.ReadByte()
            value = stream.ReadByte()
            self.fWaitToCmd[wait] = value

    def write(self,stream):
        stream.WriteByte(self.fNumCallbacks)
        stream.WriteByte(self.fSwitchToState)
        stream.WriteByte(len(self.fCmds))

        for cmd in self.fCmds:
            cmd.write(stream)

        stream.WriteByte(len(self.fWaitToCmd.keys()))
        for key in self.fWaitToCmd.keys():
            stream.WriteByte(key)
            stream.WriteByte(self.fWaitToCmd[key])

    def export_script(self,script,scnobj):
        # first parse the commands
        cmdlist = FindInDict(script,"cmds",[])
        if type(cmdlist) != list:
            cmdlist = []

        for cmdscript in cmdlist:
            if type(cmdscript) == dict:
                cmd = plResponderCmd(self)
                cmd.export_script(cmdscript,scnobj)
                self.fCmds.append(cmd)
        # Next the other settincs
        ncallbacks = FindInDict(script,"ncallbacks",0)
        self.fNumCallbacks = int(ncallbacks)
        nextstate = FindInDict(script,"nextstate",0)
        self.fSwitchToState = int(nextstate)

        # and the waitto dictionary
        waittocmd = FindInDict(script,"waittocmd",None)
        if type(waittocmd) == list:
            for wait in waittocmd:
                key = int(FindInDict(wait,"key",-1))
                msg = int(FindInDict(wait,"msg",0))
                if type(key) == int and key >= 0 and key < len(self.fCmds):
                    if type(msg) == int:
                        self.fWaitToCmd[key] = msg

    def addMessage(self,msg,waiton=-1):
        cmd = plResponderCmd()
        cmd.fMsg = msg
        cmd.fWaitOn=waiton

class plResponderCmd:
    ScriptMsgTypes = \
    { \
        "notifymsg"         : 0x02E8, \
        "armatureeffectmsg" : 0x038E, \
        "oneshotmsg"        : 0x0302, \
        "cameramsg"         : 0x020A, \
        "enablemsg"         : 0x024F, \
        "soundmsg"          : 0x0255, \
        "animcmdmsg"        : 0x0206, \
        "timercallbackmsg"  : 0x024A, \
    }

    def __init__(self,parent):
        self.parent = parent
        self.fMsg = None
        self.fWaitOn = -1

    def read(self,stream):
        self.fMsg = PrpMessage.FromStream(stream)
        self.fWaitOn = stream.ReadSignedByte()

    def write(self,stream):
        PrpMessage.ToStream(stream,self.fMsg)
        stream.WriteSignedByte(self.fWaitOn)

    def export_script(self,script,scnobj):
        msgtype = FindInDict(script,"type",None)
        if not plResponderCmd.ScriptMsgTypes.has_key(str(msgtype)):
            msgtype = "oneshotmsg"

        self.fMsg = PrpMessage(plResponderCmd.ScriptMsgTypes[msgtype],self.parent.parent.getVersion())    # create correct message object

        paramscript = FindInDict(script,"params",None)
        if type(paramscript) == dict:
            refparser = ScriptRefParser(self.parent.parent.getRoot(),str(scnobj.data.Key.name),False,[])
            self.fMsg.data.export_script(paramscript,refparser)
            self.fMsg.data.fSender = self.parent.parent.getRef()

        self.fWaitOn = int(FindInDict(script,"waiton",-1))


class plAvLadderMod(plSingleModifier):
    #Rewritten at Oct/11/2006
    fTypeField = \
    { \
        "kBig": 0, \
        "kFourFeet": 1, \
        "kTwoFeet":2, \
        "kNumOfTypeFields":3 \
    }

    def __init__(self,parent,name="unnamed",type=0x00B2):
        plSingleModifier.__init__(self,parent,name,type)
        #format
        self.fType = 0
        self.fLoops = 1
        self.fGoingUp = False
        self.fEnabled = True
        self.fLadderView = Vertex()

    def _Find(page,name):
        return page.find(0x00B2,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x00B2,name,1)
    FindCreate = staticmethod(_FindCreate)

    def changePageRaw(self,sid,did,stype,dtype):
        plSingleModifier.changePageRaw(self,sid,did,stype,dtype)


    def read(self,stream):
        plSingleModifier.read(self,stream)
        self.fType = stream.Read32()
        self.fLoops = stream.Read32()
        self.fGoingUp = stream.ReadBool()
        self.fEnabled = stream.ReadBool()
        self.fLadderView.read(stream)


    def write(self,stream):
        plSingleModifier.write(self,stream)
        stream.Write32(self.fType)
        stream.Write32(self.fLoops)
        stream.WriteBool(self.fGoingUp)
        stream.WriteBool(self.fEnabled)
        self.fLadderView.write(stream)

        # print "*writing ladder mod*"
        # print "Type: %d" % self.fType
        # print "Loops: %d" % self.fLoops
        # print "GoingUp: %s" % self.fGoingUp
        # print "Enabled: %s" % self.fEnabled
        # print "LadderView: "
        # print self.fLadderView

    def import_obj(self,obj):
        try:
            obj.removeProperty("regiontype")
        except:
            pass
        obj.addProperty("regiontype","ladder")

        objscript = AlcScript.objects.FindOrCreate(obj.name)

        if self.fType == plAvLadderMod.fTypeField["kBig"]:
            StoreInDict(objscript,"region.ladder.style","big")
        elif self.fType == plAvLadderMod.fTypeField["kFourFeet"]:
            StoreInDict(objscript,"region.ladder.style","fourfeet")
        elif self.fType == plAvLadderMod.fTypeField["kTwoFeet"]:
            StoreInDict(objscript,"region.ladder.style","twofeet")

        StoreInDict(objscript,"region.ladder.loops",self.fLoops)
        if self.fGoingUp:
            StoreInDict(objscript,"region.ladder.direction","up")
        else:
            StoreInDict(objscript,"region.ladder.direction","down")

        v = Vertex(self.fLadderView.x,self.fLadderView.y,self.fLadderView.z)

        matrix = getMatrix(obj)
        rotMatrix = matrix.rotationPart().resize4x4()
        rotMatrix.invert()
        rotMatrix.transpose()
        m = hsMatrix44()
        m.set(rotMatrix)
        v.transform(m)

        StoreInDict(objscript,"region.ladder.ladderview",str(v))


    def export_obj(self,obj):
        print "  [Ladder Modifier %s]"%(str(self.Key.name))
        objscript = AlcScript.objects.FindOrCreate(obj.name)
        # calculate the approximate Direction vector
        vct = str(FindInDict(objscript,"region.ladder.ladderview","0,-1,0"))
        try:
            X,Y,Z, = vct.split(',')
            v = Vertex(float(X),float(Y),float(Z))
        except ValueError, detail:
            print "  Error parsing region.ladder.ladderview (Value:",vct,") : ",detail

        matrix = getMatrix(obj)

        print matrix
        rotpart = matrix.rotationPart()
        rotmatrix = rotpart.resize4x4()
        rotmatrix.transpose()
        m = hsMatrix44()
        m.set(rotmatrix)
        v.transform(m)

        self.fLadderView = v # assign to Direction Vector


        print "   Ladder View: ",self.fLadderView

        if str(FindInDict(objscript,"region.ladder.direction","down")).lower() == "up":
            print "   Direction: Up"
            self.fGoingUp = True
        elif str(getTextPropertyOrDefault(obj,"direction","down")).lower() == "up":
            print "   Direction: Up"
            self.fGoingUp = True
        else:
            print "   Direction: Down"
            self.fGoingUp = False

        style = str(FindInDict(objscript,"region.ladder.style","big")).lower()
        style = str(getTextPropertyOrDefault(obj,"style",style)).lower()
        if style == "fourfeet":
            print "   Style: Four Feet"
            self.fType == plAvLadderMod.fTypeField["kFourFeet"]
        elif style == "twofeet":
            print "   Style: Two Feet"
            self.fType == plAvLadderMod.fTypeField["kTwoFeet"]
        else: #if style == 'big' or anything else...
            print "   Style: Big"
            self.fType = plAvLadderMod.fTypeField["kBig"]

        self.fLoops = FindInDict(objscript,"region.ladder.loops",self.fLoops)
        self.fLoops = getIntPropertyOrDefault(obj,"loops",self.fLoops)
        print "   Number of loops:",self.fLoops


    def export_raw(self,matrix,Type,Loops,GoingUp=0):
        # calculate the approximate Direction vector
        rotMatrix = matrix.rotationPart().resize4x4()
        v = Blender.Mathutils.Vector(0,-1,0,1) # vector describing -Y axis
        v = v * rotMatrix  # transform the vector accoring to object matrix
        self.fLadderView.setVector(v) # assign to Direction Vector
        self.fLoops = Loops
        self.fGoingUp = GoingUp
        self.fType = Type

    def _Export(page,obj,scnobj,name):
        #set the coordinate interface
        laddermod=plAvLadderMod.FindCreate(page,name)
        laddermod.data.export_obj(obj)
        scnobj.data.data2.append(laddermod.data.getRef())

    Export = staticmethod(_Export)
    
