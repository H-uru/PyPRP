#
# $Id: alc_MatClasses.py 843 2007-09-13 01:19:29Z Trylon $
#
#    Copyright (C) 2005-2007  Alcugs pyprp Project Team
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
        from Blender import Ipo
        from Blender import BezTriple
    except Exception, detail:
        print detail
except ImportError:
    pass

import md5, random, binascii, cStringIO, copy, Image, math, struct, StringIO, os, os.path, pickle
import alc_AbsClasses
import alc_AnimClasses
from alc_AbsClasses import *
from alcurutypes import *
from alcdxtconv import *
from alchexdump import *
from alc_GeomClasses import *
from alc_Functions import *
from alcConvexHull import *
from alc_VolumeIsect import *
from alc_AlcScript import *
from alc_AnimClasses import *

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

################# Rework of the main Layer and Material Classes

class hsGMatState:
    StateIdx = \
    { \
        "kBlend" : 0x0, \
        "kClamp" : 0x1, \
        "kShade" : 0x2, \
        "kZ"     : 0x3, \
        "kMisc"  : 0x4  \
    } 

    hsGMatBlendFlags =  \
    { \
        "kBlendTest"                :        0x1, \
        "kBlendAlpha"               :        0x2, \
        "kBlendMult"                :        0x4, \
        "kBlendAdd"                 :        0x8, \
        "kBlendAddColorTimesAlpha"  :       0x10, \
        "kBlendAntiAlias"           :       0x20, \
        "kBlendDetail"              :       0x40, \
        "kBlendNoColor"             :       0x80, \
        "kBlendMADD"                :      0x100, \
        "kBlendDot3"                :      0x200, \
        "kBlendAddSigned"           :      0x400, \
        "kBlendAddSigned2X"         :      0x800, \
        "kBlendMask"                :      0xF5E, \
        "kBlendInvertAlpha"         :     0x1000, \
        "kBlendInvertColor"         :     0x2000, \
        "kBlendAlphaMult"           :     0x4000, \
        "kBlendAlphaAdd"            :     0x8000, \
        "kBlendNoVtxAlpha"          :    0x10000, \
        "kBlendNoTexColor"          :    0x20000, \
        "kBlendNoTexAlpha"          :    0x40000, \
        "kBlendInvertVtxAlpha"      :    0x80000, \
        "kBlendAlphaAlways"         :   0x100000, \
        "kBlendInvertFinalColor"    :   0x200000, \
        "kBlendInvertFinalAlpha"    :   0x400000, \
        "kBlendEnvBumpNext"         :   0x800000, \
        "kBlendSubtract"            :  0x1000000, \
        "kBlendRevSubtract"         :  0x2000000, \
        "kBlendAlphaTestHigh"       :  0x4000000  \
    }

    hsGMatClampFlags = \
    { \
        "kClampTextureU"    : 0x1, \
        "kClampTextureV"    : 0x2, \
        "kClampTexture"     : 0x3  \
    }

    hsGMatShadeFlags = \
    { \
        "kShadeSoftShadow"          :        0x1, \
        "kShadeNoProjectors"        :        0x2, \
        "kShadeEnvironMap"          :        0x4, \
        "kShadeVertexShade"         :       0x20, \
        "kShadeNoShade"             :       0x40, \
        "kShadeBlack"               :       0x40, \
        "kShadeSpecular"            :       0x80, \
        "kShadeNoFog"               :      0x100, \
        "kShadeWhite"               :      0x200, \
        "kShadeSpecularAlpha"       :      0x400, \
        "kShadeSpecularColor"       :      0x800, \
        "kShadeSpecularHighlight"   :     0x1000, \
        "kShadeVertColShade"        :     0x2000, \
        "kShadeInherit"             :     0x4000, \
        "kShadeIgnoreVtxIllum"      :     0x8000, \
        "kShadeEmissive"            :    0x10000, \
        "kShadeReallyNoFog"         :    0x20000  \
    }

    hsGMatZFlags = \
    { \
        "kZIncLayer"    :  0x1, \
        "kZClearZ"      :  0x4, \
        "kZNoZRead"     :  0x8, \
        "kZNoZWrite"    : 0x10, \
        "kZMask"        : 0x1C, \
        "kZLODBias"     : 0x20 \
    }

    hsGMatMiscFlags = \
    { \
        "kMiscWireFrame"            :        0x1, \
        "kMiscDrawMeshOutlines"     :        0x2, \
        "kMiscTwoSided"             :        0x4, \
        "kMiscDrawAsSplats"         :        0x8, \
        "kMiscAdjustPlane"          :       0x10, \
        "kMiscAdjustCylinder"       :       0x20, \
        "kMiscAdjustSphere"         :       0x40, \
        "kMiscAdjust"               :       0x70, \
        "kMiscTroubledLoner"        :       0x80, \
        "kMiscBindSkip"             :      0x100, \
        "kMiscBindMask"             :      0x200, \
        "kMiscBindNext"             :      0x400, \
        "kMiscLightMap"             :      0x800, \
        "kMiscUseReflectionXform"   :     0x1000, \
        "kMiscPerspProjection"      :     0x2000, \
        "kMiscOrthoProjection"      :     0x4000, \
        "kMiscProjection"           :     0x6000, \
        "kMiscRestartPassHere"      :     0x8000, \
        "kMiscBumpLayer"            :    0x10000, \
        "kMiscBumpDu"               :    0x20000, \
        "kMiscBumpDv"               :    0x40000, \
        "kMiscBumpDw"               :    0x80000, \
        "kMiscBumpChans"            :    0xE0000, \
        "kMiscNoShadowAlpha"        :   0x100000, \
        "kMiscUseRefractionXform"   :   0x200000, \
        "kMiscCam2Screen"           :   0x400000, \
        "kAllMiscFlags"             :       0xFF  \
    }
    
    def __init__(self):
        self.fBlendFlags = 0x00 
        self.fClampFlags = 0x00 
        self.fShadeFlags = 0x00 
        self.fZFlags     = 0x00 
        self.fMiscFlags  = 0x00 

    def read(self,buf):
        self.fBlendFlags = buf.Read32()
        self.fClampFlags = buf.Read32()
        self.fShadeFlags = buf.Read32()
        self.fZFlags     = buf.Read32()
        self.fMiscFlags  = buf.Read32()
        pass

    def write(self,buf):
        buf.Write32(self.fBlendFlags)
        buf.Write32(self.fClampFlags)
        buf.Write32(self.fShadeFlags)
        buf.Write32(self.fZFlags)
        buf.Write32(self.fMiscFlags)
        pass

class hsGMaterial(plSynchedObject):         # Type 0x07

    hsGCompFlags =  \
    { \
        "kCompShaded"            :    0x1, \
        "kCompEnvironMap"        :    0x2, \
        "kCompProjectOnto"       :    0x4, \
        "kCompSoftShadow"        :    0x8, \
        "kCompSpecular"          :   0x10, \
        "kCompTwoSided"          :   0x20, \
        "kCompDrawAsSplats"      :   0x40, \
        "kCompAdjusted"          :   0x80, \
        "kCompNoSoftShadow"      :  0x100, \
        "kCompDynamic"           :  0x200, \
        "kCompDecal"             :  0x400, \
#OBSOLETE        "kCompIsEmissive"        :  0x800, \
        "kCompIsLightMapped"     : 0x1000, \
        "kCompNeedsBlendChannel" : 0x2000  \
    }

    UpdateFlags =  \
    { \
        "kUpdateAgain" : 0x1 \
    }

    def __init__(self,parent,name="unnamed",type=0x0007):
        plSynchedObject.__init__(self,parent,name,type)
        
        self.fLOD = 0# Int32 
        self.fLayersCount = 0
        self.fLayers = []   # hsTArray<plLayerInterface> 
        self.fPiggyBacksCount = 0
        self.fPiggyBacks = [] # hsTArray<plLayerInterface> 
        self.fCompFlags = 0 # UInt32 
        self.fLoadFlags = 0 # UInt32 
        #self.fLastUpdateTime# Single
        self.fZOffset = 0
        self.fCriteria = 0
        self.fRenderLevel = plRenderLevel()
        self.blendermaterial = None

    def _Find(page,name):
        return page.find(0x0007,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0007,name,1)
    FindCreate = staticmethod(_FindCreate)



    def write(self,stream):
        plSynchedObject.write(self,stream)

        stream.Write32(self.fLoadFlags);
        stream.Write32(self.fCompFlags);
        stream.Write32(len(self.fLayers));
        stream.Write32(len(self.fPiggyBacks));
        
        for key in self.fLayers:
            key.update(self.Key)
            key.write(stream)

        for key in self.fPiggyBacks:
            key.update(self.Key)
            key.write(stream)

    def read(self,stream):
        plSynchedObject.read(self,stream)

        self.fLoadFlags = stream.Read32();
        self.fCompFlags = stream.Read32();
        
        self.fLayersCount = stream.Read32();
        self.fPiggyBacksCount = stream.Read32();

        for i in range(self.fLayersCount):
            key = UruObjectRef(self.getVersion())
            key.read(stream)
            self.fLayers.append(key)

        for i in range(self.fPiggyBacksCount):
            key = UruObjectRef(self.getVersion())
            key.read(stream)
            self.fLayers.append(key)

    ###################################
    ##                               ##
    ##      Interface Functions      ##
    ##                               ##
    ###################################
    def ToBlenderMat(self,obj):
        if self.blendermaterial != None:
            return self.blendermaterial
        print "    [Material %s]"%(str(self.Key.name))


        resmanager=self.getResManager()
        texprp=resmanager.findPrp("Textures")
        root=self.getRoot()
        
        # create the material to work on:
        name = str(self.Key.name)
        self.blendermaterial=Blender.Material.New(name)
        mat=self.blendermaterial
        matmode=mat.getMode()
        mat.setMode(matmode)

        texid = 0
        
        for layerref in self.fLayers:
            layer = root.findref(layerref)
            if layer != None:
                # -- Retrieve from layer some info for the blender material
                ambientCol  = layer.data.fPreshadeColor
                diffuseCol  = layer.data.fRuntimeColor
                emitCol     = layer.data.fAmbientColor
                specCol     = layer.data.fSpecularColor
                mat.setAlpha(diffuseCol.a)
                mat.setRGBCol([diffuseCol.r,diffuseCol.g,diffuseCol.b])
                mat.setSpecCol([specCol.r,specCol.g,specCol.b])

                try:
                    emitfactor = emitCol.r / diffuseCol.r
                except:
                    emitfactor = 0.0
                mat.setEmit(emitfactor)
                
                try:
                    ambfactor = ambientCol.r/ diffuseCol.r
                except:
                    ambfactor = 0.5
                mat.setAmb(ambfactor)
                
                if layer.data.fState.fShadeFlags | hsGMatState.hsGMatShadeFlags["kShadeNoFog"]:
                    mat.mode |= Blender.Material.Modes['NOMIST']
                
                # -- Retrieve layer specific date into textures
                bitmap = None
                if not layer.data.fTexture.isNull(): # if a texture image is associated Retrieve the layer from that
                    
                    # try to find it on the current page first....
                    bitmap = root.findref(layer.data.fTexture)
                    # and on the texture page if it isn't there..
                    if bitmap is None and not texprp is None:        
                        bitmap = texprp.findref(layer.data.fTexture)    
    
                if bitmap != None:
                    tex = bitmap.data.ToBlenderTex(str(layer.data.Key.name))
                else:
                    tex = Blender.Texture.New(str(layer.data.Key.name))
                    tex.setType('None')
                    
                if tex != None and texid < 10:
                    mat.setTexture(texid,tex,Blender.Texture.TexCo["UV"],Blender.Texture.MapTo["COL"])
                    mtexlist = mat.getTextures()
                    mtex = mtexlist[texid]
                    
                    if mtex != None:
                        layer.data.ToBlenderMTex(mtex,obj)
                    
                    texid += 1
        
        return mat


    def FromBlenderMat(self,mat,obj):
        print "  [Material %s]"%(str(self.Key.name))
        # mat is the material to convert
        # obj is the object the material links to - and only used to get the UV Maps
        self.blendermaterial=mat
        
        name = str(self.Key.name)
        resmanager=self.getResManager()
        root=self.getRoot()
        mesh = obj.getData(False,True)

        # reset the flags to 00
        self.fFlags=0x00
                
        # Loop through the MTex layers of Blender, and parse every one of them as a layer.
        if (mat): #avoid crashes if we acidentally ref this function without parameters

