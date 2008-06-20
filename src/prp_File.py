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

from prp_AnimClasses import *
from prp_AbsClasses import *
from prp_Classes import *
from prp_Stream import *
from prp_SndClasses import *
from prp_ObjClasses import *
from prp_MatClasses import *
from prp_DrawClasses import *
from prp_CamClasses import *
from prp_LogicClasses import *
from prp_Types import *
import struct

class PrpObject:
    def __init__(self,parent=None,type=None,version=None):
        self.attach = {} # an identifiable storage for attaching certain processing variables
        if parent!=None:
            self.parent=parent
            self.prp=parent.parent
            self.resmanager=parent.parent.resmanager
            self.page_id=parent.page_id
            self.page_type=parent.page_type
        else:
            self.prp=None
            self.parent=None
            self.resmanager=None
            self.page_id=0x00
            self.page_type=0x00
        if type==None:
            if parent!=None:
                self.type=parent.type
            else:
                self.type=0xFFFF
        else:
            self.type=type
        if version==None:
            if parent!=None:
                self.version=parent.parent.version
            else:
                self.version=5
        else:
            self.version=version
        self.data=None
        self.offset=0
        self.size=0
        self.isProcessed = None # Usable to see if a certain object has already been exported.

        #plFactory.Create()
        if self.version==5: #Uru Types
            if self.type==0x0000:
                self.data=plSceneNode(self)
            elif self.type==0x0001:
                self.data=plSceneObject(self)
            elif self.type==0x0004:
                self.data=plMipMap(self)
            elif self.type==0x0005:
                self.data=plCubicEnvironMap(self)
            elif self.type==0x0006:
                self.data=plLayer(self)
            elif self.type==0x0007:
                self.data=hsGMaterial(self)
            elif self.type==0x000D:
                self.data=plRenderTarget(self)
            elif self.type==0x000E:
                self.data=plCubicRenderTarget(self)
            elif self.type==0x0011:
                self.data=plAudioInterface(self)
            elif self.type==0x0012:
                self.data=plAudible(self)
            elif self.type==0x0014:
                self.data=plWinAudible(self)
            elif self.type==0x0015:
                self.data=plCoordinateInterface(self)
            elif self.type==0x0016:
                self.data=plDrawInterface(self)
            elif self.type==0x001C:
                self.data=plSimulationInterface(self)
            elif self.type==0x0029:
                self.data=plSoundBuffer(self)
            elif self.type==0x002B:
                self.data=plPickingDetector(self)
            elif self.type==0x002D:
                self.data=plLogicModifier(self)
            elif self.type==0x0032:
                self.data=plActivatorConditionalObject(self)
            elif self.type==0x0037:
                self.data=plObjectInBoxConditionalObject(self)
            elif self.type==0x003D:
                self.data=plSpawnModifier(self)
            elif self.type==0x003E:
                self.data=plFacingConditionalObject(self)
            elif self.type==0x003F:
                self.data=plHKPhysical(self)
            elif self.type==0x0040:
                self.data=plViewFaceModifier(self)
            elif self.type==0x0043:
                self.data=plLayerAnimation(self)
            elif self.type==0x0048:
                self.data=plSound(self)
            elif self.type==0x0049:
                self.data=plWin32Sound(self)
            elif self.type==0x004C:
                self.data=plDrawableSpans(self)
            elif self.type==0x0050:
                self.data=plFogEnvironment(self)
            elif self.type==0x0055:
                self.data=plDirectionalLightInfo(self)
            elif self.type==0x0056:
                self.data=plOmniLightInfo(self)
            elif self.type==0x0057:
                self.data=plSpotLightInfo(self)
            elif self.type==0x006A:
                self.data=plLimitedDirLightInfo(self)
            elif self.type==0x006C:
                self.data=plAGModifier(self)
            elif self.type==0x006D:
                self.data=plAGMasterMod(self)
            elif self.type==0x006F:
                self.data=plCameraRegionDetector(self)
            elif self.type==0x0077:
                self.data=plOneShotMod(self)
            elif self.type==0x007A:
                self.data=plPostEffectMod(self)
            elif self.type==0x007B:
                self.data=plObjectInVolumeDetector(self)
            elif self.type==0x007C:
                self.data=plResponderModifier(self)
            elif self.type==0x0084:
                self.data=plWin32StreamingSound(self)
            elif self.type==0x0087:
                self.data=plSoftVolume(self)
            elif self.type==0x0088:
                self.data=plSoftVolumeSimple(self)
            elif self.type==0x0089:
                self.data=plSoftVolumeComplex(self)
            elif self.type==0x008A:
                self.data=plSoftVolumeUnion(self)
            elif self.type==0x008B:
                self.data=plSoftVolumeIntersect(self)
            elif self.type==0x008C:
                self.data=plSoftVolumeInvert(self)
            elif self.type==0x0096:
                self.data=plWin32StaticSound(self)
            elif self.type==0x0099:
                self.data=plCameraBrain1(self)
            elif self.type==0x009B:
                self.data=plCameraModifier1(self)
            elif self.type==0x009E:
                self.data=plCameraBrain1_Avatar(self)
            elif self.type==0x009F:
                self.data=plCameraBrain1_Fixed(self)
            elif self.type==0x00A2:
                self.data=plPythonFileMod(self)
            elif self.type==0x00A4:
                self.data=plExcludeRegionModifier(self)
            elif self.type==0x00A6:
                self.data=plVolumeSensorConditionalObject(self)
            elif self.type==0x00A8:
                self.data=plMsgForwarder(self)
            elif self.type==0x00AE:
                self.data=plSittingModifier(self)
            elif self.type==0x00B2:
                self.data=plAvLadderMod(self)
            elif self.type==0x00B3:
                self.data=plCameraBrain1_FirstPerson(self)
            elif self.type==0x00C2:
                self.data=plCameraBrain1_Circle(self)
            elif self.type==0x00CB:
                self.data=plInterfaceInfoModifier(self)
            elif self.type==0x00CD:
                self.data=plArmatureEffectsMgr(self)
            elif self.type==0x00D2:
               self.data=plInstanceDrawInterface(self)
            elif self.type==0x00D3:
               self.data=plShadowMaster(self)
            elif self.type==0x00D4:
                self.data=plShadowCaster(self)
            elif self.type==0x00D5:
               self.data=plPointShadowMaster(self)
            elif self.type==0x00D6:
               self.data=plDirectShadowMaster(self)
            elif self.type==0x00E2:
               self.data=plHKSubWorld(self)
            elif self.type==0x00E7:
                self.data=plObjectInVolumeAndFacingDetector(self)
            elif self.type==0x00E8:
                self.data=plDynaFootMgr(self)
            elif self.type==0x00E9:
                self.data=plDynaRippleMgr(self)
            elif self.type==0x00EA:
                self.data=plDynaBulletMgr(self)
            elif self.type==0x00ED:
                self.data=plDynaPuddleMgr(self)
            elif self.type==0x00F1:
                self.data=plATCAnim(self)
            elif self.type==0x00F2:
                self.data=plAgeGlobalAnim(self)
            elif self.type==0x00F3:
                self.data=plSubWorldRegionDetector(self)
            elif self.type==0x00FB:
                self.data=plWaveSet7(self)
            elif self.type==0x00FC:
                self.data=plPanicLinkRegion(self)
            elif self.type==0x0106:
                self.data=plDynamicEnvMap(self)
            elif self.type==0x010A:
                self.data=plDynaRippleVSMgr(self)
            elif self.type==0x0111:
                self.data=plHardRegionPlanes(self)
            elif self.type==0x0112:
                self.data=plHardRegionComplex(self)
            elif self.type==0x0113:
                self.data=plHardRegionComplex(self) #plHardRegionUnion
            elif self.type==0x0114:
                self.data=plHardRegionComplex(self) #plHardRegionIntersect
            elif self.type==0x0115:
                self.data=plHardRegionComplex(self) #plHardRegionInvert
            elif self.type==0x0116:
                self.data=plVisRegion(self)
            elif self.type==0x0117:
                self.data=hsKeyedObject(self) #Not really... But close enough ;)
            elif self.type==0x011E:
                self.data=plRelevanceRegion(self)
            elif self.type==0x012E:
                self.data=plSwimRegion(self)
            elif self.type==0x012F:
                self.data=plSwimDetector(self)
            elif self.type==0x0133:
                self.data=plSwimRegionInterface(self)
            elif self.type==0x0134:
                self.data=plSwimCircularCurrentRegion(self)
            elif self.type==0x0136:
                self.data=plSwimStraightCurrentRegion(self)
            else:
                self.data=pRaw(self)
        elif self.version==6: #Myst 5 Types
            if self.type==0x0000:
                self.data=plSceneNode(self)
            elif self.type==0x0001:
                self.data=plSceneObject(self)
            elif self.type==0x0004:
                self.data=plMipMap(self)
            elif self.type==0x0005:
                self.data=plCubicEnvironMap(self)
            elif self.type==0x0006:
                self.data=plLayer(self)
            elif self.type==0x0007:
                self.data=hsGMaterial(self)
            elif self.type==0x0015:
                self.data=plCoordinateInterface(self)
            elif self.type==0x0016:
                self.data=plDrawInterface(self)
            elif self.type==0x0029:
                self.data=plSoundBuffer(self)
            elif self.type==0x0049:
                self.data=plDrawableSpans(self)
            else:
                self.data=pRaw(self,"unnamed",self.type)
        else:
            self.data=pRaw(self,"unnamed",self.type)


    def changePage(self,sseq,dseq,spage,dpage,stype,dtype):
        page1 = xPageId()
        page2 = xPageId()
        page1.setSeq(sseq)
        page1.setNum(spage)
        page1.setType(stype)
        page2.setSeq(dseq)
        page2.setNum(dpage)
        page2.setType(dtype)
        self.changePageRaw(page1.getRaw(),page2.getRaw(),stype,dtype)


    def changePageRaw(self,sid,did,stype,dtype):
        if self.page_type==stype and self.page_id==sid:
            self.page_type=dtype
            self.page_id=did
        self.data.changePageRaw(sid,did,stype,dtype)


    def read(self,buf,offset,size,verify=1):
        self.offset=offset
        self.size=size
        buf.seek(offset)
        self.data.validation=verify
        if True: # Handy debuggin tool, but not very useful to users....
            print "[Type: 0x%x]"%(self.type)

        try:
            self.data.read(buf,size)
        except TypeError,detail:
            #print "Hmm, typeerror:",detail
            self.data.read(buf)

        if verify:
            #print self.page_id,self.data.Key.page_id
            assert(self.page_id==self.data.Key.page_id)
            #print self.page_type, self.data.Key.page_type
            assert(self.page_type==self.data.Key.page_type)
            #print self.type, self.data.Key.object_type
            if self.type!=0xFFFF:
                assert(self.type==self.data.Key.object_type)
        if buf.tell()-offset!=size:
            print "WARNING: %s %i of %iunparsed bytes!" %(self.data.Key.name,size-(buf.tell()-offset),size)
            raise RuntimeError, "%s %i off %iunparsed bytes" %(self.data.Key.name,size-(buf.tell()-offset),size)


    def write(self,buf):
        self.data.Key.page_id=self.page_id
        self.data.Key.page_type=self.page_type
        if self.type!=0xFFFF:
            self.data.Key.object_type=self.type
        self.offset=buf.tell()
        self.data.write(buf)
        self.size=buf.tell()-self.offset


