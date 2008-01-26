#
# $Id: alc_Classes.py 856 2007-10-31 19:12:27Z trylon $
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
        from Blender import Sound
    except Exception, detail:
        print detail
except ImportError:
    pass
    
import md5
import random
import binascii
import cStringIO
import copy
import Image
import math
import struct
import StringIO
import os
import os.path
import pickle
from alcurutypes import *
from alcdxtconv import *
from alchexdump import *
from alc_GeomClasses import *
from alc_Functions import *
from alcConvexHull import *
from alc_AbsClasses import *
from alc_VolumeIsect import *
from alc_MatClasses import *
import alcconfig
import alchexdump

class plAudioInterface(plObjInterface):             #Type 0x11
    def __init__(self, parent, name="unnamed"):
        plObjInterface.__init__(self, parent, name, 0x0011)
        self.fAudible = UruObjectRef(self.getVersion())
    
    def _Find(page,name):
        return page.find(0x0011,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0011,name,1)
    FindCreate = staticmethod(_FindCreate)

    def read(self, stream):
        plObjInterface.read(self, stream)
        self.fAudible.read(stream)
    
    def write(self, stream):
        plObjInterface.write(self, stream)
        self.fAudible.write(stream)
    
    def dump(self):
        print "Dump() deprecated on Audio and Sound classes"
        
    def _Export(page,obj,scnobj,name,SceneNodeRef,softVolumeParser):
        # Get this object's AlcScript section
        objscript = AlcScript.objects.Find(obj.name)
        
        # if no sound info specified, return none...
        if FindInDict(objscript,"sound",None) is None:
            return

        audioIface = plAudioInterface.FindCreate(page, name) #Create the audio Interface
        if audioIface == None:
            raise "ERROR: AudioInterface for %s not found!" %(str(scnobj.data.Key))
            return
            
        audioIface.data.parentref = scnobj.data.getRef()
        
        #Generate all of the fun plSound stuff >.<
        if string.lower(FindInDict(objscript, "sound.buffer", "stream")) == "static":
            win32snd = plWin32StaticSound.FindCreate(page, name)
        else:
            win32snd = plWin32StreamingSound.FindCreate(page, name)#Create the Win32 streaming sound
        
        win32snd.data.exportObj(obj, softVolumeParser) #We need to pass the parser                    

        #Generate the Audible
        aud = plWinAudible.FindCreate(page, name)
        aud.data.fSceneObj = SceneNodeRef
        aud.data.appendSound(win32snd.data.getRef())
        
        audioIface.data.fAudible = aud.data.getRef()
        
        scnobj.data.audio = audioIface.data.getRef() #Set the Audio Interface ref to the scene node

    Export = staticmethod(_Export)
        

class plAudible(hsKeyedObject):                             #Type 0x12
    def __init__(self,parent,name="unnamed",type=0x0012):
        hsKeyedObject.__init__(self,parent,name,type)
    
    def _Find(page,name):
        return page.find(0x0012,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0012,name,1)
    FindCreate = staticmethod(_FindCreate)

    def read(self, stream):
        hsKeyedObject.read(self, stream)
    
    def write(self, stream):
        hsKeyedObject.write(self, stream)
    
    def dump(self):
        print "Dump() deprecated on Audio and Sound classes"
        
class plWinAudible(plAudible):
    def __init__(self,parent,name="unnamed",type=0x0014):
        plAudible.__init__(self,parent,name,type)
        self.fSounds = hsTArray([],self.getVersion())
        self.fSceneObj = UruObjectRef(self.getVersion())
    
    def _Find(page,name):
        return page.find(0x0014,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0014,name,1)
    FindCreate = staticmethod(_FindCreate)

    def read(self, stream):
        plAudible.read(self, stream)
        self.fSounds.ReadVector(stream)
        self.fSceneObj.read(stream)
    
    def write(self, stream):
        plAudible.write(self, stream)
        self.fSounds.WriteVector(stream)
        self.fSceneObj.write(stream)
    
    def dump(self):
        print "Dump() deprecated on Audio and Sound classes"
    
    #######################
    # Interface Functions #
    #######################
    
    def appendSound(self, snd):
        self.fSounds.append(snd)

