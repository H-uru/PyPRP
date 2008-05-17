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
from alcConvexHull import *
from alc_AbsClasses import *
from alc_MatClasses import *
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


class plLightInfo(plObjInterface):                          #Type 0x54 (Uru)
    
    Props = \
    { \
        "kDisable"              : 0, \
        "kLPObsolete"           : 1, \
        "kLPCastShadows"        : 2, \
        "kLPMovable"            : 3, \
        "kLPHasIncludes"        : 4, \
        "kLPIncludesChars"      : 5, \
        "kLP_OBSOLECTE_0"       : 6, \
        "kLPOverAll"            : 7, \
        "kLPHasSpecular"        : 8, \
        "kLPShadowOnly"         : 9, \
        "kLPShadowLightGroup"   : 10, \
        "kLPForceProj"          : 11, \
        "kNumProps"             : 12  \
    }
    
    scriptProps = \
    { \
        "disable"              : 0, \
        "obsolete"             : 1, \
        "castshadows"          : 2, \
        "movable"              : 3, \
        "hasincludes"          : 4, \
        "includeschars"        : 5, \
        "obsolecte_0"          : 6, \
        "overall"              : 7, \
        "hasspecular"          : 8, \
        "shadowonly"           : 9, \
        "shadowlightgroup"     : 10, \
        "forceproj"            : 11, \
    }
    
    def __init__(self,parent,name="unnamed",type=None):
        plObjInterface.__init__(self,parent,name,type)
        try: #Quick, dirty fix for NameError bug with classes from alc_GeomClasses
            self.ambient = RGBA('1.0','1.0','1.0','1.0',type=1)
        except NameError:
            #print "Damnit! Need reimport alc_GeomClasses.py"
            from alc_GeomClasses import RGBA,hsMatrix44
            self.ambient = RGBA('1.0','1.0','1.0','1.0',type=1)

        self.diffuse = RGBA()
        self.specular = RGBA()
        
        self.LightToLocal = hsMatrix44()
        self.LocalToLight = hsMatrix44()
        self.LightToWorld = hsMatrix44()
        self.WorldToLight = hsMatrix44()
        
        self.fProjection = UruObjectRef(self.getVersion()) #plLayerInterface
        self.softvol = UruObjectRef(self.getVersion()) #plSoftVolume
        self.scenenode = UruObjectRef(self.getVersion()) #Dunno
        
        self.visregs = hsTArray([],self.getVersion()) #plVisRegion[]
    
    def read(self,buf):
        plObjInterface.read(self,buf)
        self.ambient.read(buf)
        self.diffuse.read(buf)
        self.specular.read(buf)
        self.LightToLocal.read(buf)
        self.LocalToLight.read(buf)
        self.LightToWorld.read(buf)
        self.WorldToLight.read(buf)
        self.fProjection.read(buf)
        self.softvol.read(buf)
        self.scenenode.read(buf)


        self.visregs.read(buf)
    
    def write(self,buf):
        plObjInterface.write(self,buf)
        self.ambient.write(buf)
        self.diffuse.write(buf)
        self.specular.write(buf)
        self.LightToLocal.write(buf)
        self.LocalToLight.write(buf)
        self.LightToWorld.write(buf)
        self.WorldToLight.write(buf)
        self.fProjection.write(buf)
        self.softvol.write(buf)
        self.scenenode.write(buf)

        self.visregs.write(buf)
    
    def changePageRaw(self,sid,did,stype,dtype):
        plObjInterface.changePageRaw(self,sid,did,stype,dtype)
        self.softvol.changePageRaw(sid,did,stype,dtype)
        self.layerint.changePageRaw(sid,did,stype,dtype)
        self.scenenode.changePageRaw(sid,did,stype,dtype)
        self.visregs.changePageRaw(sid,did,stype,dtype)

    def _Import(scnobj,prp,obj):
        # Lights
        for li in  scnobj.data1.vector:
            if li.Key.object_type in [0x55,0x56,0x57]:
                light=prp.findref(li)
                light.data.import_obj(obj)
                break
        # Shadows
        for sh in  scnobj.data1.vector:
            if sh.Key.object_type in [0xD5,0xD6]:
                shadow=prp.findref(sh)
                shadow.data.import_obj(obj)

    Import = staticmethod(_Import)

    def _Export(page,obj,scnobj,name,SceneNodeRef,softVolumeParser):

        # --- Determine Lamp type and Shadow Type ---
        shadow = None
        if obj.data.type==Blender.Lamp.Types["Spot"]:
            # plSpotLightInfo
            lamp=plSpotLightInfo.FindCreate(page,name)
            if obj.data.mode & Blender.Lamp.Modes["RayShadow"]:
                # plPointShadowMaster
                shadow = plPointShadowMaster.FindCreate(page,name)
        elif obj.data.type==Blender.Lamp.Types["Lamp"]:
            # plOmniLightInfo
            lamp=plOmniLightInfo.FindCreate(page,name)
            if obj.data.mode & Blender.Lamp.Modes["RayShadow"]:
                # plPointShadowMaster
                shadow = plPointShadowMaster.FindCreate(page,name)
        elif obj.data.type==Blender.Lamp.Types["Area"]:
            # plLimitedDirLightInfo
            lamp=plLimitedDirLightInfo.FindCreate(page,name)
            if obj.data.mode & Blender.Lamp.Modes["RayShadow"]:
                # plDirectionalShadowMaster
                shadow = plDirectShadowMaster.FindCreate(page,name)
        else:
            # plDirectionalLightInfo
            lamp=plDirectionalLightInfo.FindCreate(page,name)
            if obj.data.mode & Blender.Lamp.Modes["RayShadow"]:
                # plDirectionalShadowMaster
                shadow = plDirectShadowMaster.FindCreate(page,name)
                
        # --- Check if Lamp has a projection layer --- (HACK WARNING)
        lampscript = AlcScript.objects.Find(obj.getName())
        layername = FindInDict(lampscript,"lamp.layer",None)
        if(layername != None):
            print " Attatching layer: " + layername
            refparser = ScriptRefParser(page, name, 0x0006, [0x0006, 0x0043,])
            layer = refparser.MixedRef_FindCreate(layername)
            lamp.data.fProjection = layer.data.getRef()
            # set the projection flags depending on the lamp type
            if obj.data.type==Blender.Lamp.Types["Spot"]:
                layer.data.fState.fMiscFlags |= hsGMatState.hsGMatMiscFlags["kMiscPerspProjection"]
            elif obj.data.type==Blender.Lamp.Types["Area"]:
                layer.data.fState.fMiscFlags |= hsGMatState.hsGMatMiscFlags["kMiscOrthoProjection"]
            # now we set the uvw transform on the layer
            texMatrix = getMatrix(obj)
            texMatrix.transpose()
            layer.data.fTransform.set(texMatrix)

        # --- Prepare and Export lamp object ---
        lamp.data.parentref=scnobj.data.getRef()
        lamp.data.scenenode=SceneNodeRef
        lamp.data.softVolumeParser = softVolumeParser
        lamp.data.export_object(obj)
        scnobj.data.data1.append(lamp.data.getRef())

        # --- Prepare and Export Shadow object ---
        if shadow != None:
            shadow.data.parentref=scnobj.data.getRef()
            shadow.data.export_obj(obj)
            scnobj.data.data1.append(shadow.data.getRef())

    Export = staticmethod(_Export)