class PrpIndex:
    def __init__(self,parent,type=0):
        self.parent=parent
        self.type=type
        #if myst5
        ##self.size=0
        self.count=0
        self.objs=[]
        #
        self.page_id=parent.page_id
        self.page_type=parent.page_type


    def findobj(self,name,create=1):
        for i in self.objs:
            if i.data.Key.name==name:
                return i
        if not create:
            return None
        i = PrpObject(self,self.type)
        i.data.Key.name = name
        self.objs.append(i)
        return i

    def listobjects(self):
        list = []
        for o in self.objs:
            list.append(o)
        return list

    def changePage(self,sseq,dseq,spage,dpage,stype,dtype):
        page1 = xPageId()
        page2 = xPageId()
        page1.setSeq(sseq)
        page1.setNum(spage)
        page1.setType(stype)
        page2.setSeq(dseq)
        page2.setNum(dpage)
        page2.setType(dtype)
        self.changePageRaw(page1.getRaw(),page2.getRaw(),stype,dtype)


    def changePageRaw(self,sid,did,stype,dtype):
        if self.page_type==stype and self.page_id==sid:
            self.page_type=dtype
            self.page_id=did
        for i in self.objs:
            i.changePageRaw(sid,did,stype,dtype)

    def read(self,buf):
        self.type, = struct.unpack("H",buf.read(2))
        if self.parent.version==6: #myst5
            size, = struct.unpack("I",buf.read(4))
            extra, = struct.unpack("B",buf.read(1))
        self.count, = struct.unpack("I",buf.read(4))
        for i in range(self.count):
            dsc=plKey(self.parent.version,self.parent.age.getSeq())
            dsc.read(buf)
            #print dsc;
            assert(dsc.page_id==self.page_id)
            assert(dsc.page_type==self.page_type)
            assert(dsc.object_type==self.type)
            offset, size = struct.unpack("II",buf.read(8))
            me = buf.tell()
            #print dsc, offset, size, me
            o = PrpObject(self,self.type)
            o.read(buf,offset,size)
            #assert(o.data.Key==dsc)
            buf.seek(me)
            self.objs.append(o)


    def writeobjects(self,buf):
        self.count=len(self.objs)
        for o in self.objs:
            #print o.type,self.type
            #assert(o.data.Key.object_type==self.type and (o.type==0xFFFF or o.type==self.type))
            o.page_id=self.page_id
            o.page_type=self.page_type
            o.write(buf)


    def writeindex(self,buf):
        self.count=len(self.objs)
        buf.write(struct.pack("H",self.type))
        buf.write(struct.pack("I",self.count))
        for o in self.objs:
            o.data.Key.write(buf)
            buf.write(struct.pack("II",o.offset,o.size))