class plWAVHeader:
    Formats = \
    { \
        "kPCMFormatTag" : 0x1 \
    }
    
    def __init__(self):
        self.fFormatTag = 1
        self.fNumChannels = 0
        self.fNumSamplesPerSec = 0
        self.fAvgBytesPerSec = 0
        self.fBlockAlign = 0
        self.fBitsPerSample = 0
    
    def makeFromInput(self, wavfile):
        assert wavfile.read(4) == 'RIFF'
        wavfile.read(4)
        assert wavfile.read(4) == 'WAVE'
        assert wavfile.read(4) == 'fmt '
        wavfile.read(4)
        #We're all good to go! It must be a valid .wav file!
        
        ## Using the struct.unpack here because we're working on a wave file, 
        ## and that one is not opened with a hsStream, but wiht raw I/O
        self.fFormatTag = struct.unpack("<H", wavfile.read(2))[0]
        self.fNumChannels = struct.unpack("<H", wavfile.read(2))[0]
        self.fNumSamplesPerSec = struct.unpack("<I", wavfile.read(4))[0]
        self.fAvgBytesPerSec = struct.unpack("<I", wavfile.read(4))[0]
        self.fBlockAlign = struct.unpack("<H", wavfile.read(2))[0]
        self.fBitsPerSample = struct.unpack("<H", wavfile.read(2))[0]


 
class plSoundBuffer(hsKeyedObject):                     #Type 0x29
    Flags = \
    { \
        "kIsExternal"       : 0x1, \
        "kAlwaysExternal"   : 0x2, \
        "kOnlyLeftChannel"  : 0x4, \
        "kOnlyRightChannel" : 0x8, \
        "kStreamCompressed" : 0x10 \
    }
    
    def __init__(self, parent, name="unnamed", type=0x0029):
        hsKeyedObject.__init__(self, parent, name, type)
        
        self.fFlags = 0
        self.fDataLength = 0
        self.fFileName = Ustr("", self.getVersion())
        self.fHeader = plWAVHeader()
        self.fData = []
        
    def _Find(page,name):
        return page.find(0x0029,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0029,name,1)
    FindCreate = staticmethod(_FindCreate)

    
    def read(self, stream):
        hsKeyedObject.read(self, stream)
        
        self.fFlags = stream.Read32()
        self.fDataLength = stream.Read32()
        self.fFileName.read(stream)
        
        self.fHeader.fFormatTag = stream.Read16()
        self.fHeader.fNumChannels = stream.Read16()
        self.fHeader.fNumSamplesPerSec = stream.Read32()
        self.fHeader.fAvgBytesPerSec = stream.Read32()
        self.fHeader.fBlockAlign = stream.Read16()
        self.fHeader.fBitsPerSample = stream.Read16()
        
        if not self.fFlags & plSoundBuffer.Flags["kIsExternal"]:
            self.fData.append(stream.Read(self.fDataLength))
        
    
    def write(self, stream):
        hsKeyedObject.write(self, stream)
        
        stream.Write32(self.fFlags)
        stream.Write32(self.fDataLength)
        self.fFileName.write(stream)
        
        stream.Write16(self.fHeader.fFormatTag)
        stream.Write16(self.fHeader.fNumChannels)
        stream.Write32(self.fHeader.fNumSamplesPerSec)
        stream.Write32(self.fHeader.fAvgBytesPerSec)
        stream.Write16(self.fHeader.fBlockAlign)
        stream.Write16(self.fHeader.fBitsPerSample)
        
        if not self.fFlags & plSoundBuffer.Flags["kIsExternal"]:
            if self.fData[0] != None:
                stream.write(self.fData[0])
    
    def dump(self,buf):
        print "Dump() deprecated on Audio and Sound classes"
    
    #######################
    # Interface Functions #
    #######################
    
    def makeFromInput(self, wavobj):
        wavobj.setCurrent() #Make it the current sound object... just because we can :P
        
        self.fFileName.set(wavobj.getName().replace(".wav", ".ogg"))
        
        self.fFlags |= plSoundBuffer.Flags["kIsExternal"]
        self.fFlags |= plSoundBuffer.Flags["kAlwaysExternal"]
        self.fFlags |= plSoundBuffer.Flags["kStreamCompressed"]
        #Assume that the sound is always external... let's not deal with embedded sounds o.o
        
        self.fDataLength = os.path.getsize(Blender.sys.expandpath(wavobj.getFilename())) #should get us the size
        
        wav = file(Blender.sys.expandpath(wavobj.getFilename())) #Open the stream
        
        self.fHeader.makeFromInput(wav) #Make the header


