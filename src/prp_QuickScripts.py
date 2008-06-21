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
from prp_Functions import *
from prp_AlcScript import *
from prp_RefParser import *

# Quickscripts are run on the object before parsing it though any processing
# The different scripts must automatically set variables in the AlcScript of the object, based on settings they read
# This way, they can be used to simplify settings througout the full spectrum of classes - this can range from cameras
# to logic properties, to anything settable in alcscript.

# Quickscripts that do more than just setting variables in alcscript are deemed illegal scripts.

# Quickscripts should use the .quickscript AlcScript domain, unless it's an obvious simple feature, that is more logical
# in another area, like ".region". Footstep regions are an example of this, but for example setting multiple flags in order
# to make a simple physics setting possible can be placed under ".physical".

# Quickscripts are free to use logic properties in any way they see fit. But they may not write to them!


# Developer note:
# Always use the ".FindOrCreate()" function of the alcscript objects, so that an alcscript entry will also be made if the
# object has no alcscript entry yet.


# This function calls upon all quickscript subfunctions
def RunQuickScripts(obj):

    result = False
    result |= QuickScript_Footstep(obj)
    result |= QuickScript_SoundRegion(obj)
    result |= QuickScript_SimpleClickable(obj)
    # this needs to be added lastly
    result |= QuickScript_SelfAnimationRegion(obj)
    result |= QuickScript_SDL(obj)

    objscript = AlcScript.objects.Find(obj.name)

    if result:
        print "Quickscripted", obj.name
        print "To:",objscript,"\n"


def QuickScript_Footstep(obj):
    objscript = AlcScript.objects.FindOrCreate(obj.name)
    alctype = FindInDict(objscript,"type","object")
    alctype = getTextPropertyOrDefault(obj,"type",alctype)

    rgntype = FindInDict(objscript,"region.type","logic")
    rgntype = getTextPropertyOrDefault(obj,"regiontype",rgntype)

    if rgntype == "footstep":

        surfaces = FindInDict(objscript,"region.surfaces",None)
        if surfaces is None:
            surface = FindInDict(objscript,"region.surface",None)
            surface = getTextPropertyOrDefault(obj,"surface",surface)
            if not surface is None:
                surfaces = [surface,]

        if not surfaces is None and type(surfaces) == list:
            print "  [QuickScript - Footstep]"

            # Build up the required script

            modtxt  = "- tag: Enter_Ft\n"
            modtxt += "  flags:\n"
            modtxt += "    - multitrigger\n"
            modtxt += "  activators:\n"
            modtxt += "    - type: objectinvolume\n"
            modtxt += "  conditions:\n"
            modtxt += "    - type: volumesensor\n"
            modtxt += "      satisfied: true\n"
            modtxt += "      direction: enter\n"
            modtxt += "  actions:\n"
            modtxt += "    - type: responder\n"
            modtxt += "      ref: $FootSnd\n"
            modtxt += "\n"
            modtxt += "- tag: Exit_Ft\n"
            modtxt += "  flags:\n"
            modtxt += "    - multitrigger\n"
            modtxt += "  activators:\n"
            modtxt += "    - type: objectinvolume\n"
            modtxt += "  conditions:\n"
            modtxt += "    - type: volumesensor\n"
            modtxt += "      satisfied: true\n"
            modtxt += "      direction: exit\n"
            modtxt += "  actions:\n"
            modtxt += "    - type: responder\n"
            modtxt += "      ref: $FootSnd\n"
            modtxt += "\n"

            acttxt  = "type: responder\n"
            acttxt += "tag: FootSnd\n"
            acttxt += "responder:\n"
            acttxt += "  states:\n"
            acttxt += "    - cmds:\n"
        # make a list of commands for each footstep sound, and set the option to append for each
            # command after the first

            first = False
            for surface in list(surfaces):
                acttxt += "        - type: armatureeffectmsg\n"
                acttxt += "          params:\n"
                acttxt += "              surface: " + str(surface) + "\n"
                if not first:
                    acttxt += "              append: false\n"
                else:
                    acttxt += "              append: true\n"

            acttxt += "          waiton: -1\n"
            acttxt += "      nextstate: 0\n"
            acttxt += "      waittocmd: 0\n"
            acttxt += "  curstate: 0\n"
            acttxt += "  flags:\n"
            acttxt += "    - detecttrigger\n"

            # Parse the code
            myactscript = AlcScript(acttxt).GetRootScript()
            mymodscript = AlcScript(modtxt).GetRootScript()

            # Add the parsed script to the correct space in the dictionary, or create that space
            actscript = FindInDict(objscript,"logic.actions",None)
            if actscript is None or type(actscript) != list:
                StoreInDict(objscript,"logic.actions",[myactscript])
            else:
                actscript.append(myactscript)

            modscript = FindInDict(objscript,"logic.modifiers",None)
            if actscript is None or type(modscript) != list:
                StoreInDict(objscript,"logic.modifiers",mymodscript)
            else:
                for script in mymodscript:
                    modscript.append(script)

            return True

    return False