#list1
class plDirectionalLightInfo(plLightInfo):    
    def __init__(self,parent,name="unnamed",type=0x0055):
        plLightInfo.__init__(self,parent,name,type)
        self.softVolumeParser = None    

    def _Find(page,name):
        return page.find(0x0055,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0055,name,1)
    FindCreate = staticmethod(_FindCreate)

    def import_obj(self,obj):
        #the_name=alcUniqueName(name)
        if self.Key.object_type==0x55:
            type="Area"
        elif self.Key.object_type==0x56:
            type="Lamp"
        elif self.Key.object_type==0x57:
            type="Spot"
        else:
            raise "Unknown Lamp type"
        lamp=Blender.Lamp.New(type,str(self.Key.name))
        obj.link(lamp)

        obj.data.energy=0.5
        obj.data.dist = 1000 # plasma has no distance limit for these lights, we should reflect that in blender
        
        maxval = max(max(self.diffuse.r,self.diffuse.g),self.diffuse.b)
        
        if maxval > 1:
            obj.data.energy = maxval * 0.5
            lamp.R = self.diffuse.r / maxval
            lamp.G = self.diffuse.g / maxval
            lamp.B = self.diffuse.b / maxval
        else:
            obj.data.energy = 1 * 0.5
            lamp.R = self.diffuse.r
            lamp.G = self.diffuse.g
            lamp.B = self.diffuse.b
        
        
        softVolObj = self.getRoot().findref(self.softvol)
        if softVolObj != None:
            obj.addProperty("softvolume",softVolObj.data.getPropertyString(),'STRING')
        return obj


    def export_object(self,obj):
        lamp=obj.data
        objscript = AlcScript.objects.Find(obj.getName())
        
        print " [Light Base]\n";
        
        #set lighting flags
        try:
            p=obj.getProperty("flags")
            name=str(p.getData())
            while len(name)<8:
                name = "0" + name
            b=binascii.unhexlify(str(name))
            l,=struct.unpack(">I",b)
        except (AttributeError, RuntimeError):
            l=0
        self.BitFlags.append(l)
        
        
        # Determine negative lighting....
        if lamp.mode & (Lamp.Modes["Negative"]):
            print "  >>>Negative light<<<"
            R = 0.0 - lamp.R
            G = 0.0 - lamp.G
            B = 0.0 - lamp.B
        else:
            R = lamp.R
            G = lamp.G
            B = lamp.B

        # Plasma has the same Lights as DirectX:
        #
        
        energy = lamp.energy * 2
        
        # Diffuse:
        if lamp.mode & (Lamp.Modes["NoDiffuse"]):
            print "  Diffuse Lighting Disabled";
            self.diffuse=RGBA(0.0,0.0,0.0,1.0,type=1)
        else:
            print "  Diffuse Lighting Enabled";
            self.diffuse=RGBA(R*energy,G*energy,B*energy,1.0,type=1)

        # Specular
        if lamp.mode & (Lamp.Modes["NoSpecular"]):
            print "  Specular Lighting Disabled";
            self.specular=RGBA(0.0,0.0,0.0,1.0,type=1)
        else:
            print "  Specular Lighting Enabled";
            self.specular=RGBA(R*energy,G*energy,B*energy,1.0,type=1)
        
        # Ambient:
        # Light not directly emitted by the light source, but present because of it.

        # If one wants to use a lamp as ambient, disable both diffuse and specular colors
        # Else, it's just set to 0,0,0 aka not used.
        
        if lamp.mode & (Lamp.Modes["NoSpecular"] | Lamp.Modes["NoDiffuse"]):
            print "  Lamp is set as ambient light"
            self.ambient = RGBA(R * energy, G * energy, B * energy,1.0,type=1)
        else:
            self.ambient = RGBA(0.0, 0.0, 0.0, 0.0, type=1)
        
        # Now Calculate the matrix:
        m=getMatrix(obj)
        m.transpose()
        # Note: 
        # In Blender, the Light cannot be moved in local space,
        # so Light To Local is not needed, and can remain a unity matrix.
        # 
        # 
        # self.LightToLocal.set(m)
        # self.LocalToLight.set(m)
        
        self.LightToWorld.set(m)
        m.invert()
        self.WorldToLight.set(m)


        #Set some shadow flags
        if lamp.mode & (Lamp.Modes["RayShadow"]):
            print "  >>> kLPCastShadows <<<"
            self.BitFlags[plLightInfo.Props["kLPCastShadows"]] = 1
        else:
            print "  >>> !kLPCastShadows <<<"
            self.BitFlags[plLightInfo.Props["kLPCastShadows"]] = 0
        
        if lamp.mode & (Lamp.Modes["OnlyShadow"]):
            print "  >>> kLPShadowOnly <<<"
            self.BitFlags[plLightInfo.Props["kLPShadowOnly"]] = 1
        else:
            print "  >>> !kLPShadowOnly <<<"
            self.BitFlags[plLightInfo.Props["kLPShadowOnly"]] = 0

        
        # Set the soft volume
        propString = FindInDict(objscript,"lamp.softvolume")
        propString = getTextPropertyOrDefault(obj,"softvolume",propString)
        if (propString != None):
            if(self.softVolumeParser != None and self.softVolumeParser.isStringProperty(propString)):
                self.softvol = self.softVolumeParser.parseProperty(propString,str(self.Key.name))
            else:
                refparser = ScriptRefParser(self.getRoot(),str(self.Key.name),"softvolume")
                volume = refparser.MixedRef_FindCreate(propString)
                self.softvol = volume.data.getRef()
        
        flags = FindInDict(objscript,"lamp.flags",None)
        if type(flags) == list:
            self.BitFlags = hsBitVector() # reset
            for flag in flags:
                if flag.lower() in plLightInfo.scriptProps:
                    print "    set flag: " + flag.lower()
                    idx =  plLightInfo.scriptProps[flag.lower()]
                    self.BitFlags.SetBit(idx)