class plEAXSourceSoftSettings:
    
    def __init__(self):
        self.Reset()
        
    def Reset(self):
        self.fOcclusion = 0
        self.fOcclusionLFRatio = 0.25
        self.fOcclusionRoomRatio = 1.5
        self.fOcclusionDirectRatio = 1.0

    def read(self,stream):
        self.fOcclusion = stream.Read16()
        self.fOcclusionLFRatio = stream.ReadFloat()
        self.fOcclusionRoomRatio = stream.ReadFloat()
        self.fOcclusionDirectRatio = stream.ReadFloat()
    
    def write(self,stream):
        stream.Write16(self.fOcclusion)
        stream.WriteFloat(self.fOcclusionLFRatio)
        stream.WriteFloat(self.fOcclusionRoomRatio)
        stream.WriteFloat(self.fOcclusionDirectRatio)
        


class plEAXSourceSettings:
    ParamSets = \
    { \
        "kOcclusion"    : 0x1, \
        "kRoom"         : 0x2, \
        "kOutsideVolHF" : 0x4, \
        "kFactors"      : 0x8, \
        "kAll"          : 0xFF  \
    }
    
    def __init__(self):
        self.fEnabled = False
        self.fSoftStarts = plEAXSourceSoftSettings()
        self.fSoftEnds = plEAXSourceSoftSettings()
        self.Enable(False)
        
    def Enable(self,enable):
        self.fEnabled = enable
        if (enable == False):
            self.fOutsideVolHF = 0
            self.fRoomRolloffFactor = 0.0
            self.fDopplerFactor = 0.0
            self.fRolloffFactor = 0.0
            self.fRoom = -1
            self.fRoomHF = -1
            self.fRoomAuto = True
            self.fRoomHFAuto = True
            self.fAirAbsorptionFactor = 1.0
            self.fSoftStarts.Reset()
            self.fSoftEnds.Reset()
            self.fOcclusionSoftValue = 1.0
    
    def read(self,stream):
        self.fEnabled = stream.ReadBool()

        if self.fEnabled:
            self.fRoom = stream.Read16()
            self.fRoomHF = stream.Read16()
            self.fRoomAuto = stream.ReadBool()
            self.fRoomHFAuto = stream.ReadBool()
            self.fOutsideVolHF = stream.Read16()
            self.fAirAbsorptionFactor = stream.ReadFloat()
            self.fRoomRolloffFactor = stream.ReadFloat()
            self.fDopplerFactor = stream.ReadFloat()
            self.fRolloffFactor = stream.ReadFloat()
            self.fSoftStarts.read(stream)
            self.fSoftEnds.read(stream)
            self.fOcclusionSoftValue = stream.ReadFloat()
        else:
            self.Enable(False)

    
    def write(self,stream):
        stream.WriteBool(self.fEnabled)

        if (self.fEnabled):
            stream.Write16(self.fRoom)
            stream.Write16(self.fRoomHF)
            stream.WriteBool(self.fRoomAuto)
            stream.WriteBool(self.fRoomHFAuto)
            stream.Write16(self.fOutsideVolHF)
            stream.WriteFloat(self.fAirAbsorptionFactor)
            stream.WriteFloat(self.fRoomRolloffFactor)
            stream.WriteFloat(self.fDopplerFactor)
            stream.WriteFloat(self.fRolloffFactor)
            self.fSoftStarts.write(stream)
            self.fSoftEnds.write(stream)
            stream.WriteFloat(fOcclusionSoftValue)