def QuickScript_SoundRegion(obj):
    objscript = AlcScript.objects.FindOrCreate(obj.name)
    alctype = FindInDict(objscript,"type","object")
    alctype = getTextPropertyOrDefault(obj,"type",alctype)

    rgntype = FindInDict(objscript,"region.type","logic")
    rgntype = getTextPropertyOrDefault(obj,"regiontype",rgntype)

    if rgntype == "soundregion":

        emitters = FindInDict(objscript,"region.soundemitters",None)
        if emitters is None:
            emitter = FindInDict(objscript,"region.soundemitter",None)
            emitter = getTextPropertyOrDefault(obj,"soundemitter",emitter)
            if not emitter is None:
                emitters = [emitter,]

        if not emitters is None and type(emitters) == list:
            print "  [QuickScript - SoundRegion]"

            # Build up the required script

            modtxt  = "- tag: Enter_SndRgn\n"
            modtxt += "  flags:\n"
            modtxt += "    - multitrigger\n"
            modtxt += "  activators:\n"
            modtxt += "    - type: objectinvolume\n"
            modtxt += "  conditions:\n"
            modtxt += "    - type: volumesensor\n"
            modtxt += "      satisfied: true\n"
            modtxt += "      direction: enter\n"
            modtxt += "  actions:\n"
            modtxt += "    - type: responder\n"
            modtxt += "      ref: $SndRgn\n"
            modtxt += "\n"
            modtxt += "- tag: Exit_SndRgn\n"
            modtxt += "  flags:\n"
            modtxt += "    - multitrigger\n"
            modtxt += "  activators:\n"
            modtxt += "    - type: objectinvolume\n"
            modtxt += "  conditions:\n"
            modtxt += "    - type: volumesensor\n"
            modtxt += "      satisfied: true\n"
            modtxt += "      direction: exit\n"
            modtxt += "  actions:\n"
            modtxt += "    - type: responder\n"
            modtxt += "      ref: $SndRgn\n"
            modtxt += "\n"

            acttxt  = "type: responder\n"
            acttxt += "tag: SndRgn\n"
            acttxt += "responder:\n"
            acttxt += "  states:\n"
            acttxt += "    - cmds:\n"
            acttxt += "        - type: soundmsg\n"
            acttxt += "          params:\n"
            acttxt += "              receivers:\n"
        for emitter in list(emitters):
            acttxt += "                - 0011:" + str(emitter) + "\n"
            acttxt += "              cmds:\n"
            acttxt += "                - play\n"
            acttxt += "                - setvolume\n"
            acttxt += "              volume: 1\n"
            acttxt += "          waiton: -1\n"
            acttxt += "      nextstate: 1\n"
            acttxt += "      waittocmd: 0\n"
            acttxt += "    - cmds:\n"
            acttxt += "        - type: soundmsg\n"
            acttxt += "          params:\n"
            acttxt += "              receivers:\n"
        for emitter in list(emitters):
            acttxt += "                - 0011:" + str(emitter) + "\n"
            acttxt += "              cmds:\n"
            acttxt += "                - stop\n"
            acttxt += "          waiton: -1\n"
            acttxt += "      nextstate: 0\n"
            acttxt += "      waittocmd: 0\n"
            acttxt += "  curstate: 0\n"
            acttxt += "  flags:\n"
            acttxt += "    - detecttrigger\n"

            # Parse the code
            myactscript = AlcScript(acttxt).GetRootScript()
            mymodscript = AlcScript(modtxt).GetRootScript()

            # Add the parsed script to the correct space in the dictionary, or create that space
            actscript = FindInDict(objscript,"logic.actions",None)
            if actscript is None or type(actscript) != list:
                StoreInDict(objscript,"logic.actions",[myactscript])
            else:
                actscript.append(myactscript)

            modscript = FindInDict(objscript,"logic.modifiers",None)
            if actscript is None or type(modscript) != list:
                StoreInDict(objscript,"logic.modifiers",mymodscript)
            else:
                for script in mymodscript:
                    modscript.append(script)

            return True

    return False


