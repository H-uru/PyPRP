#
# $Id: alc_Classes.py 843 2007-09-13 01:19:29Z Robert The Rebuilder $
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
from alc_AbsClasses import *
from alc_MatClasses import *
from alc_DrawClasses import *
from alc_SwimClasses import *
from alc_CamClasses import *
from alcurutypes import *
from alcdxtconv import *
from alchexdump import *
from alc_GeomClasses import *
from alcGObjects import *
from alcConvexHull import *
from alc_VolumeIsect import *
from alc_AlcScript import *

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

class plSceneNode(hsKeyedObject):                           #Type 0x00
    def __init__(self,parent,name="unnamed",type=0x0000):               #Members
        hsKeyedObject.__init__(self,parent,name,type)            #Base
        self.SceneObjects=hsTArray([0x01],self.getVersion())                  #plSceneObjects (vector)
        if self.getVersion()==6:
            ##myst5 types
            self.OtherObjects=hsTArray([0xCD,0x6B,0x80,0x8E,0x0110],6)
        else:
            ##Uru types
            self.OtherObjects=hsTArray([0x7A,0x98,0xA8,0xB5,0xE4,0xE8,0xE9,0xEA,0xED,0xF1,0x0109,0x010A,0x0129,0x012A,0x012B],5)


    def changePageRaw(self,sid,did,stype,dtype):
        self.SceneObjects.changePageRaw(sid,did,stype,dtype)
        self.OtherObjects.changePageRaw(sid,did,stype,dtype)


    def read(self,stream):
        hsKeyedObject.read(self,stream)
        self.SceneObjects.ReadVector(stream)
        self.OtherObjects.ReadVector(stream)
       # size, = struct.unpack("I",stream.read(4))
       # for i in range(size):
       #     o = UruObjectRef(self.getVersion())
       #     o.read(stream)
       #     #print o
       #     if not o.Key.object_type in self.data1allow:
       #         raise RuntimeError, "Type %04X is not a plSceneObject [0x0000]" % o.Key.object_type
       #     self.data1.append(o)
       # size, = struct.unpack("I",stream.read(4))
       # for i in range(size):
       #     o = UruObjectRef(self.getVersion())
       #     o.read(stream)
       #     if not o.Key.object_type in self.data2allow:
       #         raise RuntimeError, "Type %04X is not in allow list 2" % o.Key.object_type
       #     self.data2.append(o)
       # assert(self.verify())


    def write(self,stream):
        hsKeyedObject.write(self,stream)
        self.SceneObjects.WriteVector(stream)
        self.OtherObjects.WriteVector(stream)
       # stream.write(struct.pack("I",len(self.data1)))
       # for o in self.data1:
       #     #o.update(self.Key)
       #     o.write(stream)
       # stream.write(struct.pack("I",len(self.data2)))
       # for o in self.data2:
       #     #o.update(self.Key)
       #     o.write(stream)


    def _Find(page,name):
        return page.find(0x0000,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0000,name,1)
    FindCreate = staticmethod(_FindCreate)

    def import_all(self,scene):
        root = self.getRoot()


        reflist1 = []
        # 1st pass - objects containing lights...
        for ref in self.SceneObjects.vector:
            o=root.findref(ref)
            
            LightInfo = False
    
            for r in  o.data.data1.vector:
                if r.Key.object_type in [0x55,0x56,0x57]: 
                    LightInfo = True
            
            if LightInfo:
                o.data.import_all(scene)
            else:
                reflist1.append(ref)
            
        # 2nd pass - other objects
        for ref in reflist1:
            o=root.findref(ref)
            o.data.import_all(scene)
        
        Blender.Redraw()