class plFadeParams:
    Type = \
    { \
        "kLinear"       : 0x0, \
        "kLogarithmic"  : 0x1, \
        "kExponential"  : 0x2 \
    }
    
    ScriptType = \
    { \
        "linear"       : 0x0, \
        "logarithmic"  : 0x1, \
        "exponential"  : 0x2 \
    }
    
    def __init__(self):
        self.fLengthInSecs = 0
        self.fVolStart = 0.0
        self.fVolEnd = 0.0
        self.fType = 0
        self.fStopWhenDone = 0
        self.fFadeSoftVol = 0
        self.fCurrTime = -1.0
    
    def write(self, stream):
        stream.WriteFloat(self.fLengthInSecs)
        stream.WriteFloat(self.fVolStart)
        stream.WriteFloat(self.fVolEnd)
        stream.WriteByte(self.fType)
        stream.WriteFloat(self.fCurrTime)
        stream.Write32(self.fStopWhenDone)
        stream.Write32(self.fFadeSoftVol)
    
    def read(self, stream):
        self.fLengthInSecs = stream.ReadFloat()
        self.fVolStart = stream.ReadFloat()
        self.fVolEnd = stream.ReadFloat()
        self.fType = stream.ReadByte()
        self.fCurrTime = stream.ReadFloat()
        self.fStopWhenDone = stream.Read32()
        self.fFadeSoftVol = stream.Read32()
    
    def export_script(self, script):
        length = FindInDict(script, "length", None)
        if length != None:
            self.fLengthInSecs = float(length)
            print "    plFadeParams: length: %f" % float(length)
        
        start = FindInDict(script, "start", None)
        if start != None:
            self.fVolStart = float(start)
            print "    plFadeParams: start: %f" % float(start)
        
        end = FindInDict(script, "end", None)
        if end != None:
            self.fVolEnd = float(end)
            print "    plFadeParams: end: %f" % float(end)
        
        stop = FindInDict(script, "stop", None)
        if stop != None:
            self.fStopWhenDone = bool(stop)
            print "    plFadeParams: stop: %s" % stop
        
        type = FindInDict(script, "type", "linear")
        if type in plFadeParams.ScriptType:
            self.fType = plFadeParams.ScriptType[type]
        else:
            self.fType = plFadeParams.ScriptType["linear"]