#implemented in an attempt to make projection lights work
class plLimitedDirLightInfo(plDirectionalLightInfo):
    def __init__(self, parent, name="unnamed", type=0x006A):
        plDirectionalLightInfo.__init__(self, parent, name, type)
        self.fWidth = 256
        self.fHeight = 256
        self.fDepth = 256
        
    def _Find(page,name):
        return page.find(0x006A,name,0)
    Find = staticmethod(_Find)
    
    def _FindCreate(page,name):
        return page.find(0x006A,name,1)
    FindCreate = staticmethod(_FindCreate)
    
    def changePageRaw(self,sid,did,stype,dtype):
        plDirectionalLightInfo.changePageRaw(self,sid,did,stype,dtype)
    
    def read(self, stream):
        plDirectionalLightInfo.read(self,stream)
        self.fWidth  = stream.ReadFloat()
        self.fHeight = stream.ReadFloat()
        self.fDepth  = stream.ReadFloat()
        
    def write(self, stream):
        plDirectionalLightInfo.write(self,stream)
        stream.WriteFloat(self.fWidth)
        stream.WriteFloat(self.fHeight)
        stream.WriteFloat(self.fDepth)
        
    def export_object(self, obj):
        plDirectionalLightInfo.export_object(self, obj)
        lamp=obj.data
        objscript = AlcScript.objects.Find(obj.getName())
        
        self.fWidth = lamp.areaSizeX
        self.fHeight = lamp.areaSizeY
        self.fDepth = lamp.dist
        
        # Blender limits values to 100. Override via alcscript
        self.fWidth = FindInDict(objscript, "lamp.width", self.fWidth)
        self.fHeight = FindInDict(objscript, "lamp.height", self.fHeight)
        self.fDepth = FindInDict(objscript, "lamp.depth", self.fDepth)