class plSceneObject(plSynchedObject):                       #Type 0x01
    def __init__(self,parent,name="unnamed",type=0x0001):               #Members
        plSynchedObject.__init__(self,parent,name,type)
        self.draw=UruObjectRef()                            #Span Info
        self.simulation=UruObjectRef()                      #Animation Info
        self.coordinate=UruObjectRef()                      #Region Info
        self.audio=UruObjectRef()                           #Sound Info
        self.scene=UruObjectRef()                           #SceneNode to which this object belong
        if self.getVersion()==6:
            #myst5 types
            self.data1=hsTArray([0x0C,0x50,0x51,0x52,0x5A,0x5B,0x76,0xB5,0xB6],6)
            self.data2=hsTArray([0x08,0x1B,0x21,0x23,0x2A,0x2C,0x3B,0x3C,0x3E,0x56,0x57,0x5F,0x60,0x62,0x6A,0x6C,0x6D,0x6E,0x7D,0x83,0x87,0x88,0x8A,0x91,0x92,0x94,0x97,0x98,0x9C,0x9E,0xA5,0xAC,0xB4,0xC1,0xD0,0xD4,0xD8,0xE0,0xF1,0x0106,0x010E,0x0113,0x0114],6)
        else:
            #uru types
            self.data1=hsTArray([0x0C,0x55,0x56,0x57,0x67,0x6A,0x88,0xD5,0xD6,0xE2,0xEC,0xF6,0x0116,0x011E,0x0133,0x0134,0x0136],5)
            self.data2=hsTArray([0x08,0x2A,0x2B,0x2D,0x3D,0x40,0x62,0x6C,0x6D,0x6F,0x71,0x76,0x77,0x79,0x7A,0x7B,0x7C,0x8F,0x95,0x9B,0xA1,0xA2,0xA4,0xA9,0xAA,0xAB,0xAC,0xAE,0xAF,0xB1,0xB2,0xB9,0xBA,0xBB,0xBD,0xC0,0xC1,0xC4,0xCB,0xCF,0xD4,0xE5,0xE7,0xEE,0xF3,0xF5,0xFB,0xFC,0xFF,0x0107,0x0108,0x010C,0x010D,0x0119,0x0122,0x012C,0x012E,0x012F,0x0131],5)

    def changePageRaw(self,sid,did,stype,dtype):
        plSynchedObject.changePageRaw(self,sid,did,stype,dtype)
        self.draw.changePageRaw(sid,did,stype,dtype)
        self.simulation.changePageRaw(sid,did,stype,dtype)
        self.coordinate.changePageRaw(sid,did,stype,dtype)
        self.audio.changePageRaw(sid,did,stype,dtype)
        for i in self.data1.vector:
            i.changePageRaw(sid,did,stype,dtype)
        for i in self.data2.vector:
            i.changePageRaw(sid,did,stype,dtype)
        self.scene.changePageRaw(sid,did,stype,dtype)


    def read(self,stream):
        plSynchedObject.read(self,stream)
        self.draw.setVersion(self.getVersion())
        self.simulation.setVersion(self.getVersion())
        self.coordinate.setVersion(self.getVersion())
        self.audio.setVersion(self.getVersion())
        self.scene.setVersion(self.getVersion())
        self.draw.read(stream)
        self.simulation.read(stream)
        self.coordinate.read(stream)
        self.audio.read(stream)
        self.data1.ReadVector(stream)
        self.data2.ReadVector(stream)
        self.scene.read(stream)


    def write(self,stream):
        plSynchedObject.write(self,stream)
        self.draw.write(stream)
        self.simulation.write(stream)
        self.coordinate.write(stream)
        self.audio.write(stream)
        self.data1.WriteVector(stream)
        self.data2.WriteVector(stream)
        self.scene.write(stream)

    def _Find(page,name):
        return page.find(0x0001,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0001,name,1)
    FindCreate = staticmethod(_FindCreate)
    
    def addGeneric(self,plobj):
        self.data1.append(plobj.data.getRef())
        
    def addModifier(self,plobj):
        self.data2.append(plobj.data.getRef())

    def import_all(self,scene):
        #assert(self.draw.checktype(0x0016)) #or self.draw.checktype(0x00D2))
        root = self.getRoot()

        # Current BlenderObject types:
        #  'Armature', 'Camera', 'Curve', 'Lamp', 'Lattice', 'Mball', 'Mesh', 'Surf' or 'Empty'

        # Used by us:
        #  'Camera', 'Lamp', 'Mesh', 'Empty'

        # Determine object type

        CameraMod = False
        LightInfo = False
        SpawnMod = False

        for ref in  self.data1.vector:
            if ref.Key.object_type in [0x55,0x56,0x57,0xD5,0xD6]: 
                LightInfo = True
            
        for mod in self.data2.vector:
            if mod.Key.object_type in [0x9B,]: #CameraModifier
                CameraMod = True
        
        
        for mod in self.data2.vector:
            if mod.Key.object_type in [0x3D,]: #SpawnModifier
                SpawnMod = True

        # Create Main Object for this item
        if not self.draw.isNull(): # if it has drawables, it's a mesh
            print "\n[Visual Object %s]"%(str(self.Key.name))
            
            obj = Blender.Object.New('Mesh',str(self.Key.name))
            scene.objects.link(obj)
            mesh = Mesh.New(str(self.Key.name))
            obj.link(mesh)
            obj.layers=[1,]

            # Import possible draw interfaces
            plDrawInterface.Import(self,root,obj)
            plCoordinateInterface.Import(self,root,obj)
            plSimulationInterface.Import(self,root,obj)

            # Import Interfaces
            for i_ref in self.data1.vector:
                if i_ref.Key.object_type in []:
                    intf=root.findref(i_ref)
                    if not intf is None:
                        intf.data.import_obj(obj)

            # Import Modifiers
            for m_ref in self.data2.vector:
                if m_ref.Key.object_type in []:
                    mod=root.findref(m_ref)
                    if not mod is None:
                        mod.data.import_obj(obj)


        elif not self.simulation.isNull(): # if it has simulation, but no drawable, it's a collider mesh
            print "\n[Phyical Object %s]"%(str(self.Key.name))
            obj = Blender.Object.New('Mesh',str(self.Key.name))
            scene.objects.link(obj)
            mesh = Mesh.New(str(self.Key.name))
            obj.link(mesh)
            obj.layers=[2,]

            plCoordinateInterface.Import(self,root,obj)
            plSimulationInterface.Import(self,root,obj)

            # Import Interfaces
            for i_ref in self.data1.vector:
                if i_ref.Key.object_type in []:
                    intf=root.findref(i_ref)
                    if not intf is None:
                        intf.data.import_obj(obj)

            # Import Modifiers
            for m_ref in self.data2.vector:
                if m_ref.Key.object_type in [0x00FC,]:
                    mod=root.findref(m_ref)
                    if not mod is None:
                        mod.data.import_obj(obj)


        elif LightInfo:
            print "\n[Lamp %s]"%(str(self.Key.name))
            obj = Blender.Object.New('Lamp',str(self.Key.name))
            scene.objects.link(obj)
            obj.layers=[1,]

            plLightInfo.Import(self,root,obj)
            plCoordinateInterface.Import(self,root,obj)
            
        elif CameraMod:
            print "\n[Camera %s]"%(str(self.Key.name))
            obj = Blender.Object.New('Camera',str(self.Key.name))
            scene.objects.link(obj)
            obj.layers=[4,]
            
            plCameraModifier1.Import(self,root,obj)                
            plCoordinateInterface.Import(self,root,obj)
            
        else: # if all else fails, it's an Empty
            print "\n[Empty Object %s]"%(str(self.Key.name))
            obj = Blender.Object.New('Empty',str(self.Key.name))
            scene.link(obj)
            plCoordinateInterface.Import(self,root,obj)
            obj.layers=[2,] # Empty's go to layer

            # Import Modifiers
            for m_ref in self.data2.vector:
                if m_ref.Key.object_type in [0x003D,]:
                    mod=root.findref(m_ref)
                    if not mod is None:
                        mod.data.import_obj(obj)

        # Add page_num property
        if self.getPageNum() != 0: # but only if it's not page 0
            obj.addProperty("page_num",str(self.getPageNum()))


    def deldefaultproperty(self,obj,propertyname,defaultvalue):
        try:
            p=obj.getProperty(propertyname)
            if(p.getData() == defaultvalue):
                obj.removeProperty(p)
        except (AttributeError, RuntimeError):
            print "Error removing %s property" % propertyname