class plSound(plSynchedObject):
    
    Properties = \
    { \
        "kPropIs3DSound"       : 0x1, \
        "kPropDisableLOD"      : 0x2, \
        "kPropLooping"         : 0x4, \
        "kPropAutoStart"       : 0x8, \
        "kPropLocalOnly"       : 0x10, \
        "kPropLoadOnlyOnCall"  : 0x20, \
        "kPropFullyDisabled"   : 0x40, \
        "kPropDontFade"        : 0x80, \
        "kPropIncidental"      : 0x100 \
    }
    
    Type = \
    { \
        "kStartType"       : 0, \
        "kSoundFX"         : 0, \
        "kAmbience"        : 1, \
        "kBackgroundMusic" : 2, \
        "kGUISound"        : 3, \
        "kNPCVoices"       : 4, \
        "kNumTypes"        : 5 \
    }
    
    def __init__(self,parent,name="unnamed",type=0x0048):
        plSynchedObject.__init__(self,parent,name,type)
        self.fPlaying = 0
        self.fTime = 0.0
        self.fMaxFalloff = 10
        self.fMinFalloff = 5
        self.fCurrVolume = 0.0
        self.fOuterVol = 0
        self.fInnerCone = 360
        self.fOuterCone = 360
        self.fDesiredVol = 0.0
        self.fFadedVolume = 0.0
        self.fProperties = 0
        self.fType = plSound.Type["kStartType"]
        self.fPriority = 0
        self.fSoftRegion = UruObjectRef(self.getVersion())
        self.fDataBuffer = UruObjectRef(self.getVersion())
        self.fSoftOcclusionRegion = UruObjectRef(self.getVersion())
        self.fFadeInParams = plFadeParams()
        self.fFadeOutParams = plFadeParams()
        self.fEAXSettings = plEAXSourceSettings()
        
    def _Find(page,name):
        return page.find(0x0048,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0048,name,1)
    FindCreate = staticmethod(_FindCreate)


    def read(self, stream):
        plSynchedObject.read(self, stream)
        self.fPlaying = stream.ReadBool()
        self.fTime = stream.ReadDouble()
        self.fMaxFalloff = stream.Read32()
        self.fMinFalloff = stream.Read32()
        self.fCurrVolume = stream.ReadFloat()
        self.fDesiredVol= stream.ReadFloat()
        self.fOuterVol = stream.Read32()
        self.fInnerCone = stream.Read32()
        self.fOuterCone = stream.Read32()
        self.fFadedVolume = stream.ReadFloat()
        self.fProperties = stream.Read32()
        self.fType = stream.ReadByte()
        self.fPriority = stream.ReadByte()
        
        self.fFadeInParams.read(stream)
        self.fFadeOutParams.read(stream)
        
        self.fSoftRegion.read(stream)
        self.fDataBuffer.read(stream)
        
        self.fEAXSettings.read(stream)
        
        self.fSoftOcclusionRegion.read(stream)

    
    def write(self, stream):
        plSynchedObject.write(self,stream)
        stream.WriteBool(self.fPlaying)
        stream.WriteDouble(self.fTime)
        stream.Write32(self.fMaxFalloff)
        stream.Write32(self.fMinFalloff)
        stream.WriteFloat(self.fCurrVolume)
        stream.WriteFloat(self.fDesiredVol)
        stream.Write32(self.fOuterVol)
        stream.Write32(self.fInnerCone)
        stream.Write32(self.fOuterCone)
        stream.WriteFloat(self.fFadedVolume)
        stream.Write32(self.fProperties)
        stream.WriteByte(self.fType)
        stream.WriteByte(self.fPriority)
        
        self.fFadeInParams.write(stream)
        self.fFadeOutParams.write(stream)
        
        self.fSoftRegion.write(stream)
        self.fDataBuffer.write(stream)
        
        self.fEAXSettings.write(stream)
        
        self.fSoftOcclusionRegion.write(stream)
    
    def dump(self,buf):
        print "Dump() deprecated on Audio and Sound classes"