#list1
class plOmniLightInfo(plDirectionalLightInfo): #Incorrect, but I guess it can slip   
    def __init__(self,parent,name="unnamed",type=0x0056):
        plDirectionalLightInfo.__init__(self,parent,name,type)
        #format
        self.fAttenConst=1.0
        self.fAttenLinear=0.0
        self.fAttenQuadratic=1.0
        self.fAttenCutoff=10.0
    
    def _Find(page,name):
        return page.find(0x0056,name,0)
    Find = staticmethod(_Find)
    
    def _FindCreate(page,name):
        return page.find(0x0056,name,1)
    FindCreate = staticmethod(_FindCreate)
    
    def changePageRaw(self,sid,did,stype,dtype):
        plDirectionalLightInfo.changePageRaw(self,sid,did,stype,dtype)
    
    def read(self,stream):
        plDirectionalLightInfo.read(self,stream)
        self.fAttenConst     = stream.ReadFloat()
        self.fAttenLinear    = stream.ReadFloat()
        self.fAttenQuadratic = stream.ReadFloat()
        self.fAttenCutoff    = stream.ReadFloat()
    
    def write(self,stream):
        plDirectionalLightInfo.write(self,stream)
        stream.WriteFloat(self.fAttenConst)
        stream.WriteFloat(self.fAttenLinear)
        stream.WriteFloat(self.fAttenQuadratic)
        stream.WriteFloat(self.fAttenCutoff)
    
    def import_obj(self,obj):
        plDirectionalLightInfo.import_obj(self,obj)

        obj.data.dist=self.fAttenCutoff*16
        
        if self.fAttenQuadratic  > 0.0:
            obj.data.mode = obj.data.mode | Blender.Lamp.Modes["Quad"]
            obj.data.quad1=self.fAttenLinear
            obj.data.quad2=self.fAttenQuadratic
        else:
            obj.data.mode = obj.data.mode | Blender.Lamp.Modes["Quad"]
        return obj
    
    def export_object(self,obj):
        plDirectionalLightInfo.export_object(self,obj)
        lamp=obj.data
        
        
        # To use blenders Half distance lighting setting, the following formula is used:
        # Linear Mode (default):
        # Blender: Intensity = BlenderDistance/(BlenderDistance + d)
        #
        # Quadratic Mode (blender [Quad] setting)
        # 
        # Blender: Intensity = BlenderDistance / (BlenderDistance + (Quad1 * d) + (Quad2 * d*d))
        # 
        # DirectX/Plasma: Intensity = 1 / ( fAttenConstant + fAttenLinear * d + fAttenQuadratic * d*d )
        # 
        # Conversion Yields:
        # fAttenQuadratic   = Quad2/BlenderDistance
        # fAttenLinear      = Quad1/BlenderDistance
        # fAttenConstant    = 1
        # 
        # 
        # Sphere (Sets Cutoff at Distance....)
        #
        #
        # # - Now there seems to be a problem with blenders distances in relation to plasma distances....
        #
        Dist = lamp.dist/16
        
        print " [OmniLight]\n";
        if lamp.mode & (Lamp.Modes["Quad"]):
            print "  Quadratic Attenuation"
            self.fAttenQuadratic = lamp.quad2/Dist
            self.fAttenLinear = lamp.quad1/Dist
            self.fAttenConstant = 1
        else:
            print "  Linear Attenuation"
            self.fAttenQuadratic = 0.0
            self.fAttenLinear = 1.0/Dist
            self.fAttenConstant = 1
       
        if lamp.mode & (Lamp.Modes["Sphere"]):
            print "  Sphere cutoff mode at %f" % lamp.dist
            self.fAttenCutoff= Dist
        else:
            print "  Long-range cutoff"
            self.fAttenCutoff= Dist * 10