class PrpFileInfo:
    def __init__(self,parent=None,version=None,vmin=None):
        self.type="prp"
        if parent!=None:
            if parent.type=="rmgr":
                self.resmanager=parent
                self.age=None
                self.page=None
            elif parent.type=="age":
                self.resmanager=parent.resmanager
                self.age=parent
                self.page=None
            else:
                self.resmanager=parent.resmanager
                self.age=parent.age
                self.page=parent
            if version==None:
                version=self.resmanager.prp_version
            if vmin==None:
                vmin=self.resmanager.prp_min_ver
        else:
            if version==None:
                version=5
            if vmin==None:
                vmin=12
            self.resmanager=self
            self.age=None
            self.page=None
        #Format
        ### Plasma 2.0 - format ##
        self.version = version #U16
        #0x00 #U16
        self.page_id = 0
        self.page_type = 0
        self.name = Ustr("",self.version)
        #iustr District
        self.page = Ustr("",self.version)
        self.vmax = 63
        self.vmin = vmin #12 or 11
        # U32 0
        # U32 8
        #self.size = 0 #Data Checksum
        # U32 1st offset
        # U32 Index offset
        ##self.n = 0 #n items
        ##self.idx=[]
        ### Plasma 2.1 - format ##
        #U16 version 6
        #U16 count?
        self.list1=[] #list of plasma types
        self.list2=[] #flags, count, unk?
        #self.page_id=0 #U32
        #self.page_type=0 #Byte
        #self.age=m5str()
        #self.page=m5str()


    def read(self,buf):
        self.version, = struct.unpack("H",buf.read(2))
        if self.version not in[0x05,0x06]:
            raise RuntimeError, "Unsuported Prp version %i!"%self.version
        if self.version==0x06: #myst5
            count, = struct.unpack("H",buf.read(2))
            for i in range(count):
                type, flags = struct.unpack("HH",buf.read(4))
                self.list1.append(type)
                self.list2.append(flags)
        else: #uru
            blank, = struct.unpack("H",buf.read(2))
            assert(blank==0)
        self.page_id, = struct.unpack("I",buf.read(4))
        if self.version==0x06: #myst5
            self.page_type, = struct.unpack("B",buf.read(1))
        else: #uru
            self.page_type, = struct.unpack("H",buf.read(2))
        self.name.setType(self.version)
        self.name.read(buf)
        if self.version==0x05: #only on Uru
            district=Ustr("",self.version)
            district.read(buf)
            if str(district)!="District":
                raise RuntimeError,"Not a district"
        self.page.setType(self.version)
        self.page.read(buf)
        if self.version==0x06:
            #print "* Reading %s_%s %08X %02X" %(self.name,self.page,self.page_id,self.page_type)
            pass
        else:
            #print "* Reading %s_District_%s %08X %04X" %(self.name,self.page,self.page_id,self.page_type),
            self.vmax, self.vmin = struct.unpack("HH",buf.read(4))
            #print " Version %i,%i" %(self.vmax,self.vmin)
            unk1,unk2 = struct.unpack("II",buf.read(8))
            assert(unk1==0)
            assert(unk2==8)


    def getVersion(self):
        return self.version

    def getName(self):
        return str(self.name) + "_District_" + str(self.page)


    def getName(self):
        if self.version==6:
            return str(self.name) + "_" + str(self.page)
        else:
            return str(self.name) + "_District_" + str(self.page)