#            if(obj.type == "Mesh" and (obj.data.mode & Blender.Mesh.Modes.TWOSIDED) > 0):
 #               self.fCompFlags |= hsGMaterial.hsGCompFlags["kCompTwoSided"] 

            if mat.getSpec() > 0.0:
                self.fCompFlags |= hsGMaterial.hsGCompFlags["kCompSpecular"] 
                
            if name.lower().find("decal") != -1:
                self.fCompFlags |= hsGMaterial.hsGCompFlags["kCompDecal"] 


            mtex_list = mat.getTextures()
            
            layerlist = []
            for mtex in mtex_list:
                if(mtex != None):
                    if (mtex.tex.type == Blender.Texture.Types.BLEND or
                        mtex.tex.type == Blender.Texture.Types.NONE or
                        mtex.tex.type == Blender.Texture.Types.IMAGE or
                        mtex.tex.type == Blender.Texture.Types.ENVMAP):

                        # we hit a problem when two textures are shared, because the mtex is different per material.
                        # because of this. we'll prefix the material name, before the layer name
                        ipo = mat.ipo
                        channel = list(mtex_list).index(mtex)
                        anim = False
                        
                        if ipo != None:
                            ipo.channel = channel
                            if(len(ipo.curves) > 0):
                                anim = True
                        
                        layer = root.find(0x06,mat.name + "-" + mtex.tex.name,1)
                        layerlist.append({"layer":layer,"mtex":mtex,"stencil":mtex.stencil,"anim":anim})

            i = 0
            while i < len(layerlist):
                layer_info = layerlist[i]
            
                if not layer_info["stencil"]:
                    layer = layer_info["layer"]
                    mtex = layer_info["mtex"]
                    if(not layer.isProcessed):
                        layer.data.FromBlenderMTex(mtex,obj,mat)
                        layer.data.FromBlenderMat(obj,mat)
                        layer.isProcessed = 1
                    self.fLayers.append(layer.data.getRef())
                    i += 1
                else:
                    if i < len(layerlist) - 1: # if it's not the last one
                        # Append the next layer first, and say that it has a stencil
                        boundlayer_info = layerlist[i+1]
                        boundlayer = boundlayer_info["layer"]
                        boundmtex = boundlayer_info["mtex"]
                        if(not boundlayer.isProcessed):
                            boundlayer.data.FromBlenderMat(obj,mat)
                            boundlayer.data.FromBlenderMTex(boundmtex,obj,mat,False,True)
                            boundlayer.isProcessed = 1
                        self.fLayers.append(boundlayer.data.getRef())
 
                        # append the stencil layer after that...
                        layer = layer_info["layer"]
                        mtex = layer_info["mtex"]
                        if(not layer.isProcessed):
                            layer.data.FromBlenderMTex(mtex,obj,mat,True,False)
#                            layer.data.FromBlenderMat(obj,mat)
                            layer.isProcessed = 1
                        self.fLayers.append(layer.data.getRef())
                        self.fCompFlags |= hsGMaterial.hsGCompFlags["kCompNeedsBlendChannel"] 
                    
                        # And ofcourse increase by 2 instead of one...
                        i += 2
                    else:
                        # just ignore it...
                        i += 1
                
                if layer_info["anim"]:
                    animlayer = root.find(0x0043,layer.data.getName() + "_LayerAnim_",1)
                    animlayer.data.FromBlender(obj,mat,mtex,chan)
                    animlayer.data.fUnderlay = layer.data.getRef()
                    self.fLayers.append(animlayer.data.getRef())

            # Add a default layer if we didn't get and layers from the mtexes
            if(len(self.fLayers) == 0):
                #find or create this new layer:
                layer=root.find(0x06,name + "/" + "AutoLayer",1)
                
                # now see if we have a uvmapped texture on the object, and add this texture if needed
                if(obj):
                    # retrieve the corresponding mesh
                    meshName = obj.data.name
                    mesh = Mesh.Get(meshName)
                    
                    texture_img=None
                    for f in mesh.faces:
                        if mesh.faceUV and f.image!=None:
                            texture_img=f.image
                            break
                    if(texture_img != None):
                        #add the texture if it is there
                        layer.data.FromUvTex(texture_img,obj)
                    layer.data.FromBlenderMat(obj,mat)    
                
                self.fLayers.append(layer.data.getRef())
    

            self.fZOffset = int(mat.zOffset)

            # If we have two vertex color layers, the 2nd is used as alpha layer - if we have vertex alpha,
            # we need to have the renderlevel set to blending
            if len(mesh.getColorLayerNames()) > 1:
                if self.fZOffset < 1:
                    self.fZOffset = 1


                                    
    def layerCount(self):
        return len(self.fLayers)

    def ZBias(self):
        root = self.getRoot()
        UsesAlpha = True
        for layerref in self.fLayers:
            layer = root.findref(layerref)
            if(layer.type == 0x0043):
                UsesAlpha = False
            else:
                UsesAlpha = (UsesAlpha and layer.data.UsesAlpha)
        
#            if layer.data.UsesAlpha:
#                print "   DEBUG: Layer \"%s\" uses Alpha"%(layer.data.Key.name)
#            else:
#                print "   DEBUG: Layer \"%s\" is Opaque"%(layer.data.Key.name)

#        if UsesAlpha:
#            print "   DEBUG: Result - Material has Alpha"
#        else:
#            print "   DEBUG: Result - Material is Opaque"
        
        ZBias = int(self.fZOffset)
        if UsesAlpha and ZBias == 0:
            ZBias += 1
        
        return ZBias
        
    def Criteria(self):
        return self.fCriteria

    def TexLayerCount(self):
        root=self.getRoot()

        # count the layers that actually have a texture set.
        count = 0
        for layerref in self.fLayers:
            layer = root.findref(layerref)
            if(layer.data.fHasTexture != 0):
                count += 1
        return count

    def getBlenderTextures(self):
        return self.blendertextures
    
    
    def export_mat(self,mat,obj):
        self.FromBlenderMat(mat,obj)



class plLayerInterface(plSynchedObject):     # Type 0x41 (uru)

    plUVWSrcModifiers = \
    { \
        "kUVWPassThru"  :        0x0, \
        "kUVWNormal"    :    0x10000, \
        "kUVWPosition"  :    0x20000, \
        "kUVWReflect"   :    0x30000, \
        "kUVWIdxMask"   : 0x0000FFFF  \
    }

    def __init__(self,parent,name="unnamed",type=None):
        plSynchedObject.__init__(self,parent,name,type)

        self.fUnderlay = UruObjectRef(self.getVersion()) 
        self.fOverLay = UruObjectRef(self.getVersion())  
        self.fOwnedChannels = 0x00  
        self.fPassThruChannels = 0x00  
        self.fTransform = hsMatrix44()
        self.fPreshadeColor = RGBA(0.5,0.5,0.5,1.0,type=1) # Grey
        self.fRuntimeColor = RGBA(0.5,0.5,0.5,1.0,type=1) # Grey
        self.fAmbientColor = RGBA(0.0,0.0,0.0,0.0,type=1) # Clear
        self.fOpacity = 1.0 
        self.fTexture = UruObjectRef(self.getVersion())  
        self.fState = hsGMatState()
        self.fUVWSrc = 0 
        self.fLODBias =  -1.0  
        self.fSpecularColor = RGBA(0.0,0.0,0.0,1.0,type=1) # Black
        self.fSpecularPower = 1.0 
        self.fVertexShader = UruObjectRef(self.getVersion()) 
        self.fPixelShader = UruObjectRef(self.getVersion())  
        self.fBumpEnvXfm = hsMatrix44()

    def read(self,buf):
        plSynchedObject.read(self,buf)
        self.fUnderlay.read(buf)
    
    def write(self,buf):
        plSynchedObject.write(self,buf)
        self.fUnderlay.write(buf)

