#
# $Id: alc_GeomClasses.py 876 2007-12-15 22:15:11Z Paradox $
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

# Help library

try:
    import Blender
except ImportError:
    pass

import struct, array, StringIO
from alc_AbsClasses import *

class hsMatrix33:
    def __init__(self):
        self.identity()
    
    
    def get(self):
        self.update()
        return self.vmatrix
    
    
    def read(self,buf):
        for i in range(3):
            for j in range(3):
                self.matrix[i][j] = buf.ReadFloat()
        
        self.update()
    
    
    def write(self,buf):
        for i in range(3):
            for j in range(3):
                buf.WriteFloat(self.matrix[i][j])

    
    def update(self):
        a = [self.matrix[0][0],self.matrix[0][1],self.matrix[0][2]]
        b = [self.matrix[1][0],self.matrix[1][0],self.matrix[1][2]]
        c = [self.matrix[2][0],self.matrix[2][0],self.matrix[2][2]]
        
        try:
            self.vmatrix = Blender.Mathutils.Matrix(a,b,c)
        except NameError:
            pass
    
    
    def identity(self):
        self.matrix=[[1,0,0],[0,1,0],[0,0,1]]
        self.update()


class hsMatrix44:
    def __init__(self):
        self.matrix=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
        self.update()
    
    
    def read(self,buf):
        for i in range(4):
            for j in range(4):
                self.matrix[i][j] = buf.ReadFloat()
        self.update()
    
    
    def write(self,buf):
        for i in range(4):
            for e in range(4):
                buf.WriteFloat(self.matrix[i][e])
    
    
    def update(self):
        a=[self.matrix[0][0],self.matrix[0][1],self.matrix[0][2],self.matrix[0][3]]
        b=[self.matrix[1][0],self.matrix[1][1],self.matrix[1][2],self.matrix[1][3]]
        c=[self.matrix[2][0],self.matrix[2][1],self.matrix[2][2],self.matrix[2][3]]
        d=[self.matrix[3][0],self.matrix[3][1],self.matrix[3][2],self.matrix[3][3]]
        try:
            self.vmatrix=Blender.Mathutils.Matrix(a,b,c,d)
        except NameError:
            pass
    
    
    def get(self):
        self.update()
        return(self.vmatrix)
    
    
    def X(self):
        return self.matrix[0][3]
    
    
    def Y(self):
        return self.matrix[1][3]
    
    
    def Z(self):
        return self.matrix[2][3]
    
    
    def set(self,matrix):
        for j in range(4):
            for k in range(4):
                self.matrix[j][k]=matrix[j][k]
        self.update()
    
    def __str__(self):
        out="{\n"
        for j in range(4):
            out = out + "["
            for k in range(4):
                val = "%10.2f" %self.matrix[j][k]
                out = out + val + ","
            out = out + "]\n"
        out = out + "}"
        return out
    
    
    def identity(self):
        self.matrix=[[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
        self.update()
    
    
    def transformvector(self,v):
        m=self.matrix
        x, y, z = v
        x = m[0][0]*x + m[0][1]*y + m[0][2]*z + m[0][3]
        y = m[1][0]*x + m[1][1]*y + m[1][2]*z + m[1][3]
        z = m[2][0]*x + m[2][1]*y + m[2][2]*z + m[2][3]
        return [x,y,z]

    def __mul__(self, m):
        # matrix multiplication :)
        sm = self.matrix
        mm = m.matrix
        om = hsMatrix44()
        for row in range(4):
            for col in range(4):
                om.matrix[row][col] = 0
                for index in range(4):
                    om.matrix[row][col] += sm[row][index] * mm[index][col]
        return om

    def rotate(self, x, y, z, r):
        # axis angle rotation r = radians (rotates self)
        c = math.cos(r)
        s = math.sin(r)
        t = 1 - c
        rot = hsMatrix44()
        rot.matrix[0] = [(t*x*x)+c, (t*x*y)-(z*s), (t*x*z)+(y*s), 0]
        rot.matrix[1] = [(t*x*y)+(z*s), (t*y*y)+c, (t*y*z)-(x*s), 0]
        rot.matrix[2] = [(t*x*z)-(y*s), (t*y*z)+(x*s), (t*z*z)+c, 0]
        rot.matrix[3] = [0, 0, 0, 1]
        self.matrix = (self * rot).matrix
    
    def scale(self, x, y, z):
        # 3 axis scale (scales self)
        scale = hsMatrix44()
        scale.matrix[0] = [x, 0, 0, 0]
        scale.matrix[1] = [0, y, 0, 0]
        scale.matrix[2] = [0, 0, z, 0]
        scale.matrix[3] = [0, 0, 0, 1]
        self.matrix = (self * scale).matrix
    
    def translate(self,v):
        m=self.matrix
        x, y, z = v
        m[0][3] += x
        m[1][3] += y
        m[2][3] += z
        self.matrix=m


class RGBA:
    def __init__(self,r=255,g=255,b=255,a=255,type=0):
        self.r=r
        self.g=g
        self.b=b
        self.a=a
        self.type=type
        #type 0 -> U32 format
        #type 1 -> 4 floats
    
    
    def __repr__(self):
        return (self.r,self.g,self.b,self.a)
    
    
    def __str__(self):
        if self.type==0:
            return "%03i,%03i,%03i,%03i" %(self.r,self.g,self.b,self.a)
        else:
            return "%10.2f %10.2f %10.2f %10.2f" %(self.r,self.g,self.b,self.a)
    
    
    def set(self,r=255,g=255,b=255,a=255):
        self.r=r
        self.g=g
        self.b=b
        self.a=a
    
    
    def uset(self,r=255,g=255,b=255,a=255):
        self.r=r
        self.g=g
        self.b=b
        self.a=a
    
    
    def get(self):
        return self.__repr__()
    
    
    def uget(self):
        return (self.r,self.g,self.b,self.a)
    
    
    def read(self,buf):
        self.r = buf.ReadFloat()
        self.g = buf.ReadFloat()
        self.b = buf.ReadFloat()
        self.a = buf.ReadFloat()
    
    
    def write(self,buf):
        buf.WriteFloat(self.r)
        buf.WriteFloat(self.g)
        buf.WriteFloat(self.b)
        buf.WriteFloat(self.a)
    
    def equals(col):
        if self.r == col.r and self.b == col.b and self.g == col.g and self.a == col.a:
            return True
        else:
            return False


class Vertex:
    def __init__(self,x=0,y=0,z=0):
        self.x=x
        self.y=y
        self.z=z
        #normals
        self.nx=0
        self.ny=0
        self.nz=0
        #Base vertex (x=px + offset/1024.0), so ((x-px)*1024 = offset)
        ##self.base=[0,0,0]
        ##self.off=[0,0,0]
        #weights - bone influence (0-1)
        self.blend=[]
        ###self.blendbase=[]
        ###self.blendoff=[]
        #bones - link to bone
        self.bones=[]
        #color
        self.color=RGBA()
        #Texture coordinates
        self.tex=[]
        ###self.texbase=[]
        ###self.texoff=[]
    
    
    def isequal(self,v):
        return(self.x==v.x and self.y==v.y and self.z==v.z)
        
    def isfullyequal(self,v):
        # this check goes in order of importance, to ensure quick loading
        
        # check vertex location
        if not (self.x==v.x and self.y==v.y and self.z==v.z):
            return False
        
        # check all uv coordinates
        if len(self.tex) != len(v.tex):
            return False
        else:
            for i in range(len(self.tex)):
                if not (self.tex[i][0] == v.tex[i][0] and self.tex[i][1] == v.tex[i][1]):
                    return False
        
        # check vertex color
        
        if not self.color.equals(v.color):
            return False

        # check blend weights
        if len(self.blend) != len(v.blend):
            return False
        else:
            for i in range(len(self.blend)):
                if not (self.blend[i] == v.blend[i]):
                    return False
        
        # check skin indices
        if len(self.bones) != len(v.bones):
            return False
        else:
            for i in range(len(self.bones)):
                if not (self.bones[i] == v.bones[i]):
                    return False
                
        # check vertex normal
        if not (self.nx==v.nx and self.ny==v.ny and self.nz==v.nz):
            return False

        # if we arrive here, the vertex is the same
        return True
            
    
    
    

    
    def __repr__(self):
        return (self.x,self.y,self.z)
    
    
    def __str__(self):
        return "%10.3f,%10.3f,%10.3f" % (self.x,self.y,self.z)
    
    
    def read(self,buf):
        self.x = buf.ReadFloat()
        self.y = buf.ReadFloat()
        self.z = buf.ReadFloat()
    
    
    def write(self,buf):
        buf.WriteFloat(self.x)
        buf.WriteFloat(self.y)
        buf.WriteFloat(self.z)
    
    
    def X(self):
        return self.x
    
    
    def Y(self):
        return self.y
    
    
    def Z(self):
        return self.z
    
    
    def transform(self,matrix):
        m=matrix.matrix
        x = m[0][0]*self.x + m[0][1]*self.y + m[0][2]*self.z + m[0][3]
        y = m[1][0]*self.x + m[1][1]*self.y + m[1][2]*self.z + m[1][3]
        z = m[2][0]*self.x + m[2][1]*self.y + m[2][2]*self.z + m[2][3]
        self.x=x
        self.y=y
        self.z=z

        nx = m[0][0]*self.nx + m[0][1]*self.ny + m[0][2]*self.nz #+ m[0][3] # Normals need to be rotated, not translated
        ny = m[1][0]*self.nx + m[1][1]*self.ny + m[1][2]*self.nz #+ m[1][3] # Normals need to be rotated, not translated
        nz = m[2][0]*self.nx + m[2][1]*self.ny + m[2][2]*self.nz #+ m[2][3] # Normals need to be rotated, not translated
        self.nx=nx
        self.ny=ny
        self.nz=nz


    def setVector(self,vector):
        self.x = vector.x
        self.y = vector.y
        self.z = vector.z
    
    def getVector(self):
        return Blender.Mathutils.Vector(self.x,self.y,self.z,1)


class Vertex4:
    def __init__(self):
        self.f1 = 0
        self.f2 = 0
        self.f3 = 0
        self.f4 = 0
    
    
    def read(self,buf):
        self.f1 = buf.ReadFloat()
        self.f2 = buf.ReadFloat()
        self.f3 = buf.ReadFloat()
        self.f4 = buf.ReadFloat()
    
    
    def write(self,buf):
        buf.WriteFloat(self.f1)
        buf.WriteFloat(self.f2)
        buf.WriteFloat(self.f3)
        buf.WriteFloat(self.f4)

class hsQuat:
    def __init__(self,w=1,x=0,y=0,z=0):
        self.w = w
        self.x = x
        self.y = y
        self.z = z
        
    def isequal(self,q):
        return(self.w == q.w and self.x==q.x and self.y==q.y and self.z==q.z)
    
    def __repr__(self):
        return (self.w,self.x,self.y,self.z)
    
    
    def __str__(self):
        return "%10.3f,%10.3f,%10.3f,%10.3f" % (self.w,self.x,self.y,self.z)
    
    
    def read(self,stream):
        self.w = stream.ReadFloat()
        self.x = stream.ReadFloat()
        self.y = stream.ReadFloat()
        self.z = stream.ReadFloat()
    
    def write(self,stream):
        stream.WriteFloat(self.w)
        stream.WriteFloat(self.x)
        stream.WriteFloat(self.y)
        stream.WriteFloat(self.z)
    
    def W(self):
        return self.w
    
    def X(self):
        return self.x
    
    def Y(self):
        return self.y
    
    def Z(self):
        return self.z
    
    def setQuat(self,quat):
        self.w = quat.w
        self.x = quat.x
        self.y = quat.y
        self.z = quat.z
    
    def getQuat(self):
        return Blender.Mathutils.Quaternion(self.w,self.x,self.y,self.z)

class hsBounds:
    def __init__(self):
        self.mode = 0 # formerly known as self.i1
    
    
    def read(self,buf):
        self.mode = buf.Read32()
    
    
    def write(self,buf):
        buf.Write32(self.mode)


class hsBounds3(hsBounds):
    def __init__(self):
        hsBounds.__init__(self)
        self.min = Vertex()
        self.max = Vertex()
    
    
    def read(self,buf):
        hsBounds.read(self,buf)
        self.min.read(buf)
        self.max.read(buf)
    
    
    def write(self,buf):
        hsBounds.write(self,buf)
        self.min.write(buf)
        self.max.write(buf)


class hsBounds3Ext(hsBounds3):
    Flags =\
    { \
        "kAxisAligned"  :      0x1, \
        "kSphereSet"    :      0x2, \
        "kDistsSet"     :      0x4, \
        "kAxisZeroZero" : 0x100000, \
        "kAxisOneZero"  : 0x200000, \
        "kAxisTwoZero"  : 0x400000  \
    }

    def __init__(self):
        hsBounds3.__init__(self)
        self.flags = 0 | hsBounds3Ext.Flags["kAxisAligned"]

        self.corner = Vertex() 
        self.diff = [] 
        self.f64 = []
        for i in range(3):
            self.diff.append(Vertex())
            floatList = []
            floatList.append(0.0)
            floatList.append(0.0)
            self.f64.append(floatList)
    
    
    def __str__(self):
        return "f:%08X,min:%s,max:%s,corner:%s,diff:[(%s),(%s),(%s)]" %\
               (self.flags,str(self.min),str(self.max),str(self.corner),\
                str(self.diff[0]),str(self.diff[1]),str(self.diff[2]))

    
    def read(self,buf):
        self.flags = buf.Read32()
        hsBounds3.read(self,buf)
        assert(self.mode==0x00)
        if not(self.flags & hsBounds3Ext.Flags["kAxisAligned"]):
            self.corner.read(buf)
            for i in range(3):
                self.diff[i].read(buf)
                self.f64[i][0] = buf.ReadFloat()
                self.f64[i][1] = buf.ReadFloat()
    
    
    def write(self,buf):
        buf.Write32(self.flags)
        hsBounds3.write(self,buf)
        if not(self.flags & hsBounds3Ext.Flags["kAxisAligned"]):
            self.corner.write(buf)
            for i in range(3):
                self.diff[i].write(buf)
                buf.WriteFloat(self.f64[i][0])
                buf.WriteFloat(self.f64[i][1])


class plGBufferTriangle:
    def __init__(self):
        self.s1 = 0
        self.s2 = 0
        self.s3 = 0
        self.s4 = 0
        self.scalar = Vertex()
    
    
    def read(self,buf):
        self.s1 = buf.Read16()
        self.s2 = buf.Read16()
        self.s3 = buf.Read16()
        self.s4 = buf.Read16()
        self.scalar.read(buf)
    
    
    def write(self,buf):
        buf.Write16(self.s1)
        buf.Write16(self.s2)
        buf.Write16(self.s3)
        buf.Write16(self.s4)
        self.scalar.write(buf)


class plFogEnvironment(hsKeyedObject):
    FogType = \
    { \
      "kLinearFog"  : 0, \
      "kExpFog"     : 1, \
      "kExp2Fog"    : 2, \
      "kNoFog"      : 3  \
    }

    def __init__(self,parent,name="unnamed",type=0x0050):
        hsKeyedObject.__init__(self,parent,name,type)
        self.fType = plFogEnvironment.FogType["kNoFog"]
        self.fStart = 0
        self.fEnd = 0
        self.fEnd = 1
        self.fColor = RGBA()
    
    def read(self,stream): 
        hsKeyedObject.read(self,stream)
        self.fType = stream.ReadByte()
        self.fStart = stream.ReadFloat()
        self.fEnd = stream.ReadFloat()
        self.fDensity = stream.ReadFloat()
        self.fColor.read(stream)
    
    
    def write(self,stream):
        hsKeyedObject.write(self,stream)
        stream.WriteByte(self.fType)
        stream.WriteFloat(self.fStart)
        stream.WriteFloat(self.fEnd)
        stream.WriteFloat(self.fDensity)
        self.fColor.write(stream)
    



class plSpan:
    Props = \
    { \
        "kLiteMaterial"             : 0x0, \
        "kPropNoDraw"               : 0x1, \
        "kPropNoShadowCast"         : 0x2, \
        "kPropFacesSortable"        : 0x4, \
        "kPropVolatile"             : 0x8, \
        "kWaterHeight"             : 0x10, \
        "kPropRunTimeLight"        : 0x20, \
        "kPropReverseSort"         : 0x40, \
        "kPropHasPermaLights"      : 0x80, \
        "kPropHasPermaProjs"      : 0x100, \
        "kLiteVtxPreshaded"       : 0x200, \
        "kLiteVtxNonPreshaded"    : 0x400, \
        "kLiteProjection"         : 0x800, \
        "kLiteShadowErase"       : 0x1000, \
        "kLiteShadow"            : 0x2000, \
        "kPropMatHasSpecular"   : 0x10000, \
        "kPropProjAsVtx"        : 0x20000, \
        "kPropSkipProjection"   : 0x40000, \
        "kPropNoShadow"         : 0x80000, \
        "kPropForceShadow"     : 0x100000, \
        "kPropDisableNormal"   : 0x200000, \
        "kPropCharacter"       : 0x400000, \
        "kPartialSort"         : 0x800000, \
        "kVisLOS"             : 0x1000000  \
    }

    plSpanType = \
    {
        "kSpan"         :  0x0, \
        "kVertexSpan"   :  0x1, \
        "kIcicleSpan"   :  0x2, \
        "kIcicle2Span"  :  0x4, \
        "kParticleSpan" :  0x8, \
        "kParticleSet"  : 0x10  \
    }
    
    def __init__(self,ver=5):
        self.fSubType = 0 #DWORD
        self.fMaterialIdx = 0 #DWORD
        self.fLocalToWorld = hsMatrix44() #hsMatrix444
        self.fWorldToLocal = hsMatrix44() #hsMatrix444
        self.fNumMatrices = 0 #CHAR, but read as int; formerly knowns as self.c98
        self.fBaseMatrix = 0 #DWORD; formerly known as self.i94
        self.fProps = 0 #DWORD
        self.fLocalBounds = hsBounds3Ext() #hsBounds3Ext
        self.fWorldBounds = hsBounds3Ext() #hsBounds3Ext
        self.fLocalUVWChans = 0 #WORD
        self.fMaxeBoneIdx = 0 #WORD
        self.fPenBoneIdx = 0 #WORD
        self.fMinDist = -1 #FLOAT
        self.fMaxDist = -1 #FLOAT
        self.fWaterHeight = 0 #FLOAT

        # Not read or written in plSpan::Read or written in plSpan:Write

        # Was self.fog
        self.fFogEnvironment = UruObjectRef(ver) #plFogEnvironment //See plDrawableSpans
        # Was self.lights1
        self.fPermaLights = hsTArray([0x55,0x56,0x57,0x6A],ver) #plLightInfo refs
        # Was self.lights2
        self.fPermaProjs = hsTArray([0x55,0x56,0x57,0x6A],ver) #plLightInfo refs
    
    
    def read(self,buf):
        self.fSubType = buf.Read32() # was self.subDrawableType
        self.fMaterialIdx = buf.Read32() # was self.subMaterialType
        self.fLocalToWorld.read(buf) # was self.L2WMatrix
        self.fWorldToLocal.read(buf) # was self.W2LMatrix
        self.fProps = buf.Read32() # was self.flags
 
        self.fLocalBounds.read(buf) # was self.bounds1
        self.fWorldBounds.read(buf) # was self.bounds2
        self.fNumMatrices = buf.Read32() # was self.blendflag
        self.fBaseMatrix = buf.Read32() # was self.blendindex
        self.fLocalUVWChans = buf.Read16() # was self.s9A
        self.fMaxeBoneIdx = buf.Read16() # was self.s9C
        self.fPenBoneIdx = buf.Read16() # was self.s9E

        self.fMinDist = buf.ReadFloat() # was self.f1A8
        self.fMinDist = buf.ReadFloat() # was self.f1AC 
        if (self.fProps & plSpan.Props["kWaterHeight"]):
            self.fWaterHeight = buf.ReadFloat() # was self.f1B0
    
    
    def write(self,buf):
        # RTR: Temporary 
        self.fProps = self.fProps & ~plSpan.Props["kPropHasPermaLights"]#0x080 #0x55,0x56,0x57
        self.fProps = self.fProps & ~plSpan.Props["kPropHasPermaProjs"]#0x100 #0x55,0x56,0x57
        if len(self.fPermaLights)!=0:
            self.fProps |= plSpan.Props["kPropHasPermaLights"]#0x080
        if len(self.fPermaProjs)!=0:
            self.fProps |= plSpan.Props["kPropHasPermaProjs"]#0x100
        # RTR: end temporary

        buf.Write32(self.fSubType)
        buf.Write32(self.fMaterialIdx)
        self.fLocalToWorld.write(buf)
        self.fWorldToLocal.write(buf)
        buf.Write32(self.fProps)
        self.fLocalBounds.write(buf)
        self.fWorldBounds.write(buf)
        buf.Write32(self.fNumMatrices)
        buf.Write32(self.fBaseMatrix)
        buf.Write16(self.fLocalUVWChans)
        buf.Write16(self.fMaxeBoneIdx)
        buf.Write16(self.fPenBoneIdx)
        buf.WriteFloat(self.fMinDist)
        buf.WriteFloat(self.fMinDist)
        if (self.fProps & plSpan.Props["kWaterHeight"]):
            buf.WriteFloat(self.fWaterHeight)


class plVertexSpan(plSpan):
    def __init__(self,ver=5):
        plSpan.__init__(self,ver)
        self.fGroupIdx = 0 #DWORD; formerly known as self.i230
        self.fVBufferIdx = 0 #DWORD
        self.fCellIdx = 0 #DWORD
        self.fCellOffset = 0 #DWORD; formerly known as self.i23C
        self.fVStartIdx = 0 #DWORD; formerly known as self.i240
        self.fVLength = 0 #DWORD; formerly known as self.i244
    
    
    def read(self,buf):
        plSpan.read(self,buf)
        self.fGroupIdx = buf.Read32() # Was self.vdbidx
        self.fVBufferIdx = buf.Read32() # Was self.i234
        self.fCellIdx = buf.Read32() # Was self.i238
        self.fCellOffset = buf.Read32() # Was self.vertexStart
        self.fVStartIdx = buf.Read32() # Was self.vertexStart2
        self.fVLength = buf.Read32() # Was self.vertexCount
    
    
    def write(self,buf):
        plSpan.write(self,buf)
        buf.Write32(self.fGroupIdx)
        buf.Write32(self.fVBufferIdx)
        buf.Write32(self.fCellIdx)
        buf.Write32(self.fCellOffset)
        buf.Write32(self.fVStartIdx)
        buf.Write32(self.fVLength)


class plIcicle(plVertexSpan):
    def __init__(self,ver=5):
        plVertexSpan.__init__(self,ver)
        self.fIBufferIdx = 0 #DWORD
        self.fIPackedIdx = 0 #DWORD
        self.fILength = 0 #DOWRD

        # Was self.triangles
        self.fSortData = [] #*plGBufferTriangle
    
    def read(self,buf):
        plVertexSpan.read(self,buf)
        self.fIBufferIdx = buf.Read32() # Was self.surfaceIdx
        self.fIPackedIdx = buf.Read32() # Was self.idxStart
        self.fILength = buf.Read32() # Was self.triCount

        self.fSortData = []
        if (self.fProps & plSpan.Props["kPropFacesSortable"]):
            for i in range(self.fILength / 3):
                self.fSortData[i] = plGBufferTriangle()
                self.fSortData[i].read(buf)
    
    
    def write(self,buf):
        plVertexSpan.write(self,buf)
        buf.Write32(self.fIBufferIdx)
        buf.Write32(self.fIPackedIdx)
        buf.Write32(self.fILength)
        if (self.fProps & plSpan.Props["kPropFacesSortable"]):
            for bufferTriangle in self.fSortData.vector:
                bufferTriangle.write(buf)


class plGeometrySpan:
    Const = \
    { \
        "kMaxNumUVChannels" : 8, \
        "kNoGroupID"        : 0  \
    }    
    
    Formats = \
    { \
        "kUVCountMask"      :  0xF, \
        "kSkinNoWeights"    :  0x0, \
        "kSkin1Weight"      : 0x10, \
        "kSkin2Weights"     : 0x20, \
        "kSkin3Weights"     : 0x30, \
        "kSkinWeightMask"   : 0x30, \
        "kSkinIndices"      : 0x40  \
    }
    Properties = \
    { \
        "kLiteMaterial"         :    0x0, \
        "kPropRunTimeLight"     :    0x1, \
        "kPropNoPreShade"       :    0x2, \
        "kLiteVtxPreshaded"     :    0x4, \
        "kLiteVtxNonPreshaded"  :    0x8, \
        "kLiteMask"             :    0xC, \
        "kRequiresBlending"     :   0x10, \
        "kInstanced"            :   0x20, \
        "kUserOwned"            :   0x40, \
        "kPropNoShadow"         :   0x80, \
        "kPropForceShadow"      :  0x100, \
        "kDiffuseFoldedIn"      :  0x200, \
        "kPropReverseSort"      :  0x400, \
        "kWaterHeight"          :  0x800, \
        "kFirstInstance"        : 0x1000, \
        "kPartialSort"          : 0x2000, \
        "kVisLOS"               : 0x4000, \
        "kPropNoShadowCast"     : 0x8000  \
    }

    def GetVertexSize(self,format):
        size = ((format & plGeometrySpans.Formats["kUVCountMask"]) + 2) * 12 #(sizeof(hsPoint3))
        
        if (format & plGeometrySpans.Formats["kSkinWeightMask"] == plGeometrySpans.Formats["kSkin1Weight"]):
            size = size + 4 # sizeof(float[1]); // 4
        elif (format & plGeometrySpans.Formats["kSkinWeightMask"] == plGeometrySpans.Formats["kSkin2Weights"]):
            size = size + 8 # sizeof(float[2]); // 8
        elif (format & plGeometrySpans.Formats["kSkinWeightMask"] == plGeometrySpans.Formats["kSkin3Weights"]):
            size = size + 12 # sizeof(float[3]); // 12
        if (format & plGeometrySpans.Formats["kSkinIndices"]):
            size = size + 4 # sizeof(uint32);   // 4
    
    
    def __init__(self):
        self.fLocalToWorld = hsMatrix44()
        self.fWorldToLocal = hsMatrix44()
        self.fLocalBounds = hsBounds3Ext()
        self.fLocalToOBB = hsMatrix44()
        self.fOBBToLocal = hsMatrix44()
        self.fBaseMatrix = 0 #DWORD
        self.fNumMatrices = 0 #CHAR
        self.fLocalUVWChans = 0 #WORD
        self.fMaxBoneIdx = 0 #WORD
        self.fPenBoneIdx = 0 #DWORD
        self.fMinDist = 0 #FLOAT
        self.fMaxDist = 0 #FLOAT
        self.fDecalLevel = 0
        self.fWaterHeight = 0 #FLOAT
        self.fFormat = 0 #CHAR
        self.fProps = 0 #DWORD
        self.fNumVerts = 0 #DWORD
        self.fNumIndices = 0 #DWORD

        self.fVertexData = []
        self.fMultColor = []
        self.fAddColor = []
        self.fDiffuseRGBA = []
        self.fSpecularRGBA = []
        self.fInstanceGroup = 0 #DWORD
        self.fInstanceRefIdx = 0

    
    def read(self,buf):
        self.fLocalToWorld.read(buf)           # Was self.m4
        self.fWorldToLocal.read(buf)          # Was self.m48
        self.fLocalBounds.read(buf)         # Was self.BE8C
        self.fOBBToLocal.read(buf)         # Was self.m234
        self.fLocalToOBB.read(buf)         # Was self.m1F0
        self.fBaseMatrix = buf.Read32()    # Was self.i190
        self.fNumMatrices = buf.ReadByte()  # Was self.c194
        self.fLocalUVWChans = buf.Read16()    # Was self.s196
        self.fMaxBoneIdx = buf.Read16()    # Was self.s198
        self.fPenBoneIdx = buf.Read16()    # Was self.il9C
        self.fMinDist = buf.ReadFloat() # Was self.f1A0
        self.fMaxDist = buf.ReadFloat() # Was self.f1A4
        self.fFormat = buf.ReadByte()  # Was self.c1AC
        self.fProps = buf.Read32()    # Was self.i1B0
        self.fNumVerts = buf.Read32()    # Was self.i1B4
        self.fNumIndices = buf.Read32()    # Was self.i1B8
        buf.Read32()      # Ignored
        buf.ReadByte()    # Ignored
        self.fDecalLevel = buf.Read32()
        if (self.fProps& plGeometrySpan.Properties["kWaterHeight"]):
            self.fWaterHeight = buf.ReadFloat() # Was self.f1A8

        self.fVertexData = []
        self.fMultColor = []
        self.fAddColor = []
        self.fDiffuseRGBA = []
        self.fSpecularRGBA = []
        if self.fNumVerts > 0:
            size = self.GetVertexSize(self.fFormat)
            self.fVertexData = buf.read(self.fNumVerts*size)
            
            for i in range(self.fNumVerts):
                cl = RGBA()
                cl.read(buf)
                self.fMultColor.append(cl)
                cl = RGBA()
                self.fAddColor.append(cl)
                cl.read(buf)

            self.fMultColor = []
            self.fAddColor = []
            
            for i in range(self.fNumVerts):
                cl = RGBA()
                cl.read(buf)
                self.fMultColor.append(cl) # Was self.v1D0
                cl = RGBA()
                self.fAddColor.append(cl) # Was self.v1D4
                cl.read(buf)
            
            for i in range(self.fNumVerts):
                self.fDiffuseRGBA.append(buf.Read32()) # Was self.ai1D8
            for i in range(self.fNumVerts):
                self.fSpecularRGBA.append(buf.Read32()) # Was self.ai1DC

        self.fIndexData = []
        for i in range(self.fNumIndices):
            self.fIndexData.append(buf.Read16()) # Was self.as1C8

        self.fInstanceGroup = buf.Read32()        # Was self.i1E4
        if(self.fInstanceGroup != 0):
            self.fInstanceRefIdx = buf.Read32()   # Was self.trash
    
    
    def write(self,buf):
        self.fLocalToWorld.write(buf)
        self.fWorldToLocal.write(buf)
        self.fLocalBounds.write(buf)
        self.fOBBToLocal.write(buf)
        self.LocalToOBB.write(buf)
        buf.Write32(self.fBaseMatrix)
        buf.WriteByte(self.fNumMatrices)
        buf.Write16(self.fLocalUVWChans)
        buf.Write16(self.fMaxBoneIdx)
        buf.Write16(self.fPenBoneIdx)
        buf.WriteFloat(self.fMinDist)
        buf.WriteFloat(self.fMaxDist)
        buf.WriteByte(self.fFormat)
        buf.Write32(self.fProps)
        buf.Write32(self.fNumVerts)
        buf.Write32(self.fNumIndices)
        buf.Write32(0)
        buf.WriteByte(0)
        buf.Write32(self.fDecalLevel)
        if (self.fProps& plGeometrySpan.Properties["kWaterHeight"]):
            buf.WriteFloat(self.fWaterHeight)
        
        if self.fNumVerts > 0:
            size = self.GetVertexSize(self.fFormat)
            buf.write(self.fVertexData)
                        
            for i in range(self.fNumVerts):
                self.fMultColor[i].write(buf)
                self.fAddColor[i].write(buf)
            
            for col in self.fNumVerts:
                buf.Write32(col.r)
                buf.Write32(col.g)
                buf.Write32(col.b)
                buf.Write32(col.a)
            for col in self.fNumVerts:
                buf.Write32(col.r)
                buf.Write32(col.g)
                buf.Write32(col.b)
                buf.Write32(col.a)

        for i in self.fIndexData:
            buf.Write16(i)

        buf.Write32(self.fInstanceGroup)
        if (self.fInstanceGroup != 0):
            buf.Write32(self.fInstanceRefIdx) 


class plCullPoly:
    def __init__(self):
        self.i0 = 0
        self.v18 = Vertex()
        self.f24 = 0
        self.v28 = Vertex()
        self.f34 = 0
        self.vV10 = []
    
    def read(self,buf):
        self.i0 = buf.Read32()
        self.v18.read(buf)
        self.f24 = buf.ReadFloat()
        self.v28.read(buf)
        self.f34 = buf.ReadFloat()
        vCount = buf.Read32()
        for i in range(vCount):
            vertex = Vertex()
            vertex.read(buf)
            self.vV10[i] = vertex
    
    def write(self,buf):
        buf.Write32(self.i0)
        self.v18.write(buf)
        buf.WriteFloat(self.f24)
        self.v28.write(buf)
        buf.WriteFloat(self.f34)
        vCount = len(self.vV10)
        buf.Write32(vCount)
        for i in range(vCount):
            self.vV10[i].write(buf)

        
class plRenderLevel:
    MajorLevel =  { \
        "kOpaqueMajorLevel"     : 0x0, \
        "kFBMajorLevel"         : 0x1, \
        "kDefRendMajorLevel"    : 0x2, \
        "kBlendRendMajorLevel"  : 0x4, \
        "kLateRendMajorLevel"   : 0x8  \
    }
    
    kMajorShift = 0x1C 
        
    MinorLevel =  { \
        "kOpaqueMinorLevel"     :        0x0, \
        "kFBMinorLevel"         :        0x1, \
        "kDefRendMinorLevel"    :        0x0, \
        "kBlendRendMinorLevel"  :        0x4, \
        "kLateRendMinorLevel"   :        0x8, \
        "kMinorLevelMask"       : 0x0FFFFFFF, \
        "kAvatarRendMinorLevel" : 0x0FFFFFFE  \
    }

    # Following code is from CH source, through alternative one used here
    #
    #MinorLevel = {
    #    "kOpaqueMinorLevel":        0x0,
    #    "kDefRendMinorLevel":       0x0,
    #    "kMinorLevelMask":          0x0FFFFFFF,
    #    "kAvatarRendMinorLevel":    0x0FFFFFFE
    #}
    
    
    def __init__(self, major = MajorLevel["kOpaqueMajorLevel"], minor = MinorLevel["kDefRendMinorLevel"]):
        self.fLevel = (major << plRenderLevel.kMajorShift) | minor
    
    def setMajorLevel(self,major):
        self.fLevel |= (major << plRenderLevel.kMajorShift)

    def clearMajorLevel(self,major):
        self.fLevel &= ~(major << plRenderLevel.kMajorShift)