#list1
class plSpotLightInfo(plOmniLightInfo):    
    def __init__(self,parent,name="unnamed",type=0x0057):
        plOmniLightInfo.__init__(self,parent,name,type)
        #format
        self.fFalloff=1.0
        self.fSpotInner=0.0
        self.fSpotOuter=0.0

    def _Find(page,name):
        return page.find(0x0057,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0057,name,1)
    FindCreate = staticmethod(_FindCreate)


    def read(self,stream):
        plOmniLightInfo.read(self,stream)
        self.fFalloff   = stream.ReadFloat()
        self.fSpotInner = stream.ReadFloat()   
        self.fSpotOuter = stream.ReadFloat()


    def write(self,stream):
        plOmniLightInfo.write(self,stream)
        stream.WriteFloat(self.fFalloff)
        stream.WriteFloat(self.fSpotInner)
        stream.WriteFloat(self.fSpotOuter)


    def import_obj(self,obj):
        obj=plOmniLightInfo.import_obj(self,obj)

        lamp = obj.data
        obj.addProperty("fFalloff",float(self.fFalloff))

        spotSizeDeg = self.fSpotOuter * 180.0 / 3.1415926536
        lamp.setSpotSize(spotSizeDeg)

        blend=0.0;
        if self.fSpotOuter > 0:
            blend = self.fSpotInner / self.fSpotOuter
        lamp.setSpotBlend(blend)

        return obj

    def export_object(self,obj):
        plOmniLightInfo.export_object(self,obj)
        lamp=obj.data

        print " [SpotLight]"

        # self.fFalloff= getFloatPropertyOrDefault(obj,"fFalloff",self.fFalloff);

        # Calculate the Outer angle of the Spotlight:
        spotSizeDeg = lamp.getSpotSize()
        self.fSpotOuter = spotSizeDeg * 3.1415926536 / 180.0
        
        # Now calculate the angle of the inner spotlight
        #self.fSpotInner = (0.99 - (lamp.spotBlend * 0.98)) * self.fSpotOuter
        self.fSpotInner = lamp.spotBlend * self.fSpotOuter
        
        # Set the falloff to 1.0
        if lamp.mode & (Lamp.Modes["Halo"]):
            print "  Using Halo setting for Spotlight Falloff"
            self.fFallOff = lamp.haloInt
        else:
            self.fFallOff = 1.0
           