class plLayer(plLayerInterface):             # Type 0x06

    def __init__(self,parent,name="unnamed",type=0x0006):
        plLayerInterface.__init__(self,parent,name,type)

        self.fOwnedChannels = 0x3FFF;
        self.fPreshadeColor = RGBA(0.5,0.5,0.5,1.0,type=1) # Grey
        self.fRuntimeColor = RGBA(0.5,0.5,0.5,1.0,type=1) # Grey
        self.fAmbientColor = RGBA(0.0,0.0,0.0,0.0,type=1) # Clear
        self.fSpecularColor = RGBA(0.0,0.0,0.0,1.0,type=1) # Black
        
        self.fTransform = hsMatrix44()
        self.fOpacity = 1.0
        self.fState = hsGMatState()
        self.fUVWSrc = 0
        self.fLODBias = -1.0
        self.fSpecularPower = 1.0
        self.fTexture = UruObjectRef(self.getVersion())
        self.fVertexShader = UruObjectRef(self.getVersion())
        self.fPixelShader = UruObjectRef(self.getVersion())
        self.fBumpEnvXfm = hsMatrix44()
        
        self.fRenderLevel = plRenderLevel() #used to determine RenderLevel
        self.fZBias = 0

        self.fHasTexture = 0
        self.InitToDefault()

    def _Find(page,name):
        return page.find(0x0006,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0006,name,1)
    FindCreate = staticmethod(_FindCreate)


    def InitToDefault(self):
        fState = hsGMatState();
        self.fTexture = UruObjectRef(self.getVersion())
        self.fRuntimeColor = RGBA(0.5, 0.5, 0.5, 1.0)  # Grey
        self.fPreshadeColor = RGBA(0.5, 0.5, 0.5, 1.0) # Grey
        self.fAmbientColor = RGBA(0.0, 0.0, 0.0, 0.0)        # Clear
        self.fOpacity = 1.0
        self.fTransform = hsMatrix44()
        self.fUVWSrc = 0
        self.fLODBias = -1.0
        self.fSpecularColor = RGBA(0.0, 0.0, 0.0, 1.0)       # Black
        self.fSpecularPower = 1.0
        self.fVertexShader = UruObjectRef(self.getVersion()) 
        self.fPixelShader = UruObjectRef(self.getVersion())
        self.fBumpEnvXfm = hsMatrix44()

        self.fRenderLevel = plRenderLevel()
        self.UsesAlpha = False

        self.fHasTexture = 0

    def read(self,stream):
        plLayerInterface.read(self,stream)
        self.fState.read(stream)
        self.fTransform.read(stream)
        self.fPreshadeColor.read(stream)    #old: self.ambient
        self.fRuntimeColor.read(stream)     #old: self.diffuse
        self.fAmbientColor.read(stream)     #old: self.emissive
        self.fSpecularColor.read(stream)    #old: self.specular
        self.fUVWSrc = stream.Read32()
        self.fOpacity = stream.ReadFloat()
        self.fLODBias = stream.ReadFloat()
        self.fSpecularPower = stream.ReadFloat()
        self.fTexture.read(stream)
        self.fVertexShader.read(stream)
        self.fPixelShader.read(stream)
        self.fBumpEnvXfm.read(stream)

    def write(self,stream):
        plLayerInterface.write(self,stream)
        self.fState.write(stream)
        self.fTransform.write(stream)
        self.fPreshadeColor.write(stream)   #old: self.ambient
        self.fRuntimeColor.write(stream)    #old: self.diffuse
        self.fAmbientColor.write(stream)    #old: self.emissive
        self.fSpecularColor.write(stream)   #old: self.specular
        stream.Write32(self.fUVWSrc)
        stream.WriteFloat(self.fOpacity)
        stream.WriteFloat(self.fLODBias)
        stream.WriteFloat(self.fSpecularPower)
        self.fTexture.write(stream)
        self.fVertexShader.write(stream)
        self.fPixelShader.write(stream)
        self.fBumpEnvXfm.write(stream)

    ###################################
    ##                               ##
    ##      Interface Functions      ##
    ##                               ##
    ###################################
        
    def ToBlenderMTex(self,mtex,obj):
        print "     [Layer %s]"%(str(self.Key.name))
        mtex.colfac = self.fOpacity 
        if self.fState.fBlendFlags & hsGMatState.hsGMatBlendFlags["kBlendInvertColor"]: 
           mtex.neg = True

        # not working in blender 2.45, perhaps will do in a later version
        if self.fState.fMiscFlags & hsGMatState.hsGMatMiscFlags["kMiscTwoSided"]:
            mode = obj.data.getMode()
            mode |= Blender.Mesh.Modes.TWOSIDED
            obj.data.setMode()
        else:
            mode = obj.data.getMode()
            mode &= Blender.Mesh.Modes.TWOSIDED
            obj.data.setMode()

        pass

    def FromBlenderMTex(self,mtex,obj,mat,stencil=False,hasstencil=False):
        print "   [Layer %s]"%(str(self.Key.name))
        #prp is for current prp file... (though that should be obtainable from self.parent.prp)
        resmanager=self.getResManager()
        root=self.getRoot()

        mesh = obj.getData(False,True)

        exportTexturesToPrp = alcconfig.export_textures_to_page_prp
        try:
            p = obj.getProperty("ignorePPT")
            if (bool(p.getData()) == True):
                exportTexturesToPrp = 0
        except:
            pass

        # determine what the texture prp must be
        if exportTexturesToPrp:
            texprp=root
        else:
            texprp=resmanager.findPrp("Textures")
        if texprp==None:
            raise "Textures PRP file not found"

        mipmap = None
        qmap = None

        if(mtex):

            # First Determine the UVW Source....
            BlenderUVLayers = mesh.getUVLayerNames()

            UVLayers = {}
            
            # Build up a nice map here....
            i = 0
            for name in BlenderUVLayers:
                UVLayers[name] = i
                i += 1

            Use_Sticky = False
            # Loop through Layers To see which coorinate systems are used.
            for _mtex in mat.getTextures():
                if not _mtex is None:
                    if _mtex.texco == Blender.Texture.TexCo["STICK"] and mesh.vertexUV:
                        Use_Sticky = True
            
            UVSticky = 0 # Setting Sticky gives you 1st uv layer if no Sticky Coords set...
            if Use_Sticky:
                UVSticky = len(UVLayers)
                
            # Check out current mapping
            if mtex.texco == Blender.Texture.TexCo["STICK"]:
                print "    -> Using sticky mapping"
                self.fUVWSrc = UVSticky
            elif mtex.texco == Blender.Texture.TexCo["UV"]:
                try:
                    print "    -> Using UV map '%s'"%(mtex.uvlayer)
                    self.fUVWSrc = UVLayers[mtex.uvlayer]
                except:
                    print "    -> Err, Using first UV map"
                    self.fUVWSrc = 0
            else:
                print "    -> Using default first UV map"
                # Other mappings will make the map default to first uv map
                self.fUVWSrc = 0
            
        
            # process the image
            tex = mtex.tex
            
            #mtex type ENVMAP
            if(tex.type == Blender.Texture.Types.ENVMAP):
                
                # check 
                if(tex.stype != Blender.Texture.STypes.ENV_LOAD or tex.image == None):
                    raise "ERROR: Cannot set Environment map from static/anim render. Please render your EnvMap, save it, and then set the EnvMap to load your saved image!"
                
                #find or create the qmap

                mipmapinfo = blMipMapInfo()
                mipmapinfo.fName = tex.image.getName()
                mipmapinfo.fMipMaps = True
                mipmapinfo.fGauss = True
                mipmapinfo.fResize = True

                qmap = plCubicEnvironMap.Export(root,tex.image.getName(),tex.image,mipmapinfo,exportTexturesToPrp)

                self.fTexture = qmap.data.getRef()
                self.fHasTexture = 1
                
                # set default settings for qmaps:
                # self.fState.fBlendFlags |= hsGMatState.hsGMatBlendFlags["kBlendAlpha"]
                self.fState.fClampFlags |= 0 # | hsGMatState.hsGMatClampFlags[""]
                self.fState.fShadeFlags |= hsGMatState.hsGMatShadeFlags["kShadeEnvironMap"]
                self.fState.fZFlags     |= 0 # | hsGMatState.hsGMatZFlags[""]
                self.fState.fMiscFlags  |= ( hsGMatState.hsGMatMiscFlags["kMiscUseReflectionXform"]
                                            | hsGMatState.hsGMatMiscFlags["kMiscRestartPassHere"] 
                                            )
                
                self.fUVWSrc            |= plLayerInterface.plUVWSrcModifiers["kUVWReflect"]
    
                # set the blendflags for this layer to the cubicmap flags
                #self.fRenderLevel = plRenderLevel(plRenderLevel.MajorLevel["kDefRendMajorLevel"] | plRenderLevel.MajorLevel["kBlendRendMajorLevel"], 
                #                                    plRenderLevel.MinorLevel["kDefRendMinorLevel"])
                self.UsesAlpha = True
                
                pass
            #mtex type IMAGE
            elif(tex.type == Blender.Texture.Types.IMAGE):
                # find or create the mipmap
                
                if(tex.image):

                    mipmapinfo = blMipMapInfo()
                    mipmapinfo.export_tex(tex)
                    
                    if stencil and (not Blender.Texture.ImageFlags["USEALPHA"]):
                        mipmapinfo.fCalcAlpha = True
                    
                    mipmap=plMipMap.Export(root,tex.image.getName(),tex.image,mipmapinfo,exportTexturesToPrp)
                                        
                    self.fTexture = mipmap.data.getRef()
                    self.fHasTexture = 1
                    
                    # set the blendflags for this layer to the alphaflags, if it has alhpa
                    if (mipmap.data.FullAlpha or mipmap.data.OnOffAlpha):
                        self.UsesAlpha = True
                
                    if tex.extend == Blender.Texture.ExtendModes["CLIP"]:
                        self.fState.fClampFlags |= hsGMatState.hsGMatClampFlags["kClampTexture"]
                
                pass
            #mtex type BLEND
            #Builds a linear AlphaBlend
            elif(tex.type == Blender.Texture.Types.BLEND):
                if mtex.tex.stype == Blender.Texture.STypes.BLN_LIN:
                    # now create a blend, depending on whether it is horizontal or vertical:
                    if(tex.flags & Blender.Texture.Flags.FLIPBLEND > 0):
                        #Vertical blend
                        blendname = "ALPHA_BLEND_FILTER_V_LIN_64x64"
                        
                        blenddata = cStringIO.StringIO()
                        blendwidth = 64
                        blendheight = 64
                        
                        for y in range(blendheight,0,-1):
                            alpha = 255 *(float(y)/blendheight)
                            for x in range(0,blendwidth):
                                blenddata.write(struct.pack("BBBB",255,255,255,alpha))
                    else:
                        #Horizontal blend
                        blendname = "ALPHA_BLEND_FILTER_U_LIN_64x64"
            
                        blenddata = cStringIO.StringIO()
                        blendwidth = 64
                        blendheight = 64
                        
                        for y in range(blendheight,0,-1):
                            for x in range(0,blendwidth):
                                alpha = 255 * (float(x)/blendwidth)
                                blenddata.write(struct.pack("BBBB",255,255,255,alpha))

                elif mtex.tex.stype == Blender.Texture.STypes.BLN_QUAD:
                    # now create a blend, depending on whether it is horizontal or vertical:
                    if(tex.flags & Blender.Texture.Flags.FLIPBLEND > 0):
                        #Vertical blend
                        blendname = "ALPHA_BLEND_FILTER_V_QUAD_64x64"
                        
                        blenddata = cStringIO.StringIO()
                        blendwidth = 4
                        blendheight = 64
                        
                        for y in range(blendheight,0,-1):
                            alpha = 255 * math.pow(float(y)/blendheight,2)
                            for x in range(0,blendwidth):
                                blenddata.write(struct.pack("BBBB",255,255,255,alpha))
                    else:
                        #Horizontal blend
                        blendname = "ALPHA_BLEND_FILTER_U_QUAD_64x64"
            
                        blenddata = cStringIO.StringIO()
                        blendwidth = 64
                        blendheight = 4
                        
                        for y in range(blendheight,0,-1):
                            for x in range(0,blendwidth):
                                alpha = 255 * math.pow(float(x)/blendwidth,2)
                                blenddata.write(struct.pack("BBBB",255,255,255,alpha))

                elif mtex.tex.stype == Blender.Texture.STypes.BLN_EASE:
                    # now create a blend, depending on whether it is horizontal or vertical:
                    if(tex.flags & Blender.Texture.Flags.FLIPBLEND > 0):
                        #Vertical blend
                        blendname = "ALPHA_BLEND_FILTER_V_EASE_64x64"
                        
                        blenddata = cStringIO.StringIO()
                        blendwidth = 4
                        blendheight = 64
                        
                        for y in range(blendheight,0,-1):
                            alpha = 255 * (1 - (0.5 + (math.cos((float(y)/blendheight) * math.pi) * 0.5)))
                            for x in range(0,blendwidth):
                                blenddata.write(struct.pack("BBBB",255,255,255,alpha))
                    else:
                        #Horizontal blend
                        blendname = "ALPHA_BLEND_FILTER_U_EASE_64x64"
            
                        blenddata = cStringIO.StringIO()
                        blendwidth = 64
                        blendheight = 4
                        
                        for y in range(blendheight,0,-1):
                            for x in range(0,blendwidth):
                                alpha = 255 * (1 - (0.5 + (math.cos( (float(x)/blendwidth) * math.pi) * 0.5)))
                                blenddata.write(struct.pack("BBBB",255,255,255,alpha))

                elif mtex.tex.stype == Blender.Texture.STypes.BLN_DIAG:
                    # Prepare the data for this object....
                    blendname = "ALPHA_BLEND_FILTER_DIAG_64x64"
   
                    blenddata = cStringIO.StringIO()
                    blendwidth = 64
                    blendheight = 64
                
                    for y in range(blendheight,0,-1):
                        for x in range(0,blendwidth):
                            dist = math.sqrt(math.pow(x ,2) + math.pow(y,2))
                            alpha = 255 *(dist / math.sqrt(math.pow(blendwidth,2) + math.pow(blendheight,2)))
                            
                            blenddata.write(struct.pack("BBBB",255,255,255,alpha))

                elif mtex.tex.stype == Blender.Texture.STypes.BLN_SPHERE:
                    # Prepare the data for this object....
                    blendname = "ALPHA_BLEND_FILTER_SPHERE_64x64"
                    
                    blenddata = cStringIO.StringIO()
                    blendwidth = 64
                    blendheight = 64
                
                    for y in range(blendheight,0,-1):
                        for x in range(0,blendwidth):
                            dist = math.sqrt(math.pow(x - (blendwidth/2),2) + math.pow(y - (blendheight/2),2))
                            alpha = 255 *(math.cos((dist / (blendwidth/2) * 0.5 * math.pi )))
                            if alpha < 0 or dist > (blendwidth/2):
                                alpha = 0
                            elif alpha > 255:
                                alpha = 255
                            blenddata.write(struct.pack("BBBB",255,255,255,alpha))

                elif mtex.tex.stype == Blender.Texture.STypes.BLN_HALO:
                    # Prepare the data for this object....
                    blendname = "ALPHA_BLEND_FILTER_HALO_64x64"
                    
                    blenddata = cStringIO.StringIO()
                    blendwidth = 64
                    blendheight = 64
                
                    for y in range(blendheight,0,-1):
                        for x in range(0,blendwidth):
                            dist = math.sqrt( math.pow(x - (blendwidth/2),2) + math.pow(y - (blendheight/2),2) ) 
                            alpha = 255 *(0.5 + (0.5 * math.cos((dist / (blendwidth/2) * math.pi ))))
                            if alpha < 0 or dist > (blendwidth/2):
                                alpha = 0
                            elif alpha > 255:
                                alpha = 255
                            blenddata.write(struct.pack("BBBB",255,255,255,alpha))

                else: ## RADIAL TYPE
                    #
                    # Prepare the data for this object....
                    if(tex.flags & Blender.Texture.Flags.FLIPBLEND > 0):
                        blendname = "ALPHA_BLEND_FILTER_V_RADIAL_64x64"
                    else:
                        blendname = "ALPHA_BLEND_FILTER_U_RADIAL_64x64"
                    
                    blenddata = cStringIO.StringIO()
                    blendwidth = 64
                    blendheight = 64
                
                    for y in range(blendheight,0,-1):
                        for x in range(0,blendwidth):
                            if(tex.flags & Blender.Texture.Flags.FLIPBLEND > 0): 
                                rely = x - (blendwidth/2)
                                relx = y - (blendheight/2)
                            else:
                                relx = x - (blendwidth/2)
                                rely = y - (blendheight/2)
                            
                            angle = math.atan2(rely,relx) + math.pi
                                
                            while angle < 0:
                                angle += 2* math.pi
                            
                            while angle > (2*math.pi):
                                angle -= 2* math.pi
                            
                            alpha = 255 *(angle/(2*math.pi))
                            if alpha < 0:
                                alpha = 0
                            blenddata.write(struct.pack("BBBB",255,255,255,alpha))
                
                # Set clipping (clamping)
                self.fState.fClampFlags |= hsGMatState.hsGMatClampFlags["kClampTexture"]

                
                mipmapinfo = blMipMapInfo()
                mipmapinfo.fName = blendname
                mipmapinfo.fMipMaps = False
                mipmapinfo.fGauss = False
                mipmapinfo.fCompressionType = plBitmap.Compression["kDirectXCompression"]
                mipmapinfo.fBitmapInfo.fDirectXInfo.fCompressionType = plBitmap.CompressionType["kDXT5"]
                
                mipmap = plMipMap.Export_Raw(root,blendname,blenddata,blendwidth,blendheight,mipmapinfo,exportTexturesToPrp)
                
                # and link the mipmap to the layer
                self.fTexture = mipmap.data.getRef()
                self.fHasTexture = 1
                # alphablend layers do not affect blendflags (as far as we know now)
                
                
            elif(tex.type == Blender.Texture.Types.NONE):
                pass # don't do anything

            
            # now process additional mtex settings


            if not stencil:
                # find the texture object, so we can get some values from it
                
                # first make a calculation of the uv transformation matrix.
                uvmobj = Blender.Object.New ('Empty')
                
                trickscale = mtex.size[2]
                # now set the scale (and rotation) to the object
                uvmobj.SizeX = mtex.size[0] * trickscale
                uvmobj.SizeY = mtex.size[1] * trickscale
                uvmobj.LocX = mtex.ofs[0]
                uvmobj.LocY = mtex.ofs[1]
                uvm=getMatrix(uvmobj)
                uvm.transpose()
                self.fTransform.set(uvm)
    
                self.fOpacity = mtex.colfac # factor how texture blends with color used as alpha blend value
    
                # See if any faces are set to double sided...
                for mface in mesh.faces:
                    if mface.uv and mface.mode & Blender.Mesh.FaceModes["TWOSIDE"]:
                        self.fState.fMiscFlags  |= hsGMatState.hsGMatMiscFlags["kMiscTwoSided"] 
                        break
                
                                                
                if(mtex.blendmode == Blender.Texture.BlendModes.ADD): 
                    # self.fState.fBlendFlags |= ( hsGMatState.hsGMatBlendFlags["kBlendAdd"])
                    self.fState.fBlendFlags |= hsGMatState.hsGMatBlendFlags["kBlendAddColorTimesAlpha"] # This is better and more intuitive
                    if mtex.mtAlpha != 0:
                        self.fState.fBlendFlags |= hsGMatState.hsGMatBlendFlags["kBlendAlphaAdd"]

                elif(mtex.blendmode == Blender.Texture.BlendModes.MULTIPLY):
                    self.fState.fBlendFlags |= hsGMatState.hsGMatBlendFlags["kBlendMult"]
                    if mtex.mtAlpha != 0:
                        self.fState.fBlendFlags |= hsGMatState.hsGMatBlendFlags["kBlendAlphaMult"]
                                                
                elif(mtex.blendmode == Blender.Texture.BlendModes.SUBTRACT):
                    self.fState.fBlendFlags |= hsGMatState.hsGMatBlendFlags["kBlendSubtract"]

                else: #(mtex.blendmode == Blender.Texture.BlendModes.MIX):
                    # Enable Normal Alpha Blending ONLY if the other alpha blend flags are not enabled
                    self.fState.fBlendFlags |= hsGMatState.hsGMatBlendFlags["kBlendAlpha"]
                if(mtex.neg): # set the negate colors flag if it is so required
                    self.fState.fBlendFlags |= hsGMatState.hsGMatBlendFlags["kBlendInvertColor"]

                    
        if stencil:
            # now set the various layer properties specific to alphablendmaps
            self.fState.fBlendFlags |= ( hsGMatState.hsGMatBlendFlags["kBlendAlpha"]
                                        | hsGMatState.hsGMatBlendFlags["kBlendAlphaMult"]
                                        | hsGMatState.hsGMatBlendFlags["kBlendNoTexColor"]
                                        )
            
            self.fState.fZFlags     |= hsGMatState.hsGMatZFlags["kZNoZWrite"]
            self.fState.fMiscFlags  |= 0 # | hsGMatState.hsGMatMiscFlags[""] 
            self.fAmbientColor = RGBA(1.0,1.0,1.0,1.0)
            
        if hasstencil:
            self.fState.fMiscFlags  |= hsGMatState.hsGMatMiscFlags["kMiscBindNext"]  | hsGMatState.hsGMatMiscFlags["kMiscRestartPassHere"] 
        
        if stencil or hasstencil:
            # a stencil joins two layers into one that has alpha....
            self.UsesAlpha = True
    
            
            

    def FromBlenderMat(self,obj,mat):
        # Now Copy Settings from the material...
        mesh = obj.getData(False,True)
        
        # get the blender basic colors and options
        matR,matG,matB = mat.getRGBCol() #color triplet (map to diffuse)
        matA = mat.getAlpha()
        
        specR,specG,specB = mat.getSpecCol() #specular color triplet (map to specular)
        specR = specR * mat.getSpec()/2
        specG = specG * mat.getSpec()/2
        specB = specB * mat.getSpec()/2
        specCol=RGBA(specR,specG,specB,matA,type=1)

        mirR,mirG,mirB = mat.getMirCol()

        emitfactor = mat.getEmit()
        #calculat the emissive colors
        emitR = matR * emitfactor
        emitG = matG * emitfactor
        emitB = matB * emitfactor
        emitCol=RGBA(emitR,emitG,emitB,1,type=1)
  

        
        diffuseCol=RGBA(matR,matG,matB,matA,type=1)
        

        # calculate the ambient colors
        ambfactor = mat.getAmb()        
        ambR = matR * ambfactor
        ambG = matG * ambfactor
        ambB = matB * ambfactor
        ambientCol = RGBA(ambR,ambG,ambB,1,type=1)

        # Map to the layer colors
        self.fPreshadeColor = ambientCol
        self.fRuntimeColor = diffuseCol
        self.fAmbientColor = emitCol
        self.fSpecularColor = specCol

        
        
        if mat.getMode() & Blender.Material.Modes['NOMIST']:
            self.fState.fShadeFlags |= hsGMatState.hsGMatShadeFlags["kShadeNoFog"]
            self.fState.fShadeFlags |= hsGMatState.hsGMatShadeFlags["kShadeReallyNoFog"]
                    
        if mat.getMode() & Blender.Material.Modes['ZTRANSP']:
            self.fState.fZFlags |= hsGMatState.hsGMatZFlags["kZNoZWrite"]
            
        if mat.getSpec() > 0.0:
            self.fState.fShadeFlags |= hsGMatState.hsGMatShadeFlags["kShadeSpecular"]
            self.fState.fShadeFlags |= hsGMatState.hsGMatShadeFlags["kShadeSpecularAlpha"]
            self.fState.fShadeFlags |= hsGMatState.hsGMatShadeFlags["kShadeSpecularColor"]
            self.fState.fShadeFlags |= hsGMatState.hsGMatShadeFlags["kShadeSpecularHighlight"]
            self.fSpecularPower = mat.getHardness()
            
        # If we have two vertex color layers, the 2nd is used as alpha layer - if we have vertex alpha,
        # we need to have the alpha blending flag set, and we need to have
        if len(mesh.getColorLayerNames()) > 1:
            self.fState.fBlendFlags |= hsGMatState.hsGMatBlendFlags["kBlendAlpha"]
    

    def FromUvTex(self,image,obj):
        resmanager=self.getResManager()
        root=self.getRoot()

        # Use default settings here...
        mipmapinfo = blMipMapInfo()
        mipmapinfo.fImageName = image.getName()
        mipmapinfo.fMipMaps = True
        mipmapinfo.fGauss = False
        mipmapinfo.fResize = True
        
        exportTexturesToPrp = alcconfig.export_textures_to_page_prp
        try:
            p = obj.getProperty("ignorePPT")
            if (bool(p.getData()) == True):
                exportTexturesToPrp = 0
        except:
            pass        

        print "  Exporting Mipmap image",image.getName()
        mipmap=plMipMap.Export(root,image.getName(),image,mipmapinfo,exportTexturesToPrp)

        print "  Processes Mipmap image",mipmap.data.Key.name

        self.fTexture = mipmap.data.getRef()

        # allow use of alpha
        self.fState.fBlendFlags |= hsGMatState.hsGMatBlendFlags["kBlendAlpha"]
                
        if obj.type == "Mesh":
            mesh = obj.getData(False,True)
            for mface in mesh.faces:
                if mface.uv and mface.mode & Blender.Mesh.FaceModes["TWOSIDE"]:
                    self.fState.fMiscFlags  |= hsGMatState.hsGMatMiscFlags["kMiscTwoSided"] 
                    break
        
        # set the blendflags for this layer to the alphaflags, if it has alhpa
        if(mipmap.data.FullAlpha | mipmap.data.OnOffAlpha):
            #self.fRenderLevel = plRenderLevel(plRenderLevel.MajorLevel["kDefRendMajorLevel"],\
            #                                  plRenderLevel.MinorLevel["kDefRendMinorLevel"])
            self.UsesAlpha = True


    def FromLamp(self,mtex,lamp):
        resmanager=self.getResManager()
        root=self.getRoot()

        pass