def QuickScript_SelfAnimationRegion(obj):
    objscript = AlcScript.objects.FindOrCreate(obj.name)
    alctype = FindInDict(objscript,"type","object")
    alctype = getTextPropertyOrDefault(obj,"type",alctype)

    if alctype == "region":
        rgntype = getTextPropertyOrDefault(obj,"regiontype","logic")
        rgntype = FindInDict(objscript,"region.type",rgntype)

        animation = getTextPropertyOrDefault(obj,"selfanimation",None)
        animation = FindInDict(objscript,"quickscript.selfanimation.animation",animation)

        if rgntype == "logic" and not animation is None and type(animation) == str:
            print "  [QuickScript - SelfAnimation]"

            # Build up the required script

            modtxt  = "- tag: SelfAnim\n"
            modtxt += "  flags:\n"
            modtxt += "    - multitrigger\n"
            modtxt += "  activators:\n"
            modtxt += "    - type: objectinvolume\n"
            modtxt += "      triggers:\n"
            modtxt += "        - enter\n"
            modtxt += "  conditions:\n"
            modtxt += "    - type: volumesensor\n"
            modtxt += "      direction: enter\n"
            modtxt += "  actions:\n"
            modtxt += "    - type: oneshot\n"
            modtxt += "      ref: $SelfAnim\n"

            acttxt  = "type: oneshot\n"
            acttxt += "tag: SelfAnim\n"
            acttxt += "oneshot: \n"
            acttxt += "    animation: " + str(animation) + "\n"

            # Parse the code
            myactscript = AlcScript(acttxt).GetRootScript()
            mymodscript = AlcScript(modtxt).GetRootScript()

            # Add the parsed script to the correct space in the dictionary, or create that space
            actscript = FindInDict(objscript,"logic.actions",None)
            if actscript is None or type(actscript) != list:
                StoreInDict(objscript,"logic.actions",[myactscript])
            else:
                actscript.append(myactscript)

            modscript = FindInDict(objscript,"logic.modifiers",None)
            if actscript is None or type(modscript) != list:
                StoreInDict(objscript,"logic.modifiers",mymodscript)
            else:
                for script in mymodscript:
                    modscript.append(script)

            return True

    return False


# Hub for different types of SDL - currently "SDLBoolShowHide", "RandomBool" and "SDLIntActEnabler"
def QuickScript_SDL(obj):
    objscript = AlcScript.objects.FindOrCreate(obj.name)

  # Modified in order to combine SDL types (previous script allowed only one SDL type)
  # Text properties support is now completely ditched here

    sdllist = FindInDict(objscript,"quickscript.sdl",None)

    if not sdllist is None:
        if type(sdllist) != list:
            sdllist = [sdllist,]
        #print sdllist

        result = False
        for sdlscript in list(sdllist):
            #print sdlscript
            if type(sdlscript) != dict:
                continue
            sdltype = str(FindInDict(sdlscript,"type",""))
            if sdltype == "boolshowhide":
                result |= QuickScript_SDLBoolShowHide(obj)
            elif sdltype == "randombool":
                result |= QuickScript_RandomBool(obj,sdlscript)
            elif sdltype == "intactenabler":
                result |= QuickScript_SDLIntActEnabler(obj)

        if result:
            return result

    return False