class plCoordinateInterface(plObjInterface):
    plCoordinateProperties = \
    { \
        "kDisable"                  : 0, \
        "kCanEverDelayTransform"    : 1, \
        "kDelayedTransformEval"     : 2, \
        "kNumProps"                 : 3  \
    }
    
    def __init__(self,parent,name="unnamed",type=0x0015):
        plObjInterface.__init__(self,parent,name,type)
        #format
        self.fLocalToParent=hsMatrix44() 
        self.fParentToLocal=hsMatrix44()
        self.fLocalToWorld=hsMatrix44() 
        self.fWorldToLocal=hsMatrix44()
        self.fChildren=hsTArray([0x01],self.getVersion(),True)

    def changePageRaw(self,sid,did,stype,dtype):
        plObjInterface.changePageRaw(self,sid,did,stype,dtype)
        self.fChildren.changePageRaw(sid,did,stype,dtype)


    def read(self,stream):
        plObjInterface.read(self,stream)
        assert(self.parentref.Key.object_type==0x01)
        self.fLocalToParent.read(stream)
        self.fParentToLocal.read(stream)
        self.fLocalToWorld.read(stream)
        self.fWorldToLocal.read(stream)
        self.fChildren.ReadVector(stream)


    def write(self,stream):
        
        if len(self.BitFlags) == 0:
            #initialize bit vector to contain one value: 0
            self.BitFlags.append(0)
        plObjInterface.write(self,stream)
        self.fLocalToParent.write(stream)
        self.fParentToLocal.write(stream)
        self.fLocalToWorld.write(stream)
        self.fWorldToLocal.write(stream)
        self.fChildren.WriteVector(stream)

    def _Find(page,name):
        return page.find(0x0015,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0015,name,1)
    FindCreate = staticmethod(_FindCreate)

    def export_obj(self,obj,objlist=[]):
        print " [Coordinate Interface %s]"%(str(self.Key.name))
        m=getMatrix(obj)
        m.transpose()
        self.fLocalToWorld.set(m) 
        self.fLocalToParent.set(m) 
        m.invert()
        self.fWorldToLocal.set(m)
        self.fParentToLocal.set(m)

        parent = obj.getParent()
        if not parent is None:
            # only set the parent matrices when it's parent has a coordinate interface as well...
            if parent.rbFlags & Blender.Object.RBFlags["ACTOR"]:
                
                parentmtx= obj.getMatrix('localspace') # get parent
                parentmtx.transpose()
                self.fLocalToParent.set(parentmtx)

                parentmtx.invert()
                self.fParentToLocal.set(parentmtx)
        
        ## Need to add code to detect children....
        for obj2 in objlist:
            parent = obj2.getParent()
            if parent == obj:
                if obj2.rbFlags & Blender.Object.RBFlags["ACTOR"]:
                    # it is dynamic, add it, otherwise just ignore it
                    name2 = obj2.name
                    scnobj2 = plSceneObject.FindCreate(self.getRoot(),name2)
                    self.fChildren.append(scnobj2.data.getRef())
        
    def set_matrices(self,localtoworld,localtoparent=None):
        l2w = Blender.Mathutils.Matrix(localtoworld)
        w2l = Blender.Mathutils.Matrix(localtoworld)
        w2l.invert()

        if(localtoparent):
            l2p = Blender.Mathutils.Matrix(localtoparent)
            p2l = Blender.Mathutils.Matrix(localtoparent)
            p2l.invert()
        else:
            l2p = Blender.Mathutils.Matrix(l2w)
            p2l = Blender.Mathutils.Matrix(w2l)
        
        l2p.transpose()
        p2l.transpose()
        l2w.transpose()
        w2l.transpose()
        
        self.fLocalToParent.set(l2p)
        self.fParentToLocal.set(p2l)
        self.fLocalToWorld.set(l2w)
        self.fWorldToLocal.set(w2l)

    def import_obj(self,obj):
        print " [Coordinate Interface %s]"%(str(self.Key.name))
        l2w = self.fLocalToWorld.get()
        l2w.transpose()
        obj.setMatrix(l2w)

    # Static Method used to separate things from the resmanagers export code
    def _Export(page,obj,scnobj,name=None,isdynamic=1,objlist=[]):
        if name is None:
            name = obj.name
            
        if isdynamic==1:
            obj.rbFlags |= Blender.Object.RBFlags["ACTOR"]
            #set the coordinate interface
            coori=page.prp.findref(scnobj.data.coordinate)
            if coori==None:
                coori=plCoordinateInterface.FindCreate(page.prp,name)
            coori.data.parentref=scnobj.data.getRef()
            coori.data.export_obj(obj,objlist)
            scnobj.data.coordinate=coori.data.getRef()
    
    Export = staticmethod(_Export)

    def _Import(scnobj,prp,obj):
        if not scnobj.coordinate.isNull() and scnobj.coordinate.Key.object_type == 0x0015:
            coordinate = prp.findref(scnobj.coordinate)
            coordinate.data.import_obj(obj)
            
    Import = staticmethod(_Import)


class plSimulationInterface(plObjInterface):
    plSimulationProperties = \
    { \
        "kDisable"                  :  0, \
        "kWeightless_DEAD"          :  1, \
        "kPinned"                   :  2, \
        "kWarp_DEAD"                :  3, \
        "kUpright_DEAD"             :  4, \
        "kPassive"                  :  5, \
        "kRotationForces_DEAD"      :  6, \
        "kCameraAvoidObject_DEAD"   :  7, \
        "kPhysAnim"                 :  8, \
        "kStartInactive"            :  9, \
        "kNoSynchronize"            : 10, \
        "kSuppressed_DEAD"          : 11, \
        "kNoOwnershipChange"        : 12, \
        "kAvAnimPushable"           : 13, \
        "kNumProps"                 : 14 \
    }
    
    def __init__(self,parent,name="unnamed",type=0x001C):
        plObjInterface.__init__(self,parent,name,type)
        #format
        self.fProps= hsBitVector()
        self.fPhysical=UruObjectRef(self.getVersion()) #plPhysical


    def changePageRaw(self,sid,did,stype,dtype):
        plObjInterface.changePageRaw(self,sid,did,stype,dtype)
        self.fPhysical.changePageRaw(sid,did,stype,dtype)


    def read(self,stream):
        plObjInterface.read(self,stream)
        self.fProps.read(stream)
        stream.Read32()

        self.fPhysical.read(stream)
        self.fPhysical.verify(self.Key)
        assert(self.fPhysical.Key.object_type==0x3F)


    def write(self,stream):
        plObjInterface.write(self,stream)
        self.fProps.write(stream)
        stream.Write32(0)
        self.fPhysical.write(stream)

    def _Find(page,name):
        return page.find(0x001C,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x001C,name,1)
    FindCreate = staticmethod(_FindCreate)

    def import_obj(self,obj,scnobj):
        print " [SimulationInterface %s]"%(str(self.Key.name))
        root=self.getRoot()
        phys=root.findref(self.fPhysical)
        phys.data.import_obj(obj,scnobj)
        
    def export_obj(self,obj):
       pass
    
    def _Import(scnobj,prp,obj):
        if not scnobj.simulation.isNull():
            simi = prp.findref(scnobj.simulation)
            simi.data.import_obj(obj,scnobj)
            
    Import = staticmethod(_Import)
    
    # Export function here is to alleviate complexity of the resmanager's export code

    def _Export(page,obj,scnobj,name,SceneNodeRef,isdynamic=0):
        # if there are bounds to export...
        alctype = getTextPropertyOrDefault(obj,"alctype","object")
        if obj.rbFlags & Object.RBFlags["BOUNDS"] or alctype == "region":
            #set the simulation interface
            
            # see if the simulation is already there....
            simiref=scnobj.data.simulation
            simi=page.prp.findref(simiref)
            if simi==None:
                # if not, make it
                simi=page.prp.find(0x1C,name,1)
            scnobj.data.simulation=simi.data.getRef()
            
            # Set the SimulationInterface's Parent ref
            simi.data.parentref=scnobj.data.getRef()
            
            # Find the Physical object
            physical=page.prp.findref(simi.data.fPhysical)
            if physical==None:
                # Or make it if it isn't there yet
                physical=page.prp.find(0x3F,name,1)
            simi.data.fPhysical=physical.data.getRef()

            # Set the physical's scene node ref
            
            physical.data.fScene=SceneNodeRef
            physical.data.fSceneObject=scnobj.data.getRef()
            physical.data.export_obj(obj,scnobj,isdynamic) 
    
    Export = staticmethod(_Export)