class PrpFile(PrpFileInfo):
    def __init__(self,parent=None,version=None,vmin=None):
        PrpFileInfo.__init__(self,parent,version,vmin)
        #the index
        self.idx=[]


    def findidx(self,type,create=1):
        for i in self.idx:
            if i.type==type:
                return i
        if not create:
            return None
        i = PrpIndex(self,type)
        self.idx.append(i)
        return i


    def changePage(self,sseq,dseq,spage,dpage,stype,dtype):
        page1 = xPageId()
        page2 = xPageId()
        page1.setSeq(sseq)
        page1.setNum(spage)
        page1.setType(stype)
        page2.setSeq(dseq)
        page2.setNum(dpage)
        page2.setType(dtype)
        self.changePageRaw(page1.getRaw(),page2.getRaw(),stype,dtype)


    def changePageRaw(self,sid,did,stype,dtype):
        if self.page_type==stype and self.page_id==sid:
            self.page_type=dtype
            self.page_id=did
        for i in self.idx:
            i.changePageRaw(sid,did,stype,dtype)


    def setPage(self,seq,page=0,flags=KAgeData,update=0):
        old_type=self.page_type
        old_id=self.page_id
        page1 = xPageId()
        page1.setSeq(seq)
        page1.setNum(page)
        page1.setFlags(flags)
        self.page_id=page1.getRaw()
        self.page_type=page1.getType()
        if update:
            self.changePageRaw(old_id,self.page_id,old_type,self.page_type)
        #print "page id: %08X" % self.page_id


    def setName(self,name):
        self.name.set(name)


    def setPageName(self,name):
        self.page.set(name)


    def read(self,buf):
        PrpFileInfo.read(self,buf)
        a, b, c = struct.unpack("III",buf.read(12))
        buf.seek(c) #go to the index
        # read the index
        n, = struct.unpack("I",buf.read(4))
        for i in range(n):
            obj = PrpIndex(self,self.page_type)
            obj.read(buf)
            self.idx.append(obj)


    def write(self,buf):
        buf.write(struct.pack("H",self.version))
        if self.version==0x06: #myst5
            count = len(self.list1)
            buf.write(struct.pack("H",count))
            for i in range(count):
                buf.write(struct.pack("HH",self.list1[i],self.list2[i]))
        else: #uru
            buf.write(struct.pack("H",0))
        buf.write(struct.pack("I",self.page_id))
        if self.version==0x06: #myst5
            buf.write(struct.pack("B",self.page_type))
        else: #uru
            buf.write(struct.pack("H",self.page_type))
        self.name.setType(self.version)
        self.name.write(buf)
        if self.version==0x05: #only on Uru
            district=Ustr("",self.version)
            district.set("District")
            district.write(buf)
        self.page.setType(self.version)
        self.page.write(buf)
        if self.version!=6:
            buf.write(struct.pack("HH",self.vmax,self.vmin))
            buf.write(struct.pack("II",0,8))
        start=buf.tell()
        buf.write(struct.pack("I",0))
        buf.write(struct.pack("I",buf.tell()+8))
        buf.write(struct.pack("I",0))
        size=buf.tell()
        #clean the index

        #seems that uru wants an ordered index
        oldidx=self.idx
        self.idx=[]
        while(len(oldidx)!=0):
            min=0xFFFF
            for o in oldidx:
                if len(o.objs)==0:
                    oldidx.remove(o)
                    continue
                if o.type<min:
                    min=o.type

            for o in oldidx:
                if o.type==min:
                    self.idx.append(o)
                    oldidx.remove(o)
                    break

        struct.pack("I",len(self.idx))
        for o in self.idx:
            o.page_id=self.page_id
            o.page_type=self.page_type
            o.writeobjects(buf)
        index=buf.tell()

        buf.write(struct.pack("I",len(self.idx)))
        for o in self.idx:
            o.writeindex(buf)
        size=buf.tell()-size
        end=buf.tell()
        buf.seek(start)
        buf.write(struct.pack("I",size))
        buf.seek(start+8)
        buf.write(struct.pack("I",index))
        #print "Index is at %08X" %index



    def find(self,type,name,create=0):
        idx=self.findidx(type,create)
        if idx==None:
            return None
        return(idx.findobj(name,create))

    def listobjects(self,type):
        list = []
        for idx in self.idx:
            if idx.type==type:
                list.extend(idx.listobjects())
        return list


    def findref(self,ref,create=0):
        if ref.flag==0x01:
            if ref.Key.page_type!=self.page_type or  ref.Key.page_id!=self.page_id:
                return None
            return(self.find(ref.Key.object_type,str(ref.Key.name),create))
        else:
            return None


    def deleteSceneNode(self):
        for i in self.idx:
            if i.type==0x00:
                self.idx.remove(i)


    def createSceneNode(self):
        idx=self.findidx(0x00)
        idx.objs=[]
        idx.findobj(self.getName())
        #scn=idx.findobj(0x00)
        #scn.data.Key.name = str(self.name) + "_District_" + str(self.page)


    def updateSceneNode(self):
        idx=self.findidx(0x00)
        scn=idx.findobj(self.getName())
        #sceneObjects
        scn.data.SceneObjects.Trash()
        idx=self.findidx(0x01)
        for i in idx.objs:
            scn.data.SceneObjects.append(i.data.getRef())
        #others
        scn.data.OtherObjects.Trash()
        for x in scn.data.OtherObjects.AllowedTypes:
            idx=self.findidx(x)
            for i in idx.objs:
                scn.data.OtherObjects.append(i.data.getRef())


    def getSceneNode(self):
        return(self.find(0x00,self.getName()))


    def getBasePath(self):
        if self.resmanager.type=="prp":
            return "./"
        else:
            return self.resmanager.getBasePath()