class blMipMapInfo:

    def __init__(self):
        self.fImageName = ""
        self.fMipMaps = True
        self.fResize = True
        self.fCalcAlpha = False
        self.fGauss = False
        self.fAlphaMult = 1.0
        self.fCompressionType = plBitmap.Compression["kDirectXCompression"]
        self.fBitmapInfo = plBitmap.Info()
        self.fBitmapInfo.fDirectXInfo.fCompressionType = plBitmap.CompressionType["kError"]
            
    def read(self,stream):
        self.fImageName = stream.ReadSafeString(0)
        self.fMipMaps = stream.ReadBool()
        self.fResize = stream.ReadBool()
        self.fCalcAlpha = stream.ReadBool()
        self.fGauss = stream.ReadBool()
        self.fAlphaMult = stream.ReadFloat()
        self.fCompressionType = stream.ReadByte()

        if (self.fCompressionType != plBitmap.Compression["kUncompressed"]  and  self.fCompressionType != plBitmap.Compression["kJPEGCompression"]):
            self.fBitmapInfo.fDirectXInfo.fBlockSize = stream.ReadByte()
            self.fBitmapInfo.fDirectXInfo.fCompressionType = stream.ReadByte()
        else:
            self.fBitmapInfo.fUncompressedInfo.fType = stream.ReadByte()
        
    def write(self,stream):
        # Set compression types correctly
        if self.fBitmapInfo.fDirectXInfo.fCompressionType == plBitmap.CompressionType["kDXT1"]:
            self.fBitmapInfo.fDirectXInfo.fBlockSize = 8
        elif self.fBitmapInfo.fDirectXInfo.fCompressionType == plBitmap.CompressionType["kDXT5"]:
            self.fBitmapInfo.fDirectXInfo.fBlockSize = 16

        stream.WriteSafeString(self.fImageName,0)
        stream.WriteBool(self.fMipMaps)
        stream.WriteBool(self.fResize)
        stream.WriteBool(self.fCalcAlpha)
        stream.WriteBool(self.fGauss)
        stream.WriteFloat(self.fAlphaMult)
        stream.WriteByte(self.fCompressionType)
        
        if (self.fCompressionType != plBitmap.Compression["kUncompressed"]  and  self.fCompressionType != plBitmap.Compression["kJPEGCompression"]):
            stream.WriteByte(self.fBitmapInfo.fDirectXInfo.fBlockSize)
            stream.WriteByte(self.fBitmapInfo.fDirectXInfo.fCompressionType)
        else:
            stream.WriteByte(self.fBitmapInfo.fUncompressedInfo.fType)
    
    def equals(self,ext):
        
        if not self.fImageName == ext.fImageName:
            return False
        if not self.fMipMaps == ext.fMipMaps:
            return False
        if not self.fResize == ext.fResize:
            return False

        if not self.fGauss == ext.fGauss:
            return False
        
        if not self.fAlphaMult == ext.fAlphaMult:
            return False

        if not self.fCompressionType == ext.fCompressionType:
            return False

        if self.fCompressionType == plBitmap.Compression["kDirectXCompression"]:
            # Ignore the dxt setting if it is set to kError (used as autodetect)....
            if not self.fBitmapInfo.fDirectXInfo.fCompressionType == plBitmap.CompressionType["kError"]:
                if not ext.fBitmapInfo.fDirectXInfo.fCompressionType == plBitmap.CompressionType["kError"]:
                    if not self.fBitmapInfo.fDirectXInfo.fCompressionType == ext.fBitmapInfo.fDirectXInfo.fCompressionType:
                        return False
        
        elif self.fCompressionType == plBitmap.Compression["kUncompressed"]:
            if not self.fBitmapInfo.fUncompressedInfo.fType == ext.fBitmapInfo.fUncompressedInfo.fType:
                return False

        if not self.fCalcAlpha == ext.fCalcAlpha:
            return False

        
        return True
    

    def export_tex(self,tex):
        # This is only valid for image textures :)
        if not tex is None and tex.type == Blender.Texture.Types["IMAGE"] and not tex.image == None:
            
            self.fImageName = tex.image.getName()
        
            if tex.flags & Blender.Texture.Flags["NEGALPHA"]:
                pass

            if tex.imageFlags & Blender.Texture.ImageFlags["INTERPOL"]:
                self.fCompressionType = plBitmap.Compression["kDirectXCompression"]
                if tex.imageFlags & Blender.Texture.ImageFlags["USEALPHA"]:
                    self.fBitmapInfo.fDirectXInfo.fCompressionType = plBitmap.CompressionType["kDXT5"]
                else:
                    # Let it be auto determined....
                    self.fBitmapInfo.fDirectXInfo.fCompressionType = plBitmap.CompressionType["kError"]
            else:
                if self.fImageName[-4:] == ".jpg" or self.fImageName[-5:] == ".jpeg":
                    self.fCompressionType = plBitmap.Compression["kJPEGCompression"]
                else:
                    self.fCompressionType = plBitmap.Compression["kUncompressed"]
                    self.fBitmapInfo.fUncompressedInfo.fType = plBitmap.Uncompressed["kRGB8888"] # The only format we support
                self.fResize = False

            if tex.imageFlags & 0x1000: #Blender.Texture.ImageFlags["GAUSS"] doesn't work... :/
                self.fGauss = True
            else:
                self.fGauss = False
                
            self.fAlphaMult = tex.filterSize
            
            if tex.imageFlags & Blender.Texture.ImageFlags["CALCALPHA"]:
                self.fCalcAlpha = True
            else:
                self.fCalcAlpha = False            

            if tex.imageFlags & Blender.Texture.ImageFlags["MIPMAP"]:
                self.fMipMaps = True
            else:
                self.fMipMaps = False            
            
            if tex.imageFlags & Blender.Texture.ImageFlags["MIPMAP"] or tex.imageFlags & Blender.Texture.ImageFlags["INTERPOL"]:
                self.fResize = True
            else:
                self.fResize = False
            
                
    def clone(self):
        new = blMipMapInfo()

        new.fImageName = self.fImageName
        new.fMipMaps = self.fMipMaps 
        new.fResize = self.fResize 
        new.fCalcAlpha = self.fCalcAlpha 
        new.fGauss = self.fGauss 
        new.fAlphaMult = self.fAlphaMult 
        new.fCompressionType = self.fCompressionType 

        new.fBitmapInfo.fDirectXInfo.fBlockSize = self.fBitmapInfo.fDirectXInfo.fBlockSize
        new.fBitmapInfo.fDirectXInfo.fCompressionType = self.fBitmapInfo.fDirectXInfo.fCompressionType

        new.fBitmapInfo.fUncompressedInfo.fType = self.fBitmapInfo.fUncompressedInfo.fType

        return new


    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s  = "---------------"
        s += "\nImagename:" + str(self.fImageName)
        s += "\nResize Image: " + str(self.fResize)
        s += "\nMake MipMaps: " + str(self.fMipMaps)
        s += "\nCalculate Alpha:" + str(self.fCalcAlpha)
        s += "\nMipMap Gauss:" + str(self.fGauss)
        s += "\nMipmap AlphaMult:" + str(self.fAlphaMult)
        if self.fCompressionType == plBitmap.Compression["kDirectXCompression"]:
            s += "\nCompressionType: DXT"
            if self.fBitmapInfo.fDirectXInfo.fCompressionType == plBitmap.CompressionType["kDXT1"]:
                s += "\n SubType: DXT1"
            elif self.fBitmapInfo.fDirectXInfo.fCompressionType == plBitmap.CompressionType["kDXT5"]:
                s += "\n SubType: DXT5"
        elif self.fCompressionType == plBitmap.Compression["kJPEGCompression"]:
            s += "\nCompressionType: JPEG"
        elif self.fCompressionType == plBitmap.Compression["kUncompressed"]:
            s += "\nCompressionType: Uncompressed"
        s += "\n---------------\n"
        
        return s