class plPhysical(plSynchedObject):
    plLOSDB = \
    { \
        "kLOSDBNone"            :    0x0, \
        "kLOSDBUIBlockers"      :    0x1, \
        "kLOSDBUIItems"         :    0x2, \
        "kLOSDBCameraBlockers"  :    0x4, \
        "kLOSDBCustom"          :    0x8, \
        "kLOSDBLocalAvatar"     :   0x10, \
        "kLOSDBShootableItems"  :   0x20, \
        "kLOSDBAvatarWalkable"  :   0x40, \
        "kLOSDBSwimRegion"      :   0x80, \
        "kLOSDBMax"             :  0x100, \
        "kLOSDBForce16"         : 0xFFFF \
    }
    
    Group = \
    { \
        "kGroupStatic"          : 0x0, \
        "kGroupAvatarBlocker"   : 0x1, \
        "kGroupDynamicBlocker"  : 0x2, \
        "kGroupAvatar"          : 0x3, \
        "kGroupDynamic"         : 0x4, \
        "kGroupDetector"        : 0x5, \
        "kGroupLOSOnly"         : 0x6, \
        "kGroupMax"             : 0x7, \
        \
        "-->Next part is conjecture" : False, \
        \
        "kGroupPhysAnim"        : 0x8, \
        "kGroupStartInactive"   : 0x9, \
        "kGroupNoSynchronize"   : 0xA, \
        "kGroupSuppressed"      : 0xB  \
    }
    
    Bounds = \
    { \
        "kBoxBounds"            :  0x1, \
        "kSphereBounds"         :  0x2, \
        "kHullBounds"           :  0x3, \
        "kProxyBounds"          :  0x4, \
        "kExplicitBounds"       :  0x5, \
        "kNumBounds"            :  0x6, \
        "kBoundsMax"            : 0xFF \
    }   



class HKBounds:
    def __init__(self,type=0x00):
        self.fType = type
    
    def read(self,stream):
        pass
    
    def write(self,stream):
        pass

    def SizeTransform_obj(self,obj):
        m=getMatrix(obj)
        self.SizeTransform_mtx(m)

    def SizeTransform_mtx(self,m): #Blender.MathUtils.Matrix input
        s = m.scalePart()
        # build up basic scale matrix transformation from this
        m = [[s.x, 0.0, 0.0, 0.0], \
             [0.0, s.y, 0.0, 0.0], \
             [0.0, 0.0, s.z, 0,0], \
             [0.0, 0.0, 0.0, 1.0]]
             
        matrix = hsMatrix44()
        matrix.set(m)
        self.Transform(matrix)

    def Transform(self,matrix): # virtual function
        pass


class SphereBounds(HKBounds):
    def __init__(self,type=plPhysical.Bounds["kSphereBounds"]):
        HKBounds.__init__(self,type)
        self.fOffset = Vertex()
        self.fRadius = 1.0
        pass
    
    def read(self,stream):
        HKBounds.read(self,stream)
        self.fOffset.read(stream)
        self.fRadius = stream.ReadFloat()
        
    def write(self,stream):
        HKBounds.write(self,stream)
        self.fOffset.write(stream)
        stream.WriteFloat(self.fRadius)
        pass

    def export_obj(self,obj):
        mesh = obj.getData(False,True)
        print "  SphereBounds export"
        print "   Sphere based on %d (%d) vertices"%(len(mesh.verts),len(obj.data.verts))
        self.vertexs=[]
        self.faces=[]
        #DONE
        verts=[]
        #transform to world for static objects
        matrix=hsMatrix44()
        m=getMatrix(obj)
        m.transpose()
        matrix.set(m)
        for vert in mesh.verts:
            v=[vert.co[0],vert.co[1],vert.co[2]]
            verts.append(v)
        max=0
        for i in verts:
            for e in verts:
                d=distance(i,e)
                if d>max:
                    max=d
        self.d=max/2
        
    def export_raw(self,vertices,faces=None):
        max=0
        print "computing distance..."
        for i in vertices:
            for e in vertices:
                d=distance(i,e)
                if d>max:
                    max=d
        self.d=max/2
    
        

class HullBounds(HKBounds):
    
    def __init__(self,type=plPhysical.Bounds["kHullBounds"]):
        HKBounds.__init__(self,type)
        self.fVertices = []
        self.fFaces = []
        pass
    
    def read(self,stream):
        HKBounds.read(self,stream)

        self.fVertices = [] # reset vertex list
        count = stream.Read32()
        for i in range(count):
            x = stream.ReadFloat()
            y = stream.ReadFloat()
            z = stream.ReadFloat()
            vertex = [x,y,z]
            self.fVertices.append(vertex)
       
    def write(self,stream):
        HKBounds.write(self,stream)
        stream.Write32(len(self.fVertices))
        for vertex in self.fVertices:
            stream.WriteFloat(vertex[0])
            stream.WriteFloat(vertex[1])
            stream.WriteFloat(vertex[2])

    def export_obj(self,obj):
        print "  HullBounds export"
        mesh = obj.getData(False,True)
        print "   Exporting %d (%d) vertices"%(len(mesh.verts),len(obj.data.verts))
        self.fVertices=[]
        
        for vert in mesh.verts:
            v=[vert.co[0],vert.co[1],vert.co[2]]
            self.fVertices.append(v)

    def export_raw(self,vertices,faces=None):
        print "  HullBounds raw export"
        self.fVertices=[]
        for vert in vertices:
            v=[vert[0],vert[1],vert[2]]
            self.fVertices.append(v)
        
    
    def Transform(self,matrix): # needs hsMatrix44 input
        tverts=[]
        for vi in self.fVertices:
            v=Vertex(vi[0],vi[1],vi[2])
            v.transform(matrix)
            va=[v.x,v.y,v.z]
            tverts.append(va)

        self.fVertices=tverts

    def Transform_obj(self,obj):
        matrix=hsMatrix44()
        m=getMatrix(obj)
        m.transpose()
        matrix.set(m)
        
        self.Transform(matrix)