# add BoolShowHide
def QuickScript_SDLBoolShowHide(obj):
    print "  [QuickScript - SDLBoolShowHide]"
    objscript = AlcScript.objects.FindOrCreate(obj.name)

    acttxt  = "- type: pythonfile\n"
    acttxt += "  tag: BoolShowHide\n"
    acttxt += "  pythonfile:\n"
    acttxt += "      file: xAgeSDLBoolShowHide\n"
    acttxt += "      parameters:\n"
    acttxt += "        - type: string\n"
    acttxt += "          value: " + str(obj.name) + "Vis\n"
    acttxt += "        - type: bool\n"
    acttxt += "          value: true\n"

    print "Resulting Code for .logic.actions:\n",acttxt

    myactscript = AlcScript(acttxt).GetRootScript()

    # Add the parsed script to the correct space in the dictionary, or create that space
    actscript = FindInDict(objscript,"logic.actions",None)
    if actscript is None or type(actscript) != list:
        StoreInDict(objscript,"logic.actions", myactscript)
    else:
        for script in myactscript:
            actscript.append(script)

    return True

# add RandomBool
def QuickScript_RandomBool(obj,sdlscript):
    print "  [QuickScript - RandomBool]"
    objscript = AlcScript.objects.FindOrCreate(obj.name)

    region = FindInDict(sdlscript,"region",None)

    if not region is None:
        modtxt  = "- tag: ProxiSensor_Enter\n"
        modtxt += "  cursor: nochange\n"
        modtxt += "  flags:\n"
        modtxt += "    - multitrigger\n"
        modtxt += "  activators:\n"
        modtxt += "    - type: objectinvolume\n"
        modtxt += "      remote: " + str(region) + "\n"
        modtxt += "      triggers:\n"
        modtxt += "        - enter\n"
        modtxt += "  conditions:\n"
        modtxt += "    - type: volumesensor\n"
        modtxt += "      satisfied: true\n"
        modtxt += "      direction: enter\n"
        modtxt += "  actions:\n"
        modtxt += "    - type: pythonfile\n"
        modtxt += "      ref: $RandomBool\n"
        modtxt += "- tag: ProxiSensor_Exit\n"
        modtxt += "  cursor: nochange\n"
        modtxt += "  flags:\n"
        modtxt += "    - multitrigger\n"
        modtxt += "  activators:\n"
        modtxt += "    - type: objectinvolume\n"
        modtxt += "      remote: " + str(region) + "\n"
        modtxt += "      triggers:\n"
        modtxt += "        - exit\n"
        modtxt += "  conditions:\n"
        modtxt += "    - type: volumesensor\n"
        modtxt += "      satisfied: true\n"
        modtxt += "      direction: exit\n"
        modtxt += "  actions:\n"
        modtxt += "    - type: pythonfile\n"
        modtxt += "      ref: $RandomBool\n"

        acttxt  = "- type: pythonfile\n"
        acttxt += "  tag: RandomBool\n"
        acttxt += "  pythonfile:\n"
        acttxt += "      file: xRandomBoolChange\n"
        acttxt += "      parameters:\n"
        acttxt += "        - type: string\n"
        acttxt += "          value: " + str(obj.name) + "Vis\n"
        acttxt += "        - type: string\n"
        acttxt += "          value: " + str(obj.name) + "Enabled\n"
        acttxt += "        - type: string\n"
        acttxt += "          value: " + str(obj.name) + "Chance\n"
        acttxt += "        - type: string\n"
        acttxt += "          value: " + str(obj.name) + "Proximity\n"
        acttxt += "        - type: activatorlist\n"
        acttxt += "          refs: [\'logicmod:$ProxiSensor_Enter\',\'logicmod:$ProxiSensor_Exit\']\n"
        acttxt += "        - type: bool\n"
        acttxt += "          value: true\n"
        acttxt += "        - type: sceneobject\n"
        acttxt += "          ref: scnobj:" + str(obj.name) + "\n"
        acttxt += "- type: pythonfile\n"
        acttxt += "  tag: BoolShowHide\n"
        acttxt += "  pythonfile:\n"
        acttxt += "      file: xAgeSDLBoolShowHide\n"
        acttxt += "      parameters:\n"
        acttxt += "        - type: string\n"
        acttxt += "          value: " + str(obj.name) + "Vis\n"
        acttxt += "        - type: bool\n"
        acttxt += "          value: true\n"


        print "Resulting Code for .logic.modifiers:\n",modtxt
        print "Resulting Code for .logic.actions:\n",acttxt

        # Parse the code
        myactscript = AlcScript(acttxt).GetRootScript()
        mymodscript = AlcScript(modtxt).GetRootScript()

        # Add the parsed script to the correct space in the dictionary, or create that space
        actscript = FindInDict(objscript,"logic.actions",None)
        if actscript is None or type(actscript) != list:
            StoreInDict(objscript,"logic.actions", myactscript)
        else:
            for script in myactscript:
                actscript.append(script)

        modscript = FindInDict(objscript,"logic.modifiers",None)
        if actscript is None or type(modscript) != list:
            StoreInDict(objscript,"logic.modifiers",mymodscript)
        else:
            for script in mymodscript:
                modscript.append(script)

        return True

    return False