class plBitmap(hsKeyedObject):               # Type 0x03   

    #region Structures
    class DirectXInfo:
        def __init__(self):
            self.fCompressionType = 0 #CompressionType;
            self.fBlockSize = 0 #ubyte  #Formerly texelSize
    

    class UncompressedInfo:
        def __init__(self):
            self.fType = 0 #Uncompressed

    class Info:
        def __init__(self):
            self.fDirectXInfo = plBitmap.DirectXInfo() #DirectXInfo 
            self.fUncompressedInfo = plBitmap.UncompressedInfo() #UncompressedInfo 


    #region Constants
    CompressionType = \
    { \
        "kError" : 0, \
        "kDXT1"  : 1, \
        "kDXT2"  : 2, \
        "kDXT3"  : 3, \
        "kDXT4"  : 4, \
        "kDXT5"  : 5  \
    }

    Uncompressed =  \
    { \
        "kRGB8888"    : 0, \
        "kRGB4444"    : 1, \
        "kRGB1555"    : 2, \
        "kInten8"     : 3, \
        "kAInten88"   : 4  \
    }

    Space = \
    {  \
        "kNoSpace"        : 0, \
        "kDirectSpace"    : 1, \
        "kGraySpace"      : 2, \
        "kIndexSpace"     : 3  \
    }

    Flags = \
    {  \
        "kNoFlag"               :    0x0, \
        "kAlphaChannelFlag"     :    0x1, \
        "kAlphaBitFlag"         :    0x2, \
        "kBumpEnvMap"           :    0x4, \
        "kForce32Bit"           :    0x8, \
        "kDontThrowAwayImage"   :   0x10, \
        "kForceOneMipLevel"     :   0x20, \
        "kNoMaxSize"            :   0x40, \
        "kIntensityMap"         :   0x80, \
        "kHalfSize"             :  0x100, \
        "kUserOwnsBitmap"       :  0x200, \
        "kForceRewrite"         :  0x400, \
        "kForceNonCompressed"   :  0x800, \
        "kIsTexture"            : 0x1000, \
        "kIsOffscreen"          : 0x2000, \
        "kMainScreen"           :    0x0, \
        "kIsProjected"          : 0x4000, \
        "kIsOrtho"              : 0x8000  \
    }

    Compression = \
    { \
        "kUncompressed"         : 0, \
        "kDirectXCompression"   : 1, \
        "kJPEGCompression"      : 2  \
    }

    BITMAPVER = 2;


    def __init__(self,parent,name="unnamed",type=0x0003):
        hsKeyedObject.__init__(self,parent,name,type)
        self.BitmapInfo = plBitmap.Info() # Info 
        
        self.fCompressionType = 1 # Compression 
    
        self.fPixelSize = 1 #ubyte 
        self.fSpace = 1     #sbyte 
        self.fFlags = 0     #Flags 
    
        self.fLowModifiedTime = 0 #uint #Formerly fInputManager
        self.fHighModifiedTime = 0 #uint #Formerly fPageMgr
        
        # for internal handling (From old implementation)
        self.isCubEvMapPart = 0 
        self.BlenderImage=None

        self.FullAlpha = False
        self.OnOffAlpha = False

        self.MipMapInfo = blMipMapInfo()

        self.texCacheExtension = ".bmap"

    def _Find(page,name):
        return page.find(0x0003,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0003,name,1)
    FindCreate = staticmethod(_FindCreate)


    def read(self,stream, really=1,silent=1):
        hsKeyedObject.read(self,stream, really, silent)
    
        stream.ReadByte() #Discarded: Version
        self.fPixelSize = stream.ReadByte()
        self.fSpace = stream.ReadByte()
        self.fFlags = stream.Read16()
        self.fCompressionType = stream.ReadByte()
        
        
        if (self.fCompressionType != plBitmap.Compression["kUncompressed"]  and  self.fCompressionType != plBitmap.Compression["kJPEGCompression"]):
            self.BitmapInfo.fDirectXInfo.fBlockSize = stream.ReadByte()
            self.BitmapInfo.fDirectXInfo.fCompressionType = stream.ReadByte()
        else:
            self.BitmapInfo.fUncompressedInfo.fType = stream.ReadByte()
        
        self.fLowModifiedTime = stream.Read32()
        self.fHighModifiedTime = stream.Read32()

    def write(self, stream, really=1):
        hsKeyedObject.write(self,stream,really)

        stream.WriteByte(0x02)    # always version 0x02
        stream.WriteByte(self.fPixelSize)
        stream.WriteByte(self.fSpace)
        stream.Write16(self.fFlags)
        stream.WriteByte(self.fCompressionType)
        
        if (self.fCompressionType != plBitmap.Compression["kUncompressed"]  and  self.fCompressionType != plBitmap.Compression["kJPEGCompression"]):
            stream.WriteByte(self.BitmapInfo.fDirectXInfo.fBlockSize)
            stream.WriteByte(self.BitmapInfo.fDirectXInfo.fCompressionType)
        else:
            stream.WriteByte(self.BitmapInfo.fUncompressedInfo.fType)
        
        stream.Write32(self.fLowModifiedTime)
        stream.Write32(self.fHighModifiedTime)

    # Version header for texture cache files
    # Update the last two digits when changing the file format
    TEXCACHEVER = "TC02"

    def TexCache_GetFilename(self):
        resmanager=self.getResManager()
        MyPath=resmanager.getBasePath()
        CachePath = MyPath + "/" + self.parent.parent.parent.age.name + "_TexCache/"

        # Make the directory if texture_cache is enabled
        if (alcconfig.texture_cache):
            try:
                os.mkdir(CachePath)
            except OSError:
                pass

        # Generate the filename
        CacheFile = CachePath + str(self.Key.name) + self.texCacheExtension

        return CacheFile

    def TexCache_Exists(self):
        if os.path.isfile(self.TexCache_GetFilename()):
            mipmapinfo = self.TexCache_LoadMipMapInfo()
            
            if not mipmapinfo is None:
                if self.MipMapInfo.equals(mipmapinfo):