class plShadowMaster(plObjInterface):    # Type: 0x00D3
    plDrawProperties = \
    { \
        "kDisable"      : 0,\
        "kSelfShadow"   : 1, \
        "kNumProps"     : 2  \
    }
    
    def __init__(self,parent,name="unnamed",type=0x00D3):
        plObjInterface.__init__(self,parent,name,type)
        self.fAttenDist = 10.0
        self.fMaxDist = 0.0
        self.fMinDist = 0.0
        self.fMaxSize = 256
        self.fMinSize = 256
        self.fPower = 2.0
    
    def _Find(page,name):
        return page.find(0x00D3,name,0)
    Find = staticmethod(_Find)
    
    def _FindCreate(page,name):
        return page.find(0x00D3,name,1)
    FindCreate = staticmethod(_FindCreate)
    
    def changePageRaw(self,sid,did,stype,dtype):
        plObjInterface.changePageRaw(self,sid,did,stype,dtype)
    
    def read(self,stream):
        plObjInterface.read(self,stream)
        
        self.fAttenDist = stream.ReadFloat()
        self.fMaxDist = stream.ReadFloat()
        self.fMinDist = stream.ReadFloat()
        self.fMaxSize = stream.Read32()
        self.fMinSize = stream.Read32()
        self.fPower = stream.ReadFloat()
    
    def write(self,stream):
        plObjInterface.write(self,stream)
        
        stream.WriteFloat(self.fAttenDist)
        stream.WriteFloat(self.fMaxDist)
        stream.WriteFloat(self.fMinDist)
        stream.Write32(self.fMaxSize)
        stream.Write32(self.fMinSize)
        stream.WriteFloat(self.fPower)
    
    def import_obj(self,obj):
        lamp = obj.data
        lamp.mode |= Blender.Lamp.Modes["RayShadow"]
    
    def export_obj(self,obj):
        lamp = obj.data
        
        print " [ShadowMaster]"
        self.BitFlags[plShadowMaster.plDrawProperties["kSelfShadow"]] = 1
        
        self.fAttenDist = 10
        
        self.fPower = lamp.energy
        print "  Power: %f" % self.fPower
        pass
        