# add IntActEnabler
def QuickScript_SDLIntActEnabler(obj):
    print "  [QuickScript - SDLIntActEnabler]"
    objscript = AlcScript.objects.FindOrCreate(obj.name)

    # Check for simpleclick quickscript!
    check = FindInDict(objscript,"quickscript.simpleclick",None)

    if not check is None:
        acttxt  = "- type: pythonfile\n"
        acttxt += "  tag: IntActEnabler\n"
        acttxt += "  pythonfile:\n"
        acttxt += "      file: xAgeSDLIntActEnabler\n"
        acttxt += "      parameters:\n"
        acttxt += "        - type: string\n"
        acttxt += "          value: " + str(obj.name) + "Func\n"
        # Use activator from simpleclick quickscript
        acttxt += "        - type: activator\n"
        acttxt += "          ref: logicmod:$AutoClick\n"
        acttxt += "        - type: string\n"
        acttxt += "          value: 1\n"

        print "Resulting Code for .logic.actions:\n",acttxt

        myactscript = AlcScript(acttxt).GetRootScript()

        # Add the parsed script to the correct space in the dictionary, or create that space
        actscript = FindInDict(objscript,"logic.actions",None)
        if actscript is None or type(actscript) != list:
            StoreInDict(objscript,"logic.actions", myactscript)
        else:
            for script in myactscript:
                actscript.append(script)

        return True
    else:
        print "No simpleclick quickscript for " + str(obj.name) + ": Abort SDLIntActEnabler\n"

    return False


