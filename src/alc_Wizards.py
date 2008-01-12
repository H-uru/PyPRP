#
# $Id: alc_Wizards.py 876 2007-12-15 22:15:11Z Paradox $
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
    try:
        from Blender import NMesh, Object, Mathutils
    except Exception, detail:
        print detail
except ImportError:
    pass

import random, md5,math, binascii, struct

from alc_AlcScript import *
from alcspecialobjs import *
import alc_Functions
from alc_Functions import *

def Wizard_BookUpgrade(RemoveOld = False):
    age = { \
        "sequenceprefix" : 99, \
        "startdatetime" : 12, \
        "daylength" : 24.4, \
        "maxcapacity" : 152, \
        "lingertime" : 181, \
        }
    config = {}
    pages = {}
    
    oldbookobjects = []
    
    scene = Blender.Scene.GetCurrent()
    for obj in list(scene.objects):
        # if this object has a "book" property, ignore it
        try:
            p=obj.getProperty("book")
            print " Found Book on object %s"%(obj.name)
            # If we haven't crashed, we have a book type
            
            try:
                # Now extract the properties
                p = obj.getProperty('SequencePrefix')
                print p
                age["sequenceprefix"] = getStrIntPropertyOrDefault(obj,"SequencePrefix",100)
    
                p = obj.getProperty('StartDateTime')
                print p
                time = getTextPropertyOrDefault(obj,"StartDateTime",0)
    
                try:
                    age["startdatetime"] = int(time,10)
                except:
                    age["startdatetime"] = 0
                    
                p = obj.getProperty('DayLength')
                print p
                age["daylength"] = float(getTextPropertyOrDefault(obj,"DayLength",24.0))
                
                p = obj.getProperty('MaxCapacity')
                print p
                age["maxcapacity"] = getStrIntPropertyOrDefault(obj,"MaxCapacity",150)
    
                p = obj.getProperty('LingerTime')
                print p
                age["lingertime"] = getStrIntPropertyOrDefault(obj,"LingerTime",180)
                
                config["agesdlhook"] = bool(getBoolPropertyOrDefault(obj,"AgeSDLHook",False))
                
                oldbookobjects.append(obj)
            except (AttributeError, RuntimeError),details:
                print "Exception: ",details
        except (AttributeError, RuntimeError),detail:
            pass
        
        # if this object has a "page" property, ignore it too...
        try:
            p=obj.getProperty("page")
            print " Found Page on object %s"%(obj.name)
            
            # If we haven't crashed, we have a book type
            # Now extract the properties
            page = {}

            index = getIntPropertyOrDefault(obj,"page",0)

            page["name"] = getTextPropertyOrDefault(obj,"name","Room"+str(index))

            page["type"] = getIntPropertyOrDefault(obj,"type",0)

            page["hide"] = getIntPropertyOrDefault(obj,"hide",0)
            
            print "  Contents:",page
            # And store this page...
            if index != -1 and index != -2:
                pages[index] = page
            
            oldbookobjects.append(obj)
                
        except (AttributeError, RuntimeError),details:
            pass
    
    if len(pages) == 0:
        pages[0] = {"name": "mainRoom","type": 0,"hide":0}
    
    # Now we can write out the stuff
    text = ""
    
    # First do the age block
    text += "age:\n"
    for key in age.keys():
        text += "\t" + key +": " + str(age[key]) + "\n"
    text += "\n"
    
    # Next print the age.pages block
    text += "\tpages:\n"
    pagekeys = pages.keys()
    pagekeys.sort()
    for key in pagekeys:
        text += "\t\t- index: " + str(key) + "\n"
        text += "\t\t  name: " + pages[key]["name"] + "\n"
        if pages[key]["hide"] > 0:
            text += "\t\t  hide: true\n"
        if pages[key]["type"] > 0:
            text += "\t\t  flags:\n"
            for flag in alcBook.PageFlags.keys():
                if pages[key]["type"] & alcBook.PageFlags[flag]:
                    text += "\t\t\t- " + flag + "\n"
    text += "\n"

    # And finish with the config block
    if len(config.keys()) > 0:
        text += "config:\n"
        for key in config.keys():
            text += "\t" + key +": " + str(config[key]) + "\n"
    
    
    blendtxt=alcFindBlenderText("Book")
    blendtxt.clear()
    blendtxt.write(text)
    
    if RemoveOld:
        for obj in oldbookobjects:
            scene.objects.unlink(obj)
    

def Wizard_alctype_update():
    l = Blender.Object.Get()
    for obj in l:
        name = str(obj.name)
        obj_type=obj.getType()
        try:
            p=obj.getProperty("alctype")
            type=str(p.getData())
            obj.removeProperty(p)
            obj.addProperty("type",type)
        except (AttributeError, RuntimeError):
            pass

        try:
            p=obj.getProperty("prpregion")
            type=str(p.getData())
            obj.removeProperty(p)
            
            if type == "climbregion":
                type = "climbing"
            elif type == "swimregion" or type == "swimrgn":
                type = "swimdetect"
            elif type == "swimplainsfc" or type == "swimscursfc" or type == "swimccursfc":
                type = "swim"
            elif type == "paniclnkrgn":
                type = "panic"
            elif type == "footsteprgn":
                type = "footstep"
            elif type == "camerargn":
                type = "camera"
            elif type == "clickregion":
                type = "logic"
            
            obj.addProperty("regiontype",type)
            
        except (AttributeError, RuntimeError):
            pass
                
        pass