class plShadowCaster(plMultiModifier):    #Type 0x00D4
    Flags = \
    { \
        "kNone"         : 0, \
        "kSelfShadow"   : 0x1, \
        "kPerspective"  : 0x2, \
        "kLimitRes"     : 0x4  \
    }
    def __init__(self,parent,name="unnamed",type=0x00D4):
        plMultiModifier.__init__(self,parent,name,type)

        self.fCastFlags = plShadowCaster.Flags["kNone"]
        self.fBoost = 1.5       # 1.0 (probable default)
        self.fAttenScale = 1    # 1.0 (probable default)
        self.fBlurScale = 0.3   # 0.0 (probable default)

    def _Find(page,name):
        return page.find(0x00D4,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x00D4,name,1)
    FindCreate = staticmethod(_FindCreate)


    def changePageRaw(self,sid,did,stype,dtype):
        plMultiModifier.changePageRaw(self,sid,did,stype,dtype)

    def read(self,stream):
        plMultiModifier.read(self,stream)

        self.fCastFlags = stream.ReadByte() & ~plShadowCaster.Flags["kPerspective"]
        self.fBoost = stream.ReadFloat();
        self.fAttenScale = stream.ReadFloat();
        self.fBlurScale = stream.ReadFloat();


    def write(self,stream):
        plMultiModifier.write(self,stream)

        stream.WriteByte(self.fCastFlags);
        stream.WriteFloat(self.fBoost);
        stream.WriteFloat(self.fAttenScale);
        stream.WriteFloat(self.fBlurScale);

    def export_obj(self,obj):
        print " [ShadowCaster]"
        self.fCastFlags = plShadowCaster.Flags["kSelfShadow"]
        pass
        
    def _Export(page,obj,scnobj,name,SceneNodeRef,isdynamic=0):
        if len(obj.data.materials) > 0 :
            if obj.data.materials[0].mode & Blender.Material.Modes["SHADOWBUF"]:
                shadowcaster = page.prp.find(0xD4,name,1)
                shadowcaster.data.export_obj(obj)
                scnobj.data.data2.append(shadowcaster.data.getRef())

    Export = staticmethod(_Export)
        
    
class plPointShadowMaster(plShadowMaster):    # Type: 0x00D5
    def __init__(self,parent,name="unnamed",type=0x00D5):
        plShadowMaster.__init__(self,parent,name,type)
    
    def _Find(page,name):
        return page.find(0x00D5,name,0)
    Find = staticmethod(_Find)
    
    def _FindCreate(page,name):
        return page.find(0x00D5,name,1)
    FindCreate = staticmethod(_FindCreate)
    
    def changePageRaw(self,sid,did,stype,dtype):
        plShadowMaster.changePageRaw(self,sid,did,stype,dtype)
    
    def read(self,stream):
        plShadowMaster.read(self,stream)
    
    def write(self,stream):
        plShadowMaster.write(self,stream)

class plDirectShadowMaster(plShadowMaster):    # Type: 0x00D6
    def __init__(self,parent,name="unnamed",type=0x00D6):
        plShadowMaster.__init__(self,parent,name,type)
    
    def _Find(page,name):
        return page.find(0x00D6,name,0)
    Find = staticmethod(_Find)
    
    def _FindCreate(page,name):
        return page.find(0x00D6,name,1)
    FindCreate = staticmethod(_FindCreate)
    
    def changePageRaw(self,sid,did,stype,dtype):
        plShadowMaster.changePageRaw(self,sid,did,stype,dtype)
    
    def read(self,stream):
        plShadowMaster.read(self,stream)
    
    def write(self,stream):
        plShadowMaster.write(self,stream)

