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
#from prp_LogicClasses import *
from prp_Functions import *
from prp_ConvexHull import *
from prp_VolumeIsect import *
from prp_AlcScript import *
from prp_RefParser import *
from prp_Messages import *
import prp_Config, prp_HexDump

class plPostEffectMod(plSingleModifier):
    def __init__(self,parent,name="unnamed",type=0x007A):
        plSingleModifier.__init__(self,parent,name,type)

        self.fState = hsBitVector()
        self.fHither = 1.0
        self.fYon = 100.0
        self.fFOVX = 45.00
        self.fFOVY = 33.75
        self.fNodeKey = UruObjectRef(self.getVersion())
        self.fC2W = hsMatrix44()
        self.fW2C = hsMatrix44()

    def _Find(page,name):
        return page.find(0x007A,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x007A,name,1)
    FindCreate = staticmethod(_FindCreate)

    def read(self,stream):
        plSingleModifier.read(self,stream)

        self.fState.read(stream)
        self.fHither = stream.ReadFloat()
        self.fYon = stream.ReadFloat()
        self.fFOVX = stream.ReadFloat()
        self.fFOVY = stream.ReadFloat()

        self.fNodeKey.read(stream)

        self.fW2C.read(stream)
        self.fC2W.read(stream)

    def write(self,stream):
        plSingleModifier.write(self,stream)

        self.fState.write(stream)

        stream.WriteFloat(self.fHither)
        stream.WriteFloat(self.fYon)
        stream.WriteFloat(self.fFOVX)
        stream.WriteFloat(self.fFOVY)

        self.fNodeKey.write(stream)

        self.fW2C.write(stream)
        self.fC2W.write(stream)

    def export_obj(self, obj, sceneNode):
        script = AlcScript.objects.Find(obj.name)

        m = getMatrix(obj)
        m.transpose()
        self.fC2W.set(m)
        m.invert()
        self.fW2C.set(m)

        self.fNodeKey = sceneNode

        self.fHither = float(FindInDict(script, "camera.hither", 1.0))
        self.fYon = float(FindInDict(script, "camera.yon", 100.0))

class pfGUIColorScheme:
    def __init__(self):
        self.fForeColor = RGBA(1.0,1.0,1.0,1.0,type=1)
        self.fBackColor = RGBA(0.0,0.0,0.0,0.0,type=1)
        self.fSelForeColor = RGBA(1.0,1.0,1.0,1.0,type=1)
        self.fSelBackColor = RGBA(0.0,0.0,1.0,1.0,type=1)
        self.fTransparent = 0
        self.fFontFace = "Times New Roman"
        self.fFontSize = 10
        self.fFontFlags = 0x0

    def read(self, stream):
        self.fForeColor.read(stream)
        self.fBackColor.read(stream)
        self.fSelForeColor.read(stream)
        self.fSelBackColor.read(stream)
        self.fTransparent = stream.Read32()
        self.fFontFace = stream.ReadSafeString()
        self.fFontSize = stream.ReadByte()
        self.fFontFlags = stream.ReadByte()

    def write(self,stream):
        self.fForeColor.write(stream)
        self.fBackColor.write(stream)
        self.fSelForeColor.write(stream)
        self.fSelBackColor.write(stream)
        stream.Write32(self.fTransparent)
        stream.WriteSafeString(self.fFontFace)
        stream.WriteByte(self.fFontSize)
        stream.WriteByte(self.fFontFlags)

class pfGUIDialogMod(plSingleModifier):
    def __init__(self,parent=None, name="unnamed", type=0x0098):
       plSingleModifier.__init__(self,parent,name,type)

       self.fTagID = 0
       self.fVersion = 0
       self.fName = "untitled"
       self.fColorScheme = pfGUIColorScheme()
       self.fProc = UruObjectRef(self.getVersion())
       self.fSceneNodeKey = UruObjectRef(self.getVersion())
       self.fRenderMod = UruObjectRef(self.getVersion())
       self.fControls = hsTArray([0x00A1,0x0062,0x00A3,0x00A5,0x00AA, 0x00AB,0x00AC,0x00AF,0x00B0,0x00B1,0x00B9,0x00BA,0x00BB,0x00BD,0x00EE,0x010C,0x011A,], self.getVersion())

    def _Find(page,name):
        return page.find(0x0098,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0098,name,1)
    FindCreate = staticmethod(_FindCreate)

    def read(self,stream):
        plSingleModifier.read(self,stream)

        self.fRenderMod.read(stream)
        self.fName = stream.read(128)
        count = stream.Read32()
        for i in range(count):
            control = UruObjectRef(self.getVersion())
            control.read(stream)
            self.fControls.append(control)

        self.fTagID = stream.Read32()
        self.fProc.read(stream)

        self.fVersion = stream.Read32()
        self.fColorScheme.read(stream)
        self.fSceneNodeKey.read(stream)

    def write(self,stream):
        plSingleModifier.write(self,stream)

        self.fRenderMod.write(stream)
        total = 128
        size = total - len(self.fName)
        stream.write(self.fName)
        for i in range(size):
            stream.WriteByte(0x00)

        stream.Write32(len(self.fControls))
        for ctrl in self.fControls:
            ctrl.write(stream)

        stream.Write32(self.fTagID)
        self.fProc.write(stream)

        stream.Write32(self.fVersion)
        self.fColorScheme.write(stream)
        self.fSceneNodeKey.write(stream)

    def export_obj(self,obj,sceneNode):
        script = AlcScript.objects.Find(obj.name)

        self.fSceneNodeKey = sceneNode

        self.fName = FindInDict(script, "dialog.name", "Untitled")
        self.fTagID = int(FindInDict(script, "dialog.id", 0))
        self.fVersion = int(FindInDict(script, "dialog.version", 0))

        ctrllist = list(FindInDict(script,"dialog.controls",[]))
        refparser = ScriptRefParser(self.getRoot(),str(obj.name),None,[])
        for ctrl in ctrllist:
            ref = refparser.MixedRef_FindCreateRef(ctrl)
            self.fControls.append(ref)

        pem = FindInDict(script, "dialog.camera", "")
        self.fRenderMod = refparser.MixedRef_FindCreateRef(pem)

        modal = bool(FindInDict(script, "dialog.modal", "false"))
        if modal:
            self.bitVector.SetBit(0x0)

        self.fColorScheme.fFontFace = FindInDict(script, "dialog.fontface", "Times New Roman")
        self.fColorScheme.fFontSize = int(FindInDict(script, "dialog.fontsize", 10))
        self.fColorScheme.fTransparent = bool(FindInDict(script, "dialog.transparent", "false"))