#                    print "TEXCACHE DEBUG:"
#                    print "Mipmapinfo's match"
                    return True
#                else:
#                    print "TEXCACHE DEBUG:"
#                    print "Self's mipmapinfo:"
#                    print self.MipMapInfo
#                    print "Cachefile's mipmapinfo:"
#                    print mipmapinfo
#            else:
#                print "TEXCACHE DEBUG:"
#                print "Could not read mipmapinfo from cachefile...."
                
        return False
        
    def TexCache_Store(self,mipmapinfo=None):
        CacheFile = self.TexCache_GetFilename()
        stream=hsStream(CacheFile,"wb")

        # Write the version number
        stream.fs.write(plBitmap.TEXCACHEVER)

        if mipmapinfo is None:
            self.MipMapInfo.write(stream)
        else:
            mipmapinfo.write(stream)
        # Write the alpha flags
        stream.WriteBool(self.FullAlpha)
        stream.WriteBool(self.OnOffAlpha)
        self.write(stream)
        stream.close()
    
    def TexCache_LoadVersionInfo(self,stream):
        try:
            versionString = stream.fs.read(4)
            if versionString == plBitmap.TEXCACHEVER:
                return True
        except:
            pass
        return False

    def TexCache_LoadMipMapInfo(self):
        # load in the data from the file
        CacheFile = self.TexCache_GetFilename()
        stream=hsStream(CacheFile,"rb")
        try:
            # load the texture cache version first
            if not self.TexCache_LoadVersionInfo(stream):
                return None
            mipmapinfo = blMipMapInfo()
            mipmapinfo.read(stream)
            return mipmapinfo
        except:
            print "    WARNING: Problem reading Texture Cache"
            print "             PLEASE REMOVE YOUR OLD TEXTURE CACHE FILES"
            return None
    
    
    def TexCache_Load(self):
        # load in the data from the file
        CacheFile = self.TexCache_GetFilename()
        print "     Reading mipmap %s from cache" % (str(self.Key.name) + ".tex")
        stream=hsStream(CacheFile,"rb")
        try:
            # load the texture cache version first
            if not self.TexCache_LoadVersionInfo(stream):
                raise RuntimeError
            self.MipMapInfo.read(stream)
            # Read the alpha flags
            self.FullAlpha = stream.ReadBool()
            self.OnOffAlpha = stream.ReadBool()
            self.read(stream)
        except:
            print "    WARNING: Problem reading Texture Cache"
            print "             PLEASE REMOVE YOUR OLD TEXTURE CACHE FILES"
        
        stream.close()
        
    def TexCache_Delete(self):
        CacheFile = self.TexCache_GetFilename()
        return os.remove(CacheFile)


 
class plMipMap(plBitmap):                    # Type 0x04

    Color = \
    { \
        "kColor8Config" :  0x0, \
        "kGray44Config" :  0x1, \
        "kGray4Config"  :  0x2, \
        "kGray8Config"  :  0x8, \
        "kRGB16Config"  : 0x10, \
        "kRGB32Config"  : 0x18, \
        "kARGB32Config" : 0x20  \
    }

    CreateDetail = \
    { \
        "kCreateDetailAlpha" :  0x1, \
        "kCreateDetailAdd"   :  0x2, \
        "kCreateDetailMult"  :  0x4, \
        "kCreateDetailMask"  :  0x7, \
        "kCreateCarryAlpha"  : 0x10, \
        "kCreateCarryBlack"  : 0x20, \
        "kCreateCarryMask"   : 0x38  \
    }

    hsGPixelType = \
    { \
        "kPixelARGB4444" : 0, \
        "kPixelARGB1555" : 1, \
        "kPixelAI88"     : 2, \
        "kPixelI8"       : 3  \
    }

    hsGCopyOptions = \
    { \
        "kCopyLODMask" : 0 \
    }

    Data = \
    { \
        "kColorDataRLE" : 0x1, \
        "kAlphaDataRLE" : 0x2  \
    }

    CompositeFlags = \
    { \
        "kForceOpaque"      :  0x1, \
        "kCopySrcAlpha"     :  0x2, \
        "kBlendSrcAlpha"    :  0x4, \
        "kMaskSrcAlpha"     :  0x8, \
        "kBlendWriteAlpha"  : 0x10  \
    }

    ScaleFilter = \
    { \
        "kBoxFilter"     : 0, \
        "kDefaultFilter" : 0  \
    }


    def __init__(self,parent,name="unnamed",type=0x0004):
        plBitmap.__init__(self,parent,name,type)

        self.fImages = [] 
        self.fWidth = 0 
        self.fHeight = 0 
        self.fRowBytes = 0 

        self.fTotalSize = 0 
        self.fNumLevels = 0
        self.fLevelSizes = [] 

        # setting of fields from plBitmap
        self.fPixelSize = 32
        
        # fields used for internal processing
        
        self.Processed = 0
        
        self.Cached_BlenderImage = None
        self.texCacheExtension = ".tex"        
        
    def _Find(page,name):
        return page.find(0x0004,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0004,name,1)
    FindCreate = staticmethod(_FindCreate)

    def read(self, stream, really=1,silent=0):
        plBitmap.read(self,stream,really)

        nread = 0;
        self.fWidth = stream.Read32()
        self.fHeight = stream.Read32()
        self.fRowBytes = stream.Read32()
        self.fTotalSize = stream.Read32()
        self.fNumLevels = stream.ReadByte()
        
        
        if self.fTotalSize == 0:
            return
        
        self.fImages = []
        
        if self.fCompressionType == plBitmap.Compression["kJPEGCompression"]:
            data=tJpgImage(self.fWidth,self.fHeight)
            data.read(stream)
            self.fImages.append(data)

        elif self.fCompressionType == plBitmap.Compression["kDirectXCompression"]:
            if (self.fNumLevels > 0):
                for i in range(self.fNumLevels):
                    data=tDxtImage(self.fWidth>>i,self.fHeight>>i, self.BitmapInfo.fDirectXInfo.fCompressionType)
                    data.read(stream)
                    self.fImages.append(data)

        elif self.fCompressionType == plBitmap.Compression["kUncompressed"]:
            if (self.fNumLevels > 0):
                for i in range(self.fNumLevels):
                    data=tImage(self.fWidth>>i,self.fHeight>>i)
                    data.read(stream)
                    self.fImages.append(data)
        else:
            return

        return

    def write(self,stream, really=1,silent=0):
        plBitmap.write(self,stream,really)
            
        self.fRowBytes = int(self.fWidth * (self.fPixelSize / 8.0))
        
        padding_needed = (4 - (self.fRowBytes % 4) ) # fRowBytes needs to be padded to a multiple of 4
        
        if (padding_needed > 0 and padding_needed < 4):
            self.fRowbytes = self.fRowBytes + padding_needed

        stream.Write32(self.fWidth)
        stream.Write32(self.fHeight)
        stream.Write32(self.fRowBytes)
        
        offset_fTotalSize = stream.tell() # store offset of this field
        stream.Write32(self.fTotalSize) # write dummy fTotalSize

        self.fNumLevels=len(self.fImages)
        stream.WriteByte(self.fNumLevels)

        offset_ImageDataStart=stream.tell() # save begin position of image data
        for img in self.fImages: # write all the images
            img.write(stream)
        offset_ImageDataEnd=stream.tell() # save end position of image data

        
        self.fTotalSize = offset_ImageDataEnd - offset_ImageDataStart # calculate actual size
        stream.seek(offset_fTotalSize) # reposition stream to fTotalSize field
        stream.Write32(self.fTotalSize) # write actual fTotalSize
        stream.seek(offset_ImageDataEnd) # reposition stream to end of object


    def SetConfig(self,Config):
        if Config == plMipMap.Color["kColor8Config"]:
            self.fPixelSize = 8
            self.fSpace = 3
            self.fFlags = plBitmap.Flags["kNoFlag"]

        elif Config == plMipMap.Color["kGray44Config"]:
            self.fPixelSize = 8
            self.fSpace = 2
            self.fFlags = plBitmap.Flags["kAlphaChannelFlag"]

        elif Config == plMipMap.Color["kGray4Config"]:
            self.fPixelSize = 4
            self.fSpace = 2
            self.fFlags = plBitmap.Flags["kNoFlag"]

        elif Config == plMipMap.Color["kGray8Config"]:
            self.fPixelSize = 8
            self.fSpace = 1
            self.fFlags = plBitmap.Flags["kNoFlag"]

        elif Config == plMipMap.Color["kRGB16Config"]:
            self.fPixelSize = 16
            self.fSpace = 1
            self.fFlags = plBitmap.Flags["kAlphaBitFlag"]

        elif Config == plMipMap.Color["kRGB32Config"]:
            self.fPixelSize = 32
            self.fSpace = 1
            self.fFlags = plBitmap.Flags["kNoFlag"]

        elif Config == plMipMap.Color["kARGB32Config"]:
            self.fPixelSize = 32
            self.fSpace = 1
            self.fFlags = plBitmap.Flags["kAlphaChannelFlag"]

    ###################################
    ##                               ##
    ##      Interface Functions      ##
    ##                               ##
    ###################################
        
    def ToBlenderImage(self):
        # retrieve the image from cache if it's there
        if self.Cached_BlenderImage!=None:
            return self.Cached_BlenderImage
        
        print "     [MipMap %s]"%str(self.Key.name)

        # Build up a temprary file path and name
        resmanager=self.getResManager()
        BasePath=resmanager.getBasePath()
        TexPath = BasePath + "/TMP_Textures/"

        Name=stripIllegalChars(str(self.Key.name)) + ".png"
        TexFileName = TexPath + "/" + Name

        # create the temporary Texture Path
        try:
            os.mkdir(TexPath)
        except OSError:
            pass
            
        # get the first image in the list (return None if it isn't there)
        if len(self.fImages)==0:
            return None
            
        myimg = self.fImages[0]
        
        # save it to the temporary folder
        myimg.save(TexFileName)
        
        # and load it again as a blender image
        BlenderImg=Blender.Image.Load(TexFileName)
        BlenderImg.pack()
        
        # cache it for easy fetching
        self.Cached_BlenderImage=BlenderImg
        
        return BlenderImg
        
    def ToBlenderTex(self,name=None):
        print "     [MipMap %s]"%str(self.Key.name)

        if name == None:
            name = str(self.Key.name)

        # Form the Blender cubic env map MTex
        Tex=Blender.Texture.New(name)
        Tex.setImage(self.ToBlenderImage())
        Tex.type  = Blender.Texture.Types["IMAGE"]
        Tex.setImageFlags('UseAlpha')

        return Tex

    def FromBlenderImage(self,BlenderImage):
        if(self.Processed):
            return

        print "    [MipMap %s]"%str(self.Key.name)
        print "     MipMapInfo:"
        print self.MipMapInfo

        if ((alcconfig.texture_cache) and self.TexCache_Exists()): # unless disabled, check for the texture's cache file
            self.TexCache_Load()
        else:
            # Read in the texture filename from blender (for the name),
            # and convert the texture to an image buffer
            
            print "     Converting texture %s..." %str(self.Key.name)
            ImWidth, ImHeight = BlenderImage.getSize()
            ImageBuffer=cStringIO.StringIO()
            
            self.FullAlpha = False
            self.OnOffAlpha = False
            
            if str(BlenderImage.getFilename())[-4:]==".gif":
                isGIF=1
                print "     Image is GIF Image"
            else:
                isGIF=0
                
            for y in range(ImHeight,0,-1):
                for x in range(ImWidth):
                    r,g,b,a = BlenderImage.getPixelF(x,y-1)
                    if self.MipMapInfo.fCalcAlpha:
                        a = (float(r)+float(g)+float(b))/3.0
                    else:
                        if isGIF: # ignora alpha info, and always put it to opaque
                            a=1.0
            
                    #print "Color: %f %f %f - Alpha: %f" % (r,g,b,a)
                    if a == 0 and not self.FullAlpha:
                        self.OnOffAlpha = True
                    if a > 0.0 and a < 1.0:
                        OnOffAlpha = 0
                        self.FullAlpha = True

                    ImageBuffer.write(struct.pack("BBBB",r*255,g*255,b*255,a*255))
            
            # see if we should automatically determine compression type
            if self.MipMapInfo.fCompressionType == plBitmap.Compression["kDirectXCompression"] and \
                self.MipMapInfo.fBitmapInfo.fDirectXInfo.fCompressionType == plBitmap.CompressionType["kError"]:
                if self.FullAlpha: # Full Alpha requires DXT5
                    print "     Image uses full alpha channel, compressing DXT5"
                    self.MipMapInfo.fBitmapInfo.fDirectXInfo.fCompressionType = plBitmap.CompressionType["kDXT5"]
                elif self.OnOffAlpha: # DXT1 supports On/Off Alpha
                    self.MipMapInfo.fBitmapInfo.fDirectXInfo.fCompressionType = plBitmap.CompressionType["kDXT1"]
                    print "     Image uses on/off alpha , compressing DXT1"
                else: # anything else is ok on the DXT1
                    self.MipMapInfo.fBitmapInfo.fDirectXInfo.fCompressionType = plBitmap.CompressionType["kDXT1"]
                    print "     Image uses no alpha, compressing DXT1"

            # Reset the image buffer
            ImageBuffer.seek(0)
            
            # And use the FromRawImage function to set this texture data.
            
            self.FromRawImage(ImageBuffer,ImWidth,ImHeight)

            # now store the data in a file if texture_cache is enabled
            if (alcconfig.texture_cache):
                self.TexCache_Store()

        self.Processed = 1

    def FromRawImage(self, ImageBuffer, Width, Height):

        # Copy basic parameters
        self.fWidth     = Width
        self.fHeight    = Height
        
        # prepare the image buffer and images field
        ImageBuffer.seek(0)
        self.fImages=[]

        # Resize images to make width and height be powers of two
        # Makes it easier on the graphics card.
        # Don't do this on JPEG compression
        if self.MipMapInfo.fResize and self.MipMapInfo.fCompressionType != plBitmap.Compression["kJPEGCompression"]:    
        
            new_w=2 ** int(math.log(self.fWidth,2))
            new_h=2 ** int(math.log(self.fHeight,2))
            
            if new_w!=self.fWidth or new_h!=self.fHeight:
                print "      Resizing image from %ix%i to %ix%i" % (self.fWidth,self.fHeight,new_w, new_h)
                im=Image.new("RGBA",(self.fWidth,self.fHeight))
                im.fromstring(ImageBuffer.read())
                im2=im.resize((new_w,new_h),Image.ANTIALIAS)
                ImageBuffer=cStringIO.StringIO()
                ImageBuffer.write(im2.tostring())
                self.fWidth=new_w
                self.fHeight=new_h
            else:
                print "      Image size: %ix%i" % (self.fWidth,self.fHeight)
        else:
            print "      Image size: %ix%i" % (self.fWidth,self.fHeight)

        # Compress the image to the desired compression, 
        # either DXT compression, JPEG Compression or Uncompressed (only RGB8888 colorspace supported)
    
        if (self.MipMapInfo.fCompressionType == plBitmap.Compression["kDirectXCompression"]):
            print "      DXT Compressing texture .... this can take a few minutes"
            
            if(self.MipMapInfo.fBitmapInfo.fDirectXInfo.fCompressionType == plBitmap.CompressionType["kDXT1"]):
                print "     Compressing DXT1"
            elif(self.MipMapInfo.fBitmapInfo.fDirectXInfo.fCompressionType == plBitmap.CompressionType["kDXT5"]):
                print "     Compressing DXT5"
            elif(self.MipMapInfo.fBitmapInfo.fDirectXInfo.fCompressionType == plBitmap.CompressionType["kError"]):
                print "     Compressing kError"
                raise RuntimeError, "Hmm, wait a second, we can't compress \"kError\", you'd better fix this somewhere :P"
            else:
                print "     DXT Compression unknown"
                raise RuntimeError, "Okay, don't know what went wrong here... Probably you're a really smart person to be able to get this exception that should never be given...."

            myimg=tDxtImage(self.fWidth,self.fHeight,self.MipMapInfo.fBitmapInfo.fDirectXInfo.fCompressionType)
            myimg.data=ImageBuffer  # input the buffer into the image
            myimg.fromRGBA()        # tell it to process
            self.fImages=[myimg,]
            self.fCompressionType = plBitmap.Compression["kDirectXCompression"]
            self.BitmapInfo.fDirectXInfo.fCompressionType = self.MipMapInfo.fBitmapInfo.fDirectXInfo.fCompressionType

            if self.MipMapInfo.fBitmapInfo.fDirectXInfo.fCompressionType == plBitmap.CompressionType["kDXT1"]:
                self.BitmapInfo.fDirectXInfo.fBlockSize = 8
            elif self.MipMapInfo.fBitmapInfo.fDirectXInfo.fCompressionType == plBitmap.CompressionType["kDXT5"]:
                self.BitmapInfo.fDirectXInfo.fBlockSize = 16
            else:
                raise ValueError, "Can only support DXT1 and DXT5 Compression"
            
        elif (self.MipMapInfo.fCompressionType == plBitmap.Compression["kJPEGCompression"]):
            print "     JPEG Compressing texture ...."

            myimg=tJpgImage(self.fWidth,self.fHeight)
            myimg.data=ImageBuffer  # input the buffer into the image
            myimg.fromRGBA()        # tell it to process
            self.fImages=[myimg,]
            self.fCompressionType = plBitmap.Compression["kJPEGCompression"]
            self.BitmapInfo.fUncompressedInfo.fType = plBitmap.Uncompressed["kRGB8888"];

        elif (self.MipMapInfo.fCompressionType == plBitmap.Compression["kUncompressed"]):
            print "     Not Compressing texture"

            myimg=tImage(self.fWidth,self.fHeight)
            myimg.data=ImageBuffer  # input the buffer into the image
            myimg.fromRGBA()        # tell it to process
            self.fImages=[myimg,]
            self.fCompressionType = plBitmap.Compression["kUncompressed"]
            self.BitmapInfo.fUncompressedInfo.fType = plBitmap.Uncompressed["kRGB8888"];


        # Make the mipmaps
        # this works by copying the image that was compressed before, resizing it to half it's size, and 
        # adding it to the queue - this repeats until the lowest texture...
        # ofcourse, no mipmapping for jpeg uncompressed textures :)
        
        if self.MipMapInfo.fCompressionType != plBitmap.Compression["kJPEGCompression"] and self.MipMapInfo.fMipMaps:
            print "     MipMapping...."