class plWin32Sound(plSound):
    ChannelSelect = \
    { \
        "kLeftChannel"  : 0, \
        "kRightChannel" : 1 \
    }
    
    def __init__(self,parent,name="unnamed",type=0x0049):
        plSound.__init__(self,parent,name,type)
        self.fChannelSelect = 0

    def _Find(page,name):
        return page.find(0x0049,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0049,name,1)
    FindCreate = staticmethod(_FindCreate)

    def read(self, stream):
        plSound.read(self, stream)
        self.fChannelSelect = stream.ReadByte()
    
    def write(self, stream):
        plSound.write(self, stream)
        stream.WriteByte(self.fChannelSelect)
    
    
    def dump(self,buf):
        print "Dump() deprecated on Audio and Sound classes"
    
    #######################
    # Interface Functions #
    #######################
    
    def exportObj(self, obj, softVolumeParser):
        objscript = AlcScript.objects.Find(obj.getName())
        
        flags = FindInDict(objscript,"sound.flags", "")
        flags = flags.replace(" ","")
        f = flags.split('|')
        for prop in f:
            if(prop == "3d"):
                self.fProperties |= plSound.Properties["kPropIs3DSound"]
            if(prop == "loop"):
                self.fProperties |= plSound.Properties["kPropLooping"]
            if(prop == "start"):
                self.fProperties |= plSound.Properties["kPropAutoStart"]
            if(prop == "local"):
                self.fProperties |= plSound.Properties["kPropLocalOnly"]
        
        chan = FindInDict(objscript,"sound.channel")
        if(chan == "right"):
            self.fChannelSelect = plWin32Sound.ChannelSelect["kRightChannel"]
        else:
            self.fChannelSelect = plWin32Sound.ChannelSelect["kLeftChannel"]
        
        sname = FindInDict(objscript,"sound.file")
        assert sname != None #We can't create a null SoundBuffer
        
        maxFallDist = FindInDict(objscript,"sound.maxfdist", 10)
        self.fMaxFalloff = int(maxFallDist)
        
        minFallDist = FindInDict(objscript,"sound.minfdist", 5)
        self.fMinFalloff = int(minFallDist)
        
        wavobj = Blender.Sound.Get(sname+'.wav')
        if wavobj:
            #HACK - Save the sound so that Blender doesn't eat it >.<
            wavobj.fakeUser = 1
            #Export a SoundBuffer
            root=self.getRoot()
            sbuff = root.find(0x0029, wavobj.getName(), 1)
            sbuff.data.makeFromInput(wavobj)
            if(chan == "right"):
                sbuff.data.fFlags |= plSoundBuffer.Flags["kOnlyRightChannel"]
            if(chan == "left"):
                sbuff.data.fFlags |= plSoundBuffer.Flags["kOnlyLeftChannel"]
            self.fDataBuffer = sbuff.data.getRef() #We have our sound buffer
        
        vol = FindInDict(objscript,"sound.volume", 1.0)
        self.fDesiredVol = vol
        
        type = FindInDict(objscript,"sound.type", "Ambience")
        if(type.lower() == "soundfx"):
            self.fType = plSound.Type["kSoundFX"]
        elif(type.lower() == "ambience"):
            self.fType = plSound.Type["kAmbience"]
        elif(type.lower() == "backgroundmusic"):
            self.fType = plSound.Type["kBackgroundMusic"]
        elif(type.lower() == "guisound"):
            self.fType = plSound.Type["kGUISound"]
        elif(type.lower() == "npcvoices"):
            self.fType = plSound.Type["kNPCVoices"]
        else:
            self.fType = plSound.Type["kAmbience"]
        
        #FadeIn params
        fIn = FindInDict(objscript,"sound.fadein",None)
        if fIn != None:
            self.fFadeInParams.export_script(fIn)
        
        #FadeOut params
        fOut = FindInDict(objscript,"sound.fadeout",None)
        if fOut != None:
            self.fFadeOutParams.export_script(fOut)
        
        # Set the soft volume
        propString = FindInDict(objscript,"sound.softvolume")
        if (propString != None and softVolumeParser != None):
            self.fSoftRegion = softVolumeParser.parseProperty(str(propString),str(self.Key.name))
        


class plWin32StaticSound(plWin32Sound):
    def __init__(self,parent,name="unnamed",type=0x0096):
        plWin32Sound.__init__(self,parent,name,type)
    
    def _Find(page,name):
        return page.find(0x0096,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0096,name,1)
    FindCreate = staticmethod(_FindCreate)

    def read(self, stream):
        plWin32Sound.read(self, stream)
    
    def write(self, stream):
        plWin32Sound.write(self, stream)
    
    def dump(self,buf):
        print "Dump() deprecated on Audio and Sound classes"
    
    def exportObj(self, obj, softVolumeParser):
        plWin32Sound.exportObj(self, obj, softVolumeParser)


class plWin32StreamingSound(plWin32Sound):
    def __init__(self,parent,name="unnamed",type=0x0084):
        plWin32Sound.__init__(self,parent,name,type)
    
    def _Find(page,name):
        return page.find(0x0084,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0084,name,1)
    FindCreate = staticmethod(_FindCreate)

    def read(self, stream):
        plWin32Sound.read(self, stream)
    
    def write(self, stream):
        plWin32Sound.write(self, stream)
    
    def dump(self,buf):
        print "Dump() deprecated on Audio and Sound classes"
    
    def exportObj(self, obj, softVolumeParser):
        plWin32Sound.exportObj(self, obj, softVolumeParser)