class ProxyBounds(HullBounds):
    def __init__(self,type=plPhysical.Bounds["kProxyBounds"]):
        HullBounds.__init__(self,type)
        self.fFaces = []
    
    def read(self,stream):
        HullBounds.read(self,stream)

        self.fFaces = [] # reset face list
        count = stream.Read32()
        for i in range(count):
            a = stream.Read16()
            b = stream.Read16()
            c = stream.Read16()
            face = [a,b,c]
            self.fFaces.append(face)
        
    def write(self,stream):
        HullBounds.write(self,stream)
        
        stream.Write32(len(self.fFaces))
        for face in self.fFaces:
            for v_idx in face:
                stream.Write16(v_idx)
        
    def export_obj(self,obj):
        mesh = obj.getData(False,True)
        print "  ProxyBounds export"
        print "   Exporting %d (%d) vertices"%(len(mesh.verts),len(obj.data.verts))
        print "   Exporting %d (%d) faces"%(len(mesh.verts),len(obj.data.verts))
        
        self.fVertices=[]
        self.fFaces=[]
        for vert in mesh.verts:
            v=[vert.co[0],vert.co[1],vert.co[2]]
            self.fVertices.append(v)
        for face in mesh.faces:
            n=len(face.v)
            if n<3:
                continue
            elif n==3:
                tface=[]
                for i in range(3):
                    tface.append(face.v[i].index)
                self.fFaces.append(tface)
            elif n==4:
                tface=[]
                for i in range(3):
                    tface.append(face.v[i].index)
                self.fFaces.append(tface)
                tface=[]
                for i in (0,2,3):
                    tface.append(face.v[i].index)
                self.fFaces.append(tface)
            else:
                raise RuntimeError

    def export_raw(self,vertices,faces=[]):
        self.fVertices=[]
        self.fFaces=[]
        for vert in vertices:
            v=[vert[0],vert[1],vert[2]]
            self.fVertices.append(v)

        for face in faces:
            n=len(face)
            if n<3:
                continue
            elif n==3:
                tface=[]
                for i in range(3):
                    tface.append(face[i])
                self.fFaces.append(tface)
            elif n==4:
                tface=[]
                for i in range(3):
                    tface.append(face[i])
                self.fFaces.append(tface)
                tface=[]
                for i in (0,2,3):
                    tface.append(face[i])
                self.fFaces.append(tface)
            else:
                raise RuntimeError
        

class BoxBounds(ProxyBounds):
    def __init__(self,type=plPhysical.Bounds["kBoxBounds"]):
        ProxyBounds.__init__(self,type)
    
    def read(self,stream):
        ProxyBounds.read(self,stream)
        
    def write(self,stream):
        ProxyBounds.write(self,stream)

    def export_obj(self,obj):
        print "  BoxBounds export"
        # first get worldspace bounding box
        verts=obj.getBoundBox()
        
        # get WorldToLocal matrix...
        matrix=hsMatrix44()
        m=getMatrix(obj)
        m.invert()
        m.transpose()
        matrix.set(m)
        
        #transform coordinates to local
        tverts=[]
        for vi in verts:
            v=Vertex(vi[0],vi[1],vi[2])
            v.transform(matrix)
            va=[v.x,v.y,v.z]
            tverts.append(va)
        verts=tverts
        #
        try:
            c=alcConvexHull(verts)
            self.vertexs=c.vertexs
            self.faces=c.faces
        except:
            raise RuntimeException, "Error Generating physical bounding box for object " + str(obj.name) + " please select another bounding method"

    def export_raw(self,vertices,faces=None):
        boundsmin=None # maximum vertex
        boundsmax=None # minimum vertex

        # store each vertex
        for vertex in vertices:
            # Determine if the vertex needs to be made
            if boundsmin is None or boundsmax is None:
                boundsmin = Vertex(vert.x,vert.y,vert.z)
                boundsmax = Vertex(vert.x,vert.y,vert.z)
            else:
                if vert.x < boundsmin.x:
                    boundsmin.x = vert.x
                if vert.y < boundsmin.y:
                    boundsmin.y = vert.y
                if vert.z < boundsmin.z:
                    boundsmin.z = vert.z
                if vert.x > boundsmax.x:
                    boundsmax.x = vert.x
                if vert.y > boundsmax.y:
                    boundsmax.y = vert.y
                if vert.z > boundsmax.z:
                    boundsmax.z = vert.z
        box = []
        box.append([boundsmin.x,boundsmin.y,boundsmin.z])
        box.append([boundsmin.x,boundsmin.y,boundsmax.z])
        box.append([boundsmin.x,boundsmax.y,boundsmin.z])
        box.append([boundsmin.x,boundsmax.y,boundsmax.z])
        box.append([boundsmax.x,boundsmin.y,boundsmin.z])
        box.append([boundsmax.x,boundsmin.y,boundsmax.z])
        box.append([boundsmax.x,boundsmax.y,boundsmin.z])
        box.append([boundsmax.x,boundsmax.y,boundsmax.z])

        c=alcConvexHull(box)
        self.vertexs=c.vertexs
        self.faces=c.faces


        
class ExplicitBounds(ProxyBounds): # essentially a basic copy of proxybounds
    def __init__(self,type=plPhysical.Bounds["kExplicitBounds"]):
        ProxyBounds.__init__(self,type)
    
    def read(self,stream):
        ProxyBounds.read(self,stream)
        
    def write(self,stream):
        ProxyBounds.write(self,stream)
            