#            print "     MipMapinfo:\n",self.MipMapInfo
            
            print "      Level 0 %ix%i" %(self.fWidth,self.fHeight)
            i=1
            mw=self.fWidth>>i
            mh=self.fHeight>>i
            while mw!=0 and mh!=0:
                print "      Level %i %ix%i" %(i,mw,mh)
                img=copy.copy(myimg)    # copy the previous image
                img.resize_alphamult(mw,mh,self.MipMapInfo.fAlphaMult,self.MipMapInfo.fGauss)       # apply the new size

                img.fromRGBA()          # and reprocess/recompress
                self.fImages.append(img) # add to the list
                myimg=img
                i=i+1
                mw=self.fWidth>>i
                mh=self.fHeight>>i
        
        print "Done"

    UniquePrefix = 1

    def _FindCreateByMipMapInfo(page,name,mipmapinfo,exportTexturesToPrp):
        resmgr = page.resmanager
        tex=resmgr.findPrp("Textures")
        if not exportTexturesToPrp:
            page=tex
            if page==None:
                raise "    Textures PRP file not found"
        
        try:
            if not page.age.specialtex.index(name) is -1:
                page = tex
                if page==None:
                    raise "    Textures PRP file not found"
        except ValueError:
            pass
        
#        print "Locating mipmap for mipmapinfo:"
#        print mipmapinfo
        nameExists = False
        # See if we have already got one of these....
        idx = page.findidx(0x0004)
        for plobj in idx.listobjects():
#            print "-- MIPMAP:",plobj.data.Key.name
#            print "   MipmapInfo:"
#            print plobj.data.MipMapInfo
            
            if plobj.data.MipMapInfo.equals(mipmapinfo):
                return plobj
            if plobj.data.Key.name==name:
                nameExists = True
                
                

        # else, create one        
        
        # make sure we have a unique name....
        if nameExists:
            name = str(plMipMap.UniquePrefix) +"-" + name
            plMipMap.UniquePrefix += 1
        
        plobj = plMipMap.FindCreate(page,name)
        plobj.data.MipMapInfo = mipmapinfo
        
        return plobj
        

    FindCreateByMipMapInfo = staticmethod(_FindCreateByMipMapInfo)

    def _Export(page,name,blenderimage,mipmapinfo,exportTexturesToPrp):
        mipmap = plMipMap.FindCreateByMipMapInfo(page,name,mipmapinfo,exportTexturesToPrp)
        mipmap.data.SetConfig(plMipMap.Color["kARGB32Config"])
        mipmap.data.FromBlenderImage(blenderimage)
        return mipmap
        
    Export = staticmethod(_Export)
    
    def _Export_Raw(page,name,imbuffer, imwidth, imheight, mipmapinfo,exportTexturesToPrp):
        mipmap = plMipMap.FindCreateByMipMapInfo(page,name,mipmapinfo,exportTexturesToPrp)
        mipmap.data.SetConfig(plMipMap.Color["kARGB32Config"])
        mipmap.data.FromRawImage(imbuffer,imwidth,imheight)
        return mipmap

    Export_Raw = staticmethod(_Export_Raw)

