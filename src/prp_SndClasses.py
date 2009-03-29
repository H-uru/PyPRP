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
        from Blender import Sound
    except Exception, detail:
        print detail
except ImportError:
    pass

import md5
import random
import cStringIO
import copy
import Image
import math
import struct
import StringIO
import os
import pickle
from os.path import *
from binascii import *
from prp_Types import *
from prp_DXTConv import *
from prp_HexDump import *
from prp_GeomClasses import *
from prp_Functions import *
from prp_ConvexHull import *
from prp_AbsClasses import *
from prp_VolumeIsect import *
from prp_MatClasses import *
from prp_AlcScript import *
from prp_LogicClasses import *
import prp_Config
import prp_HexDump

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

    def _Export(page,obj,scnobj,name,SceneNodeRef,softVolumeParser, MultiSounds=[]):
        # Get this object's AlcScript section
        objscript = AlcScript.objects.Find(obj.name)

        # if no sound info specified, return none...
        if MultiSounds == []:
            if FindInDict(objscript,"sound",None) is None:
                return

        audioIface = plAudioInterface.FindCreate(page, name) #Create the audio Interface
        if audioIface == None:
            raise "ERROR: AudioInterface for %s not found!" %(str(scnobj.data.Key))
            return

        audioIface.data.parentref = scnobj.data.getRef()
        if MultiSounds:
            print MultiSounds
            aud = plWinAudible.FindCreate(page, name)
            aud.data.fSceneObj = SceneNodeRef
            for WSound in MultiSounds:
                WSoundScript = WSound[(WSound.keys()[0])]
                if string.lower(FindInDict(WSoundScript, "sound.buffer", "stream")) == "static":
                    win32snd = plWin32StaticSound.FindCreate(page, (WSound.keys()[0]))
                else:
                    win32snd = plWin32StreamingSound.FindCreate(page, (WSound.keys()[0]))
                win32snd.data.exportObj(obj, softVolumeParser,RndSndName=WSoundScript)
                aud.data.appendSound(win32snd.data.getRef())
            
            audioIface.data.fAudible = aud.data.getRef()
    
            scnobj.data.audio = audioIface.data.getRef()
        else:
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
        self.fFormatTag = plWAVHeader.Formats["kPCMFormatTag"]
        self.fNumChannels = 0
        self.fNumSamplesPerSec = 0
        self.fAvgBytesPerSec = 0
        self.fBlockAlign = 0
        self.fBitsPerSample = 0

    def read(self, stream):
        self.fFormatTag = stream.Read16()
        self.fNumChannels = stream.Read16()
        self.fNumSamplesPerSec = stream.Read32()
        self.fAvgBytesPerSec = stream.Read32()
        self.fBlockAlign = stream.Read16()
        self.fBitsPerSample = stream.Read16()

    def write(self, stream):
        stream.Write16(self.fFormatTag)
        stream.Write16(self.fNumChannels)
        stream.Write32(self.fNumSamplesPerSec)
        stream.Write32(self.fAvgBytesPerSec)
        stream.Write16(self.fBlockAlign)
        stream.Write16(self.fBitsPerSample)

    def makeFromInput(self, filename):
        wavfile = file(filename,'rb')
        try:
            assert wavfile.read(4) == 'RIFF'
            wavfile.read(4)
            assert wavfile.read(4) == 'WAVE'
            assert wavfile.read(4) == 'fmt '
            wavfile.read(4)
        except:
            raise IOError, "The file %s is not a valid WAV file" % filename
        #We're all good to go! It must be a valid .wav file!

        ## Using the struct.unpack here because we're working on a wave file,
        ## and that one is not opened with a hsStream, but wiht raw I/O
        self.fFormatTag = struct.unpack("<H", wavfile.read(2))[0]
        self.fNumChannels = struct.unpack("<H", wavfile.read(2))[0]
        self.fNumSamplesPerSec = struct.unpack("<I", wavfile.read(4))[0]
        self.fAvgBytesPerSec = struct.unpack("<I", wavfile.read(4))[0]
        self.fBlockAlign = struct.unpack("<H", wavfile.read(2))[0]
        self.fBitsPerSample = struct.unpack("<H", wavfile.read(2))[0]


    def makeFromOGG(self, oggFileName):
        oggfile = file(oggFileName,'rb')
        try:
            # OGG packet header
            assert oggfile.read(4) == 'OggS'
            streamVersion = struct.unpack("<B", oggfile.read(1))[0]
            assert streamVersion == 0
            headerTypeFlag = struct.unpack("<B", oggfile.read(1))[0]
            assert headerTypeFlag == 2
            absoluteGranulePosition = struct.unpack("<Q", oggfile.read(8))[0]
            assert absoluteGranulePosition == 0
            oggfile.read(4) # stream serial number
            pageSeqNum = struct.unpack("<i", oggfile.read(4))[0]
            assert pageSeqNum == 0
            oggfile.read(4) # checksum
            numPageSegments = struct.unpack("<B", oggfile.read(1))[0]
            for i in range(numPageSegments):
                oggfile.read(1) # entry in segment table
            # VORBIS header
            headerType = struct.unpack("<B", oggfile.read(1))[0]
            assert headerType == 1
            assert oggfile.read(6) == 'vorbis'
            vorbisVersion = struct.unpack("<I", oggfile.read(4))[0]
            assert vorbisVersion == 0 
        except:
            raise IOError, "The file %s was not a valid OGG file" % oggFileName

        # It is a valid OGG VORBIS file!
        self.fNumChannels = struct.unpack("<B", oggfile.read(1))[0]
        self.fNumSamplesPerSec = struct.unpack("<I",oggfile.read(4))[0]
        oggfile.close()
        self.fBitsPerSample = 16
        self.fBlockAlign = self.fNumChannels * (self.fBitsPerSample / 8)
        self.fAvgBytesPerSec = self.fBlockAlign * self.fNumSamplesPerSec


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

        self.fHeader.read(stream)

        if not self.fFlags & plSoundBuffer.Flags["kIsExternal"]:
            self.fData.append(stream.Read(self.fDataLength))


    def write(self, stream):
        hsKeyedObject.write(self, stream)

        stream.Write32(self.fFlags)
        stream.Write32(self.fDataLength)
        self.fFileName.write(stream)

        self.fHeader.write(stream)

        if not self.fFlags & plSoundBuffer.Flags["kIsExternal"]:
            if self.fData[0] != None:
                stream.write(self.fData[0])

    def dump(self,buf):
        print "Dump() deprecated on Audio and Sound classes"

    #######################
    # Interface Functions #
    #######################

    def makeFromInput(self, filename):

        if filename[-3:] == "wav" or filename[-3:] == "WAV":
            isWAVFile = True
            sname = filename.replace(".wav",".ogg")
        else:
            isWAVFile = False
            sname = filename
        self.fFileName.set(Blender.sys.basename(sname))
        #DEBUG
        print "  Sound source file: ", filename
        print "  In-game file: ", self.fFileName.name

        self.fFlags |= plSoundBuffer.Flags["kIsExternal"]
        self.fFlags |= plSoundBuffer.Flags["kAlwaysExternal"]
        self.fFlags |= plSoundBuffer.Flags["kStreamCompressed"]
        #Assume that the sound is always external... let's not deal with embedded sounds o.o
        self.fDataLength = os.path.getsize(filename) #should get us the size

        #Make the header
        if isWAVFile:
            self.fHeader.makeFromInput(filename) 
        else:
            self.fHeader.makeFromOGG(filename)


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

    scriptProps = \
    { \
        "is3dsound"       : 0x1, \
        "disablelod"      : 0x2, \
        "looping"         : 0x4, \
        "autostart"       : 0x8, \
        "localonly"       : 0x10, \
        "loadonlyoncall"  : 0x20, \
        "fullydisabled"   : 0x40, \
        "dontfade"        : 0x80, \
        "incidental"      : 0x100 \
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

    def getFullFileName(self, filename):
        fullFileName = Blender.sys.expandpath(filename)
        if not Blender.sys.exists(fullFileName):
            # Try the sound directory
            baseFilename = Blender.sys.basename(filename)
            fullFileName = Blender.Get('soundsdir') + Blender.sys.sep + baseFilename
            if not Blender.sys.exists(fullFileName):
                # Look in the same directory as the .blend file
                blendfile = Blender.Get('filename')
                fullFileName = Blender.sys.dirname(blendfile) + Blender.sys.sep + baseFilename
                if not Blender.sys.exists(fullFileName):
                    fullFileName = None
        return fullFileName


    #######################
    # Interface Functions #
    #######################

    def exportObj(self, obj, softVolumeParser, RndSndName=''):
        if RndSndName:
            objscript = RndSndName
        else:
            objscript = AlcScript.objects.Find(obj.getName())

        flags = FindInDict(objscript,"sound.flags",[])
        if type(flags) == list:
            self.fProperties = 0 # reset
            for flag in flags:
                if flag.lower() in plWin32Sound.scriptProps:
                    idx =  plWin32Sound.scriptProps[flag.lower()]
                    self.fProperties |= idx

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
        wavobj = None
        fullsname = None
        try:
            wavobj = Blender.Sound.Get(sname)
        except:
            try:
                wavobj = Blender.Sound.Get(sname+".wav")
            except:
                wavobj = None
                fullsname = self.getFullFileName(sname + ".wav")
                if fullsname == None:
                    fullsname = self.getFullFileName(sname + ".ogg")
                    if fullsname == None:
                        raise ValueError, "Cannot locate any sound named \"%s\"" % sname

        if wavobj:
            #HACK - Save the sound so that Blender doesn't eat it >.<
            wavobj.fakeUser = 1
            wavobj.setCurrent() #Make it the current sound object... just because we can :P
            fullsname = self.getFullFileName(wavobj.getFilename())
            if fullsname == None:
                raise ValueError, "Cannot locate any sound named \"%s\"" % wavobj.getFilename()


        #Export a SoundBuffer
        root=self.getRoot()
        sbuff = root.find(0x0029, sname, 1)
        sbuff.data.makeFromInput(fullsname)
        if(chan == "right"):
            sbuff.data.fFlags |= plSoundBuffer.Flags["kOnlyRightChannel"]
        if(chan == "left"):
            sbuff.data.fFlags |= plSoundBuffer.Flags["kOnlyLeftChannel"]
        self.fDataBuffer = sbuff.data.getRef() #We have our sound buffer

        vol = FindInDict(objscript,"sound.volume", 1.0)
        self.fDesiredVol = vol

        sndtype = FindInDict(objscript,"sound.type", "Ambience")
        if(sndtype.lower() == "soundfx"):
            self.fType = plSound.Type["kSoundFX"]
        elif(sndtype.lower() == "ambience"):
            self.fType = plSound.Type["kAmbience"]
        elif(sndtype.lower() == "backgroundmusic"):
            self.fType = plSound.Type["kBackgroundMusic"]
        elif(sndtype.lower() == "guisound"):
            self.fType = plSound.Type["kGUISound"]
        elif(sndtype.lower() == "npcvoices"):
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
        if (propString != None):
            if(softVolumeParser != None and softVolumeParser.isStringProperty(propString)):
                self.fSoftRegion = softVolumeParser.parseProperty(propString,str(self.Key.name))
            else:
                refparser = ScriptRefParser(self.getRoot(),str(self.Key.name),"softvolume")
                volume = refparser.MixedRef_FindCreate(propString)
                self.fSoftRegion = volume.data.getRef()

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

    def exportObj(self, obj, softVolumeParser,RndSndName=''):
        plWin32Sound.exportObj(self, obj, softVolumeParser,RndSndName)


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

    def exportObj(self, obj, softVolumeParser,RndSndName=''):
        plWin32Sound.exportObj(self, obj, softVolumeParser,RndSndName)


class plRandomSoundMod(plRandomCommandMod):
    def __init__(self,parent,name="unnamed",type=0x0079):
        plRandomCommandMod.__init__(self,parent,name,type)
        self.fGroups = hsTArray()

    def _Find(page,name):
        return page.find(0x0079,name,0)
    Find = staticmethod(_Find)

    def _FindCreate(page,name):
        return page.find(0x0079,name,1)
    FindCreate = staticmethod(_FindCreate)
    
    def _Export(page, obj, scnobj, name):
        RandomSoundMod = plRandomSoundMod.FindCreate(page, name)
        RandomSoundMod.data.export_obj(obj)
        scnobj.data.addModifier(RandomSoundMod)
    Export = staticmethod(_Export)

    def export_obj(self, obj):
        self.fMode = 11
        self.fState = 1

    def read(self, stream):
        self.fGroups.write(stream)

    def write(self, stream):
        plRandomCommandMod.write(self, stream)
        self.fGroups.write(stream)