def QuickScript_SimpleClickable(obj):
    objscript = AlcScript.objects.FindOrCreate(obj.name)

    region = getTextPropertyOrDefault(obj,"region",None)
    if not region is None:
        clickfile = getTextPropertyOrDefault(obj,"clickfile",None)
        animation = getTextPropertyOrDefault(obj,"animation",None)
        animtarget = getTextPropertyOrDefault(obj,"animtarget","/")
        autorun = getTextPropertyOrDefault(obj,"autorun","false")
        soundemitter = getTextPropertyOrDefault(obj,"soundemitter",None)
        facevalue = getTextPropertyOrDefault(obj,"facevalue",None)
    else:
        clickfile =     FindInDict(objscript,"quickscript.simpleclick.pythonfile",None)
        region =        FindInDict(objscript,"quickscript.simpleclick.region",None)
        animation =     FindInDict(objscript,"quickscript.simpleclick.animation",None)
        animtarget =    FindInDict(objscript,"quickscript.simpleclick.animtarget","/")
        autorun =       FindInDict(objscript,"quickscript.simpleclick.autorun","false")
        soundemitter =  FindInDict(objscript,"quickscript.simpleclick.soundemitter",None)
        facevalue =     FindInDict(objscript,"quickscript.simpleclick.facevalue",None)

    if not animation is None and clickfile is None:
        # User wants animation but does not use python file: force autorun
        autorun = "true"

    if not soundemitter is None:
        emitscript = AlcScript.objects.FindOrCreate(soundemitter)
        emitvolume = FindInDict(emitscript,"sound.volume",1)

    if not region is None:
        print "  [QuickScript - Simple Clickable]"
        # Force the object's physical logic to 'detect'
        StoreInDict(objscript,"physical.physlogic","detect")
            # Build up the required script

        modtxt  = "- tag: AutoClick\n"
        modtxt += "  cursor: poised\n"
        modtxt += "  flags:\n"
        modtxt += "    - localelement\n"
        modtxt += "  activators:\n"
        modtxt += "    - type: objectinvolume\n"
        modtxt += "      remote: "+str(region)+"\n"
        modtxt += "      triggers:\n"
        modtxt += "        - any\n"
        modtxt += "  conditions:\n"
        modtxt += "    - type: activator\n"
        modtxt += "      activators:\n"
        modtxt += "        - type: picking\n"
        modtxt += "    - type: objectinbox\n"
        modtxt += "      satisfied: true\n"

        if not facevalue is None:
        # facing condition was broken because default tolerance in alc_LogicClasses is -1.0
            modtxt += "    - type: facing\n"
            modtxt += "      satisfied: true\n"
            modtxt += "      directional: true\n"
            modtxt += "      tolerance: " + str(facevalue) + "\n"

        modtxt += "  actions:\n"

        if not clickfile is None:
            modtxt += "    - type: pythonfile\n"
            modtxt += "      ref: $AutoClick\n"

        if not animation is None:
            if str(autorun).lower() == "true":
                modtxt += "    - type: oneshot\n"
                modtxt += "      ref: $AutoClick\n"

        if not soundemitter is None:
            modtxt += "    - type: responder\n"
            modtxt += "      ref: $SoundResp\n"

        acttxt = ""

        if not clickfile is None:
            acttxt += "- type: pythonfile\n"
            acttxt += "  tag: AutoClick\n"
            acttxt += "  pythonfile:\n"
            acttxt += "      file: "+str(clickfile)+"\n"
            acttxt += "      parameters:\n"
            acttxt += "        - type: activator\n"
            acttxt += "          ref: logicmod:$AutoClick\n"
            acttxt += "        - type: string\n"
            acttxt += "          value: "+str(obj.name) +"\n"

            if not animation is None:
                if str(autorun).lower() == "false":
                    acttxt += "        - type: behavior\n"
                    acttxt += "          ref: oneshotmod:$AutoClick\n"

        if not animation is None:
            acttxt += "- type: oneshot\n"
            acttxt += "  tag: AutoClick\n"
            acttxt += "  oneshot:\n"
            acttxt += "      animation: "+str(animation)+"\n"
            acttxt += "      seektime: 1.0\n"

            if not animtarget is None:
                acttxt += "      remote: "+str(animtarget)+"\n"

        if not soundemitter is None:
            acttxt += "- type: responder\n"
            acttxt += "  tag: SoundResp\n"
            acttxt += "  responder:\n"
            acttxt += "    states:\n"
            acttxt += "      - cmds:\n"
            acttxt += "          - type: soundmsg\n"
            acttxt += "            params:\n"
            acttxt += "                receivers:\n"
            acttxt += "                  - 0011:" + str(soundemitter) + "\n"
            acttxt += "                cmds:\n"
            acttxt += "                  - play\n"
            acttxt += "                  - setvolume\n"
            acttxt += "                volume: " + str(emitvolume) + "\n"
            acttxt += "            waiton: -1\n"
            acttxt += "        nextstate: 0\n"
            acttxt += "        waittocmd: 0\n"
            acttxt += "    curstate: 0\n"
            acttxt += "    flags:\n"
            acttxt += "      - detecttrigger\n"


        print "Resulting Code for .logic.modifiers:\n",modtxt
        print "Resulting Code for .logic.actions:\n",acttxt

        # Parse the code
        myactscript = AlcScript(acttxt).GetRootScript()
        mymodscript = AlcScript(modtxt).GetRootScript()

        # Add the parsed script to the correct space in the dictionary, or create that space
        actscript = FindInDict(objscript,"logic.actions",None)
        if actscript is None or type(actscript) != list:
            StoreInDict(objscript,"logic.actions", myactscript)
        else:
            for script in myactscript:
                actscript.append(script)

        modscript = FindInDict(objscript,"logic.modifiers",None)
        if actscript is None or type(modscript) != list:
            StoreInDict(objscript,"logic.modifiers",mymodscript)
        else:
            for script in mymodscript:
                modscript.append(script)

        return True

    return False