class plCubicEnvironMap(plBitmap):          # Type 0x05

    Faces = {
        "kLeftFace"     : 0,
        "kRightFace"    : 1,
        "kFrontFace"    : 2,
        "kBackFace"     : 3,
        "kTopFace"      : 4,
        "kBottomFace"   : 5
    }

    def __init__(self,parent,name="unnamed",type=0x0005):
        plBitmap.__init__(self,parent,name,type)
        self.fFaces = []
        
        self.Processed = 0

        self.Cached_BlenderCubicMap = None
        self.texCacheExtension = ".qmap"

    def _Find(page,name):
        return page.find(0x0005,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0005,name,1)
    FindCreate = staticmethod(_FindCreate)


    def read(self, stream):
        plBitmap.read(self,stream);

        self.fFaces = []
        for i in range(6):
            mipmap = plMipMap(self.parent)
            mipmap.read(stream,0) # "Really" is set to 0, to avoid reading hsKeyedObject code
            self.fFaces.append(mipmap)

    def write(self, stream):
        plBitmap.write(self,stream);

        for i in range(6):
            self.fFaces[i].write(stream,0) # "Really" is set to 0, to avoid writing hsKeyedObject code
        
    ###################################
    ##                               ##
    ##      Interface Functions      ##
    ##                               ##
    ###################################
        
    def ToBlenderCubicMap(self):
        # retrieve the image from cache if it's there
        if self.Cached_BlenderCubicMap==None:
            print "     [CubicEnvMap %s]"%str(self.Key.name)

            # Build up a temprary file path and name
            resmanager=self.getResManager()
            BasePath=resmanager.getBasePath()
            TexPath = BasePath + "/TMP_Textures/"
    
            Name=stripIllegalChars(str(self.Key.name)) + ".png"
            TexFileName = TexPath + "/" + Name
            TexFileName = TexFileName.replace("*","_") # strip out unwanted characters
    
    
            # Convert images to Blender images for easy processing
            RawImages = []
            for i in (0,3,1,5,4,2):
                rawimg = self.fFaces[i].ToBlenderImage()
                RawImages.append(rawimg)
    
            # Stitch together 6 images
            xpart,ypart, = RawImages[0].getSize()
            print "      Size of maps: %i x %i" % (xpart,ypart)

            width = xpart*3
            height = ypart*2

            CookedImage = Image.new("RGBA",(width,height))
            
            try:
            
                ImageBuffer=cStringIO.StringIO()
                # Copy bottom three images
                for y in range(ypart-1,-1,-1):
                    for i in range(0,3):
                        for x in range(0,xpart):
                            try:
                                r,g,b,a = RawImages[i].getPixelF(x,y)
                                ImageBuffer.write(struct.pack("BBBB",r*255,g*255,b*255,a*255))
                            except Exception, detail:
                                print "      Now in image # %i"% i
                                print "      Size of image:",RawImages[i].getSize()
                                print "      Value of X and Y: %i, %i" % (x,y)
                                raise Exception, detail
        
                # Copy top three images
                for y in range(ypart-1,-1,-1):
                    for i in range(3,6):
                        for x in range(0,xpart):
                            try:
                                r,g,b,a = RawImages[i].getPixelF(x,y)
                                ImageBuffer.write(struct.pack("BBBB",r*255,g*255,b*255,a*255))
                            except Exception, detail:
                                print "      Now in image # %i"% i
                                print "      Size of image:",RawImages[i].getSize()
                                print "      Value of X and Y: %i, %i" % (x,y)
                                raise Exception, detail
        
                # Transfer buffer to image
                ImageBuffer.seek(0)
    
                CookedImage.fromstring(ImageBuffer.read())
            
            except Exception, detail:
                print "      Exception:",detail
                print "      Continuing"
                
            # And save the image...
            CookedImage.save(TexFileName)
    
            # Load it back in to process in blender
            self.Cached_BlenderCubicMap = Blender.Image.Load(TexFileName)
        
        return self.Cached_BlenderCubicMap
    
    def ToBlenderTex(self,name=None):

        if name == None:
            name = str(self.Key.name)

        # Form the Blender cubic env map MTex
        Tex=Blender.Texture.New(name)
        Tex.setImage(self.ToBlenderCubicMap())
        Tex.type  = Blender.Texture.Types["ENVMAP"]
        Tex.stype = Blender.Texture.STypes["ENV_LOAD"]

        return Tex
        
    def FromBlenderCubicMap(self,cubicmap):
        # if we are already set up and ready, don't continue....
        if(self.Processed):
            return

        if ((alcconfig.texture_cache) and self.TexCache_Exists()): # unless disabled, check for the texture's cache file
            self.TexCache_Load()
        else:
        
            print " => Converting CubicEnvironMap %s <=" %str(self.Key.name)
        
            # first calculate the size of the 6 parts
            
            width, height = cubicmap.getSize()
            
            xpart = width / 3
            ypart = height / 2
            
    
            # Now parse those 6 parts one by one
    
            CubeSide = 0 # just there to count up from 0-5 even in a weird order
            
            for i in (0,2,5,1,4,3): # for correct conversion from blender to uru sequence we need this sequence
                if(i == 0):
                    ystart = height
                    yend = height - ypart
                    xstart = 0
                    xend = 0 + xpart
                elif(i == 1):
                    ystart = height
                    yend = height - ypart
                    xstart = xpart
                    xend = 0 + 2*xpart
                elif(i == 2):
                    ystart = height
                    yend = height - ypart
                    xstart = 2*xpart
                    xend = width
                elif(i == 3):
                    ystart = ypart
                    yend = 0
                    xstart = 0
                    xend = 0 + xpart
                elif(i == 4):
                    ystart = ypart
                    yend = 0
                    xstart = xpart
                    xend = 0 + 2*xpart
                elif(i == 5):
                    ystart = ypart
                    yend = 0
                    xstart = 2*xpart
                    xend = width
                
                ImageBuffer=cStringIO.StringIO()
                self.FullAlpha = False
                self.OnOffAlpha = True
                
                if str(cubicmap.getFilename())[-4:]==".gif":
                    isGIF=1
                else:
                    isGIF=0
                for y in range(ystart,yend,-1):
                    for x in range(xstart,xend):
                        r,g,b,a = cubicmap.getPixelF(x,y-1)

                        if self.MipMapInfo.fCalcAlpha:
                            a = (r+g+b)/3
                        else:
                            if isGIF: # ignora alpha info, and always put it to opaque
                                a=1.0

                        if a == 0 and not self.FullAlpha:
                            self.OnOffAlpha = True
                        if a > 0 and a < 1:
                            OnOffAlpha = False
                            self.FullAlpha = True
    
                        ImageBuffer.write(struct.pack("BBBB",r*255,g*255,b*255,a*255))
                
                # see if we should automatically determine compression type
                if self.MipMapInfo.fCompressionType == plBitmap.Compression["kDirectXCompression"] and \
                    self.MipMapInfo.fBitmapInfo.fDirectXInfo.fCompressionType == plBitmap.CompressionType["kError"]:
                    if self.FullAlpha: # Full Alpha requires DXT5
                        print "     Image uses full alpha channel, compressing DXT5"
                        self.MipMapInfo.fBitmapInfo.fDirectXInfo.fCompressionType = plBitmap.CompressionType["kDXT5"]
                    elif self.OnOffAlpha: # DXT1 supports On/Off Alpha
                        self.MipMapInfo.fBitmapInfo.fDirectXInfo.fCompressionType = plBitmap.CompressionType["kDXT1"]
                        print "     Image uses on/off alpha , compressing DXT1"
                    else: # anything else is ok on the DXT1
                        self.MipMapInfo.fBitmapInfo.fDirectXInfo.fCompressionType = plBitmap.CompressionType["kDXT1"]
                        print "     Image uses no alpha, compressing DXT1"
    
                print " Setting EnvMap side %i" % CubeSide
                CubeSide += 1
    
                # prepare a MipMap object
                MipMappedFace = plMipMap(self.parent)
                MipMappedFace.Key.name = str(self.Key.name) + "+%i"%(i)
                
                MipMappedFace.MipMapInfo = self.MipMapInfo
                # assign the texture
                MipMappedFace.FromRawImage(ImageBuffer,xpart,ypart)
                
                self.fFaces.append(MipMappedFace)
                
            # copy the plBitmap fields from the first face onto this object
            self.fSpace = self.fFaces[0].fSpace
            self.fFlags = self.fFaces[0].fFlags
           
            self.fCompressionType = self.fFaces[0].fCompressionType
            self.BitmapInfo.fDirectXInfo.fCompressionType = self.fFaces[0].BitmapInfo.fDirectXInfo.fCompressionType
            self.BitmapInfo.fDirectXInfo.fBlockSize = self.fFaces[0].BitmapInfo.fDirectXInfo.fBlockSize
            self.BitmapInfo.fUncompressedInfo.fType = self.fFaces[0].BitmapInfo.fUncompressedInfo.fType

            # now store the data in a file if texture_cache is enabled
            if (alcconfig.texture_cache):
                self.TexCache_Store()
        
        # now set that we processed it all
        self.Processed = 1
        
        
    def _Export(page,name,image,mipmapinfo,exportTexturesToPrp):
        resmgr = page.resmanager
        if not exportTexturesToPrp:
            page=resmgr.findPrp("Textures")
            if page==None:
                raise "    Textures PRP file not found"
        
        qmap=plCubicEnvironMap.FindCreate(page,name)
        qmap.data.MipMapInfo = mipmapinfo
        
        qmap.data.FromBlenderCubicMap(image)
        
        return qmap
    
    Export = staticmethod(_Export)

class plLayerAnimationBase(plLayerInterface):
    def __init__(self,parent,name="unnamed",type=0x00EF):
        plLayerInterface.__init__(self,parent,name,type)
        
        self.fEvalTime = -1.0
        self.fCurrentTime = -1.0
        self.fSegmentID = None
        self.fPreshadeColorCtl = None
        self.fRuntimeColorCtl = None
        self.fAmbientColorCtl = None
        self.fSpecularColorCtl = None
        self.fOpacityCtl = None
        self.fTransformCtl = None
    
    def _Find(page,name):
        return page.find(0x00EF,name,0)
    Find = staticmethod(_Find)
    
    def _FindCreate(page,name):
        return page.find(0x00EF,name,1)
    FindCreate = staticmethod(_FindCreate)
    
    def read(self, stream):
        plLayerInterface.read(self,stream)
        self.fPreshadeColorCtl = PrpController(stream.Read16(), self.getVersion())
        self.fPreshadeColorCtl.read(stream)
        self.fRuntimeColorCtl = PrpController(stream.Read16(), self.getVersion())
        self.fRuntimeColorCtl.read(stream)
        self.fAmbientColorCtl = PrpController(stream.Read16(), self.getVersion())
        self.fAmbientColorCtl.read(stream)
        self.fSpecularColorCtl = PrpController(stream.Read16(), self.getVersion())
        self.fSpecularColorCtl.read(stream)
        self.fOpacityCtl = PrpController(stream.Read16(), self.getVersion())
        self.fOpacityCtl.read(stream)
        self.fTransformCtl = PrpController(stream.Read16(), self.getVersion())
        self.fTransformCtl.read(stream)
    
    def write(self, stream):
        plLayerInterface.write(self,stream)
        self.fPreshadeColorCtl.write(stream)
        self.fRuntimeColorCtl.write(stream)
        self.fAmbientColorCtl.write(stream)
        self.fSpecularColorCtl.write(stream)
        self.fOpacityCtl.write(stream)
        self.fTransformCtl.write(stream)

class plLayerAnimation(plLayerAnimationBase):
    def __init__(self,parent=None,name="unnamed",type=0x0043):
        plLayerAnimationBase.__init__(self,parent,name,type)
        self.fTimeConvert = None
    
    def _Find(page,name):
        return page.find(0x0043,name,0)
    Find = staticmethod(_Find)
    
    def _FindCreate(page,name):
        return page.find(0x0043,name,1)
    FindCreate = staticmethod(_FindCreate)
    
    def read(self, stream):
        plLayerAnimationBase.read(self, stream)
        self.fTimeConvert.read(stream)
    
    def write(self, stream):
        plLayerAnimationBase.write(self, stream)
        self.fTimeConvert.write(stream)
    
    def FromBlender(self,obj,mat,mtex,chan = 0):
        print "   [LayerAnimation %s]"%(str(self.Key.name))
        # We have to grab the animation stuff here...
        ipo = mat.ipo
        ipo.channel = chan
        endFrame = 0
        
        if (Ipo.MA_OFSX in ipo) and (Ipo.MA_OFSY in ipo) and (Ipo.MA_OFSZ in ipo):
            KeyList = []
            
            # We need to get the list of BezCurves
            # Then get the value for each and create a point3
            # Then store that in a frame and store than in the list
            curves = ipo[Ipo.MA_OFSX].bezierPoints
            for frm in range(len(curves)):
                frame = alc_AnimClasses.hsMatrix44Key()
                num = curves[frm].pt[0]
                if num == 1:
                    num = 0
                frame.fFrameNum = int(num)
                frame.fFrameTime = num/30.0
                
                matx = hsMatrix44()
                matx.translate((curves[frm].pt[1], ipo[Ipo.MA_OFSY].bezierPoints[frm].pt[1], ipo[Ipo.MA_OFSZ].bezierPoints[frm].pt[1]))
                
                frame.fValue = matx
                KeyList.append(frame)
            
            self.fTransformCtl = alc_AnimClasses.PrpController(0x0234, self.getVersion())
            self.fTransformCtl.data.fKeys = KeyList
            endFrame = curves[-1].pt[0]
        else:
            self.fTransformCtl = alc_AnimClasses.PrpController(0x8000, self.getVersion())
        
        ##MAJOR HACK HERE
        self.fPreshadeColorCtl = alc_AnimClasses.PrpController(0x8000, self.getVersion())
        self.fRuntimeColorCtl = alc_AnimClasses.PrpController(0x8000, self.getVersion())
        self.fAmbientColorCtl = alc_AnimClasses.PrpController(0x8000, self.getVersion())
        self.fSpecularColorCtl = alc_AnimClasses.PrpController(0x8000, self.getVersion())
        self.fOpacityCtl = alc_AnimClasses.PrpController(0x8000, self.getVersion())
        
        self.fTimeConvert = alc_AnimClasses.plAnimTimeConvert()
        self.fTimeConvert.fFlags |= 0x22
        self.fTimeConvert.fBegin = 0.0
        self.fTimeConvert.fEnd = endFrame/30.0
        self.fTimeConvert.fLoopEnd = endFrame/30.0
        self.fTimeConvert.fLoopBegin = 0.0