class plHKPhysical(plPhysical):    
    ## Conjectured constants following:

    # Constants in these Dictionaries start with 'c' instead of 'k', to inticate that
    # they are not known flags, but conjectured settings.

    # cNone             object is not used for avatar or other object collision (can be used for camera collision)
    # cStorePosition    object responds to avatar and location is remembered after exit
    # cResetPosition    object responds to avatar and location is reset after exit.
    # cDetector         is for detector regions and clickables, indicating game logic of some kinf

    # cIgnoreAvatars    do not respond to objects of same type
    
    # flags for gColType (was 'type')
    Collision = \
    { \
        "cNone"             : 0x0000,\
        "cIgnoreAvatars"    : 0x0002,\
        "cStorePosition"    : 0x0100,\
        "cResetPosition"    : 0x0200,\
        "cDetector"         : 0x0400,\
    }
    
    
    # flags for gFlagsDetect (was 'flags1')
    
    # cDetectVolume         is used in swim detection regions
    # cDetectBoundaries     is used in generic detection regions that need to do things on entry and exit
    FlagsDetect = \
    { \
        "cDetectNone"       : 0x00000000,\
        "cDetectVolume"     : 0x00020000,\
        "cDetectBoundaries" : 0x08000000\
    }
    
    # flags for gFlagsRespond (was 'flags2')
    FlagsRespond = \
    { \
        "cRespNone"         : 0x00000000,\
        "cRespClickable"    : 0x00020000,\
        "cRespInitial"      : 0x02000000\
    }
    
    ## end conjectured flags

    # Used for exporting (blender hull types):

    HullTypes = {"BOX" : 0, "SPHERE" : 1, "CYLINDER" : 2, "CONE" : 3, "TRIANGLEMESH" : 4, "CONVEXHULL" : 5}    

    def __init__(self,parent,name="unnamed",type=0x003F):
        plSynchedObject.__init__(self,parent,name,type)
        
        ## Havok structure?
        self.fPosition=Vertex() #position
        self.fOrientation=hsQuat() #orientation
        self.fMass=0.0   #mass (if 0, position is ignored as well as any related coordinate interface)
        self.fRC=10.0    #refriction coefficient
        self.fEL=0.0     #elasticity
        self.fBounds = ProxyBounds()
        
        ## Fairly unkown parts
        
        # Fields in this part are starting with "g" instead of the default "f".
        # this is to indicate that they are not known fields, but conjectured names and bitfields
        
        self.gShort1=0
        # 0x00 almost always
        # 0x02 TreeDummy02 (sphere02)

        self.gColType=plHKPhysical.Collision["cResetPosition"]

        self.gFlagsDetect=plHKPhysical.FlagsDetect["cDetectNone"]
        self.gFlagsRespond=plHKPhysical.FlagsRespond["cRespInitial"]
        
        self.gBool1=0 
        self.gBool2=0
       
        
        ## Uru structure
        self.fSceneObject=UruObjectRef()
        self.fGroup = hsBitVector()
        self.fScene=UruObjectRef()
        self.fLOSDB=plHKPhysical.plLOSDB["kLOSDBNone"]
        self.fSubWorld=UruObjectRef()
        self.fSndGroup=UruObjectRef()
        self.blendobj = None


    def changePageRaw(self,sid,did,stype,dtype):
        plSynchedObject.changePageRaw(self,sid,did,stype,dtype)
        self.sceneobject.changePageRaw(sid,did,stype,dtype)
        self.scene.changePageRaw(sid,did,stype,dtype)
        self.subworld.changePageRaw(sid,did,stype,dtype)
        self.sndgroup.changePageRaw(sid,did,stype,dtype)


    def read(self,stream):
        plSynchedObject.read(self,stream)
        
        self.fPosition.read(stream)
        self.fOrientation.read(stream)

        self.fMass = stream.ReadFloat()
        self.fRC = stream.ReadFloat()
        self.fEL = stream.ReadFloat()
        bounds = stream.Read32()

        self.gShort1 = stream.Read16()
        self.gColType  = stream.Read16()

        self.gFlagsDetect = stream.Read32()
        self.gFlagsRespond = stream.Read32()
        self.gBool1 = stream.ReadBool()
        self.gBool2 = stream.ReadBool()

        if bounds == plPhysical.Bounds["kBoxBounds"]:
            self.fBounds = BoxBounds()
        elif bounds == plPhysical.Bounds["kSphereBounds"]:
            self.fBounds = SphereBounds()
        elif bounds == plPhysical.Bounds["kHullBounds"]:
            self.fBounds = HullBounds()
        elif bounds == plPhysical.Bounds["kProxyBounds"]:
            self.fBounds = ProxyBounds()
        else:
            self.fBounds = ExplicitBounds()

        self.fBounds.read(stream) # HKBounds Subclass specifically set above


        self.fSceneObject.read(stream)
        self.fGroup.read(stream) # bitvector
        self.fScene.read(stream)
        self.fLOSDB = stream.Read32()
        self.fSubWorld.read(stream)
        self.fSndGroup.read(stream)


    def write(self,stream):
        plSynchedObject.write(self,stream)

        self.fPosition.write(stream)

        self.fOrientation.write(stream)

        stream.WriteFloat(self.fMass)
        stream.WriteFloat(self.fRC)
        stream.WriteFloat(self.fEL)

        stream.Write32(self.fBounds.fType) # retrieve from HKBounds Subclass

        stream.Write16(self.gShort1)
        stream.Write16(self.gColType)

        stream.Write32(self.gFlagsDetect)
        stream.Write32(self.gFlagsRespond)
        stream.WriteBool(self.gBool1)
        stream.WriteBool(self.gBool2)

        self.fBounds.write(stream) # HKBounds Subclass

        self.fSceneObject.write(stream)
        self.fGroup.write(stream)
        self.fScene.write(stream)
        stream.Write32(self.fLOSDB)
        self.fSubWorld.write(stream)
        self.fSndGroup.write(stream)

    def _Find(page,name):
        return page.find(0x003F,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x003F,name,1)
    FindCreate = staticmethod(_FindCreate)

    def import_obj(self,obj,scnobj):
        print "  [HKPhysical %s]"%(str(self.Key.name))
        root= self.getRoot()
        
        # find the Mesh Object
        mesh = obj.getData(False,True) # gets a Mesh object instead of an NMesh
        
        print "   fBounds.fType:",self.fBounds.fType
        if self.fBounds.fType == plPhysical.Bounds["kBoxBounds"]:
            # Just use this object as the object to work on
            sobj = obj
            sobj.rbFlags |= Blender.Object.RBFlags["BOUNDS"]
            sobj.rbShapeBoundType = plHKPhysical.HullTypes["BOX"]
            
        elif self.fBounds.fType == plPhysical.Bounds["kSphereBounds"]:
            sobj = obj
            sobj.rbFlags |= Object.RBFlags["BOUNDS"]
            sobj.rbShapeBoundType = plHKPhysical.HullTypes["SPHERE"]
            
        elif self.fBounds.fType == plPhysical.Bounds["kHullBounds"]:
            # use the amount of vertices as a way to see if we must create a new object, or if we can assume
            # that the objects drawables are similar to the objects physical data
            if not scnobj.draw.isNull():
                if len(self.fBounds.fVertices) != len(mesh.verts):
                   # Directly read it into a hull
                    hull = alcConvexHull(self.fBounds.fVertices)
                    sobj=alcCreateMesh('Phys_' + str(self.Key.name),hull.vertexs,hull.faces)
                    if self.getPageNum() != 0: # but only if it's not page 0
                        obj.addProperty("page_num",str(self.getPageNum()))
                    sobj.addProperty("alctype","collider")
                    sobj.addProperty("rootobj",obj.name)
                    sobj.layers=[2,]
                    sobj.drawType=2
                    plCoordinateInterface.Import(scnobj,root,sobj) # apply the coordinate interface to the new object
                else:
                    # separate physical mesh is ignorable
                    sobj = obj
            else:
                sobj = obj
                hull = alcConvexHull(self.fBounds.fVertices)
                mesh.verts.extend(hull.vertexs)
                mesh.faces.extend(hull.faces)
                sobj.addProperty("alctype","collider")
                sobj.layers=[2,]
                sobj.drawType=2

            sobj.rbFlags |= Blender.Object.RBFlags["BOUNDS"]
            sobj.rbShapeBoundType = plHKPhysical.HullTypes["CONVEXHULL"]

        elif self.fBounds.fType == plPhysical.Bounds["kProxyBounds"] or self.fBounds.fType == plPhysical.Bounds["kExplicitBounds"]:
            # use the amount of vertices as a way to see if we must create a new object, or if we can assume
            # that the objects drawables are similar to the objects physical data
            if not scnobj.draw.isNull():
                if len(self.fBounds.fVertices) != len(mesh.verts):
                    sobj=alcCreateMesh('Phys_' + str(self.Key.name),self.fBounds.fVertices,self.fBounds.fFaces)
                    if self.getPageNum() != 0: # but only if it's not page 0
                        obj.addProperty("page_num",str(self.getPageNum()))
                    sobj.addProperty("alctype","collider")
                    sobj.addProperty("rootobj",obj.name)
                    sobj.layers=[2,]
                    sobj.drawType=2
                    plCoordinateInterface.Import(scnobj,root,sobj) # apply the coordinate interface to the new object
                else:
                    # separate physical mesh is ignorable
                    sobj = obj
            else:
                sobj = obj
                print "   Vertex Count :",len(self.fBounds.fVertices)
                print "   Face Count   :",len(self.fBounds.fFaces)
                mesh.verts.extend(self.fBounds.fVertices)
                mesh.faces.extend(self.fBounds.fFaces)
                sobj.addProperty("alctype","collider")
                sobj.layers=[2,]
                sobj.drawType=2
                
            sobj.rbFlags |= Blender.Object.RBFlags["BOUNDS"]
            sobj.rbShapeBoundType = plHKPhysical.HullTypes["TRIANGLEMESH"]

        if self.fMass > 0.0:
            sobj.rbFlags |= Blender.Object.RBFlags["ACTOR"]
            sobj.rbFlags |= Blender.Object.RBFlags["DYNAMIC"]
            sobj.rbMass = self.fMass
        
        # Continue now with adding friction and elasticity
        
        objscript = AlcScript.objects.FindOrCreate(obj.name)

        
        # See if it should be considered a region, and process accordingly...
        
        # Import Modifiers
        IsRegion = False
        IsSurface = False
        
        for m_ref in scnobj.data2.vector:
            # plCameraRegionDetector
            # plSwimRegion
            # plPanicLinkRegion
            # plAVLadderMod
            # plObjectInVolumeDetector
            if m_ref.Key.object_type in [0x006F,0x012E,0x00FC,0x00B2,0x007B]:
                mod=root.findref(m_ref)
                if not mod is None:
                    mod.data.import_obj(sobj)        
                    IsRegion = True

        for i_ref in scnobj.data1.vector:
            # plSwimRegionInterface
            # plSwimCircularCurrentRegion
            # plSwimStraightCurrentRegion
            if i_ref.Key.object_type in [0x0133,0x0134,0x0136]: 
                intf=root.findref(i_ref)
                if not intf is None:
                    intf.data.import_obj(sobj)        
                    IsSurface = True

        if not (IsRegion or IsSurface or self.gColType == plHKPhysical.Collision["cDetector"]):
            #sobj.addProperty("coltype",self.gColType) # debug only...
            if self.gColType == plHKPhysical.Collision["cNone"]:
                
                if self.fLOSDB & plPhysical.plLOSDB["kLOSDBCameraBlockers"]:
                    try:
                        sobj.removeProperty("alctype")
                    except:
                        pass
                    sobj.addProperty("alctype","camcollider")
                else:
                    # Not a camera colloder, but probably covered by a region we don't get yet..
                    pass
            else:
                if not (self.fLOSDB & plPhysical.plLOSDB["kLOSDBAvatarWalkable"]):
                    StoreInDict(objscript,"physical.friction",self.fRC)
        
                if self.fEL > 0.0:
                    StoreInDict(objscript,"physical.elasticity",self.fEL)
        
                if self.fGroup[plPhysical.Group["kGroupDynamicBlocker"]]:
                    StoreInDict(objscript,"physical.pinned","true")
                
                if not (self.fLOSDB & plPhysical.plLOSDB["kLOSDBCameraBlockers"]):
                    StoreInDict(objscript,"physical.campassthrough","true")

        else:
            # If it is a region...
            sobj.layers=[3,] # regions go to layer 3
            try:
                sobj.removeProperty("alctype")
            except:
                pass
            sobj.addProperty("alctype","region")

            
  
    def export_obj(self,obj,scnobj,isdynamic=0):
        print " [Physical]"
        
        # determine the hull type
        if obj.rbFlags & Object.RBFlags["BOUNDS"]:
            if obj.rbShapeBoundType == plHKPhysical.HullTypes["BOX"]:
                self.fBounds = BoxBounds()
            elif obj.rbShapeBoundType == plHKPhysical.HullTypes["SPHERE"]:
                self.fBounds = SphereBounds()
            elif obj.rbShapeBoundType == plHKPhysical.HullTypes["CYLINDER"]:
                self.fBounds = HullBounds()
            elif obj.rbShapeBoundType == plHKPhysical.HullTypes["CONE"]:
                self.fBounds = HullBounds()
            elif obj.rbShapeBoundType == plHKPhysical.HullTypes["TRIANGLEMESH"]:
                self.fBounds = ProxyBounds()
            elif obj.rbShapeBoundType == plHKPhysical.HullTypes["CONVEXHULL"]:
                self.fBounds = HullBounds()
            else:
                self.fBounds = HullBounds()
        else:
            # this should never happen, because objects without bounds set
            # should not be given a physical prp object
            # Failsafe will put it to HullBounds
            self.fBounds = HullBounds()

        # export the hull
        self.fBounds.export_obj(obj)

        # retrieve alcscript for this object
        objscript = AlcScript.objects.Find(obj.name)

        ## First determine if we should encode this as a region
        ## This should happen here, rather than in the resource manager, to avoid
        ## code congestion
        try:
            prptype = objscript['type']
        except:
            prptype = "object"
        prptype = getTextPropertyOrDefault(obj,"alctype",prptype)
        
        if prptype == "region":
            print "  Setting Region-Specific settings...."
            regiontype = FindInDict(objscript,'regiontype',"logic")
            
            regiontype = getTextPropertyOrDefault(obj,"regiontype",regiontype)
           
            if regiontype == "swimdetect":
                # set the Collision Type to Detector
                self.gColType = plHKPhysical.Collision["cDetector"]#["cNone"]
    
                # set mass to 0.0, for swimregions
                self.fMass = 0.0
                self.fRC = 0.0
                self.fEL = 0.0
                
                self.gFlagsDetect  = plHKPhysical.FlagsDetect["cDetectVolume"]
                self.gFlagsRespond = plHKPhysical.FlagsRespond["cRespNone"]

                #self.fLOSDB=plHKPhysical.plLOSDB["kLOSDBSwimRegion"] #8D in AhnShpere1
                
            elif regiontype == "swim":
                # set the Collision Type to None
                self.gColType = plHKPhysical.Collision["cDetector"]#["cNone"]
    
                # set mass to 0.0, for swimregions
                self.fMass = 0.0
                self.fRC = 0.0
                self.fEL = 0.0

                self.gFlagsDetect  = plHKPhysical.FlagsDetect["cDetectNone"]
                self.gFlagsRespond = plHKPhysical.FlagsRespond["cRespNone"]

                self.fLOSDB=plHKPhysical.plLOSDB["kLOSDBSwimRegion"]

            else:
                # set the Collision Type to Detector
                self.gColType = plHKPhysical.Collision["cDetector"]
    
                # set mass to 1.0, as is default for regions
                self.fMass = 1.0
                self.fRC = 0.0
                self.fEL = 0.0

                self.gFlagsDetect  = plHKPhysical.FlagsDetect["cDetectBoundaries"]
                self.gFlagsRespond = plHKPhysical.FlagsRespond["cRespNone"]

                self.fGroup[plHKPhysical.Group["kGroupDynamicBlocker"]] = 1
        

        else:
            # if not a region

            # retrieve mass from Blender rigid body settings if available
            if obj.rbFlags & Blender.Object.RBFlags["ACTOR"]:
                if obj.rbFlags & Blender.Object.RBFlags["DYNAMIC"]:
                    self.fMass = obj.rbMass
                else:
                    self.fMass = 1.0
            else:
                self.fMass = 0.0
            
            if self.fMass <= 0.0:
                print "  No Mass"
            else:
                print "  Mass",obj.rbMass

            # retrieve friction from logic property
            self.fRC = getFloatPropertyOrDefault(obj,"rc",-1.0)
            if self.fRC == -1.0:
                # retrieve from alcscript if not set as logic property
                self.fRC = float(FindInDict(objscript,"physical.friction",-1.0))

            if self.fRC < 0.0:
                print "  No Friction, disabling frictive setting"
                # If no friction is set, or it is set lower than 0
                # Default it to a relatively high setting
                self.fRC = 100.0 
                # And disable friction :)
                self.fLOSDB |= plPhysical.plLOSDB["kLOSDBAvatarWalkable"]
            else:
                print "  Friction:",self.fRC
    
            # retrieve elasticity from logic property
            self.fEL = getFloatPropertyOrDefault(obj,"el",-1)
            if self.fEL == -1:
                self.fEL = float(FindInDict(objscript,"physical.elasticity",0.0))
            if self.fEL < 0.0:
                print "  No Elasticity set"
            else:
                print "  Elasticity:",self.fEL

            self.gFlagsDetect = plHKPhysical.FlagsDetect["cDetectNone"]
            self.gFlagsRespond = plHKPhysical.FlagsRespond["cRespInitial"]

            if scnobj.attach.has_key('clickable') and scnobj.attach['clickable'] == True: # 
                # Special settings when an object is "clickable"
                
                self.gFlagsRespond = plHKPhysical.FlagsRespond["cRespClickable"]
                self.gColType = plHKPhysical.Collision["cDetector"]
                self.fGroup[plHKPhysical.Group["kGroupDynamicBlocker"]] = 1
                self.fLOSDB |= plHKPhysical.plLOSDB["kLOSDBUIItems"]

            else:
                # basic setting: if it is dynamic, it is kickable
                if not isdynamic:
                    self.gColType = plHKPhysical.Collision["cStorePosition"]
                else:
                    self.gColType = plHKPhysical.Collision["cResetPosition"]        
                
                if (str(FindInDict(objscript,"physical.pinned","false")).lower() == "true" or (obj.rbFlags & Blender.Object.RBFlags["DYNAMIC"] == 0 and obj.rbFlags & Blender.Object.RBFlags["ACTOR"])):
                    print "  Pinning object"
                    self.fGroup[plPhysical.Group["kGroupDynamicBlocker"]] = 1
                
                # and make objects Camera Blockers By default - or let them through if physical.camerapassthrough is set to true
                if str(FindInDict(objscript,"physical.campassthrough","false")).lower() != "true":
                    print "  Camera blocking enabled"
                    self.fLOSDB |= plPhysical.plLOSDB["kLOSDBCameraBlockers"]
                else:
                    print "  Camera blocking disabled"

        #set position and other attribs
        if (self.fMass == 0.0 and  isdynamic == 0): 
            print "  Object is Static"
            #transform to world for static objects
            self.fBounds.Transform_obj(obj) # do this with transformation data from object
        else:
            print "  Object is Dynamic"
            # set position
            x,y,z = obj.getLocation()
            self.Position=Vertex(x,y,z)

            # set orientation
            m = getMatrix(obj)
            quat = m.toQuat()
            quat.normalize()
            self.fOrientation = hsQuat()
            self.fOrientation.setQuat(quat)
            
            # transform the object, size only.
            self.fBounds.SizeTransform_obj(obj)


    def export_raw(self,L2Wmatrix,vertex_list,face_list,col_type,isdynamic,mass=1.0):
        # set the objects properties to a default region
        
        if col_type == plPhysical.Bounds["kBoxBounds"]:
            self.fBounds = BoxBounds()
        elif col_type == plPhysical.Bounds["kSphereBounds"]:
            self.fBounds = SphereBounds()
        elif col_type == plPhysical.Bounds["kHullBounds"]:
            self.fBounds = HullBounds()
        elif col_type == plPhysical.Bounds["kProxyBounds"]:
            self.fBounds = ProxyBounds()
        elif col_type == plPhysical.Bounds["kExplicitBounds"]:
            self.fBounds = ExplicitBounds()
        else:
            self.fBounds = HullBounds()

        # export the hull
        self.fBounds.export_raw(vertex_list,face_list)
            
            
        # set default settings....
        self.fMass = mass
        self.fRC = 0.0
        self.fEL = 0.0

        # export_raw is ususally only used for regions
        self.gFlagsDetect = plHKPhysical.FlagsDetect["cDetectBoundaries"]
        self.gFlagsRespond = plHKPhysical.FlagsRespond["cRespNone"]

        self.gColType = plHKPhysical.Collision["cDetector"]
        
        self.fGroup[plPhysical.Group["kGroupDynamicBlocker"]] = 1
        self.fLOSDB = 0

        #set position and other attribs
        if (self.fMass == 0.0 and  isdynamic == 0): 
            #transform to world for static objects
            self.fBounds.Transform_obj(obj) # do this with transformation data from object
        else:
            # set position
            x,y,z = L2Wmatrix.translationPart()
            self.Position=Vertex(x,y,z)

            # set orientation
            quat = L2Wmatrix.toQuat()
            quat.normalize()
            self.fOrientation = hsQuat()
            self.fOrientation.setQuat(quat)
            
            # transform the object, size only.
            self.fBounds.SizeTransform_mtx(L2Wmatrix)
