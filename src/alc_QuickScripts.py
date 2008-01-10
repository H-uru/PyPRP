#
# $Id: alc_QuickScripts.py 843 2007-09-13 01:19:29Z Trylon $
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
from alcdxtconv import *
from alchexdump import *
from alc_Functions import *
from alc_AlcScript import *
from alc_RefParser import *


def QuickScript_Footstep(surface):
    # Build up the required script
    
    txt  = "modifiers:\n"
    txt += "  - tag: Enter\n"
    txt += "    flags:\n"
    txt += "      - multitrigger\n"
    txt += "    activators:\n"
    txt += "      - type: objectinvolume\n"
    txt += "    conditions:\n"
    txt += "      - type: volumesensor\n"
    txt += "        satisfied: true\n"
    txt += "        direction: enter\n"
    txt += "    actions:\n"
    txt += "      - type: responder\n"
    txt += "        ref: /\n"
    txt += "\n"
    txt += "  - tag: Exit\n"
    txt += "    flags:\n"
    txt += "      - multitrigger\n"
    txt += "    activators:\n"
    txt += "      - type: objectinvolume\n"
    txt += "    conditions:\n"
    txt += "      - type: volumesensor\n"
    txt += "        satisfied: true\n"
    txt += "        direction: exit\n"
    txt += "    actions:\n"
    txt += "      - type: responder\n"
    txt += "        ref: /n"
    txt += "\n"
    txt += "actions:\n"
    txt += "  - type: responder\n"
    txt += "    responder:\n"
    txt += "      states:\n"
    txt += "        - cmds:\n"
    txt += "            - type: footstep\n"
    txt += "              params:\n"
    txt += "                  surface: " + str(surface) + "\n"  
    txt += "              waiton: -1\n"
    txt += "          nextstate: 0\n"
    txt += "          waittocmd: 0\n"
    txt += "      curstate: 0\n"
    txt += "      flags:\n"
    txt += "        - detect_trigger\n"
    
    return txt
    
def QuickScript_FootstepList(surfaces):
    # Build up the required script
    
    txt  = "modifiers:\n"
    txt += "  - tag: Enter\n"
    txt += "    flags:\n"
    txt += "      - multitrigger\n"
    txt += "    activators:\n"
    txt += "      - type: objectinvolume\n"
    txt += "    conditions:\n"
    txt += "      - type: volumesensor\n"
    txt += "        satisfied: true\n"
    txt += "        direction: enter\n"
    txt += "    actions:\n"
    txt += "      - type: responder\n"
    txt += "        ref: /\n"
    txt += "\n"
    txt += "  - tag: Exit\n"
    txt += "    flags:\n"
    txt += "      - multitrigger\n"
    txt += "    activators:\n"
    txt += "      - type: objectinvolume\n"
    txt += "    conditions:\n"
    txt += "      - type: volumesensor\n"
    txt += "        satisfied: true\n"
    txt += "        direction: exit\n"
    txt += "    actions:\n"
    txt += "      - type: responder\n"
    txt += "        ref: /n"
    txt += "\n"
    txt += "actions:\n"
    txt += "  - type: responder\n"
    txt += "    responder:\n"
    txt += "      states:\n"
    txt += "        - cmds:\n"
    
    first = False
    for surface in list(surfaces):
        txt += "            - type: footstep\n"
        txt += "              params:\n"
        txt += "                  surface: " + str(surface) + "\n"  
        if not first:
            txt += "                  append: false\n"  
        else:
            txt += "                  append: true\n"  
        
        txt += "              waiton: -1\n"

    txt += "          nextstate: 0\n"
    txt += "          waittocmd: 0\n"
    txt += "      curstate: 0\n"
    txt += "      flags:\n"
    txt += "        - detect_trigger\n"
    
    return txt
    
def QuickScript_SelfAnimationRegion(animation):

    txt  = "modifiers:\n"
    txt += "  - tag: Detect\n"
    txt += "    flags:\n"
    txt += "      - multitrigger\n"
    txt += "    activators:\n"
    txt += "      - type: objectinvolume\n"
    txt += "        triggers:\n"
    txt += "          - enter\n"
    txt += "    conditions:\n"
    txt += "      - type: volumesensor\n"
    txt += "        direction: enter\n"
    txt += "    actions:\n"
    txt += "      - type: oneshot\n"
    txt += "        ref: /\n"
    txt += "actions:\n"
    txt += "  - type: oneshot\n"
    txt += "    oneshot: \n"
    txt += "        animation: " + str(animation) + "\n"
    
    return txt

def QuickScript_OnOffSDL(sdlname):

    txt += "actions:\n"
    txt += "  - type: pythonfile\n"
    txt += "    pythonfile:\n"
    txt += "        file: xAgeSDLBoolShowHide\n"
    txt += "        parameters:\n"
    txt += "          - type: string\n"
    txt += "            value: " + str(sdlname) + "\n"
    txt += "          - type: bool\n"
    txt += "            value: true\n"
    
    return txt

def QuickScript_SimpleClickable(regionname,objectname):

    txt = ""

    return txt


def QuickScript_SimpleAnimClickable(regionname,objectname,animname):

    txt = ""

    return txt


            