#!BPY
#
# $Id: uruprp_objectopts.py 425 2006-03-15 20:52:43Z Robert The Rebuilder $
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

# this file contains various options to modify objects and their properties.
## --Trylon

"""
Name: 'PyPRP'
Blender: 237
Group: 'Object'
Submenu: 'Copy Logic Properties from main selection to secondary selection' i_CopyProperties
Submenu: 'Update regions from old-style to new-style' i_fixregions
Submenu: 'Add default collider settings' i_collide
Submenu: 'Show object Info' i_objinfo

Tooltip: 'alcugs pyprp'
"""

__author__ = "Almlys"
__url__ = ("blender", "elysiun",
"Author's homepage, http://alcugs.almlys.dyns.net")
__version__ = "Alcugs PRP exporter 1.3a"

__bpydoc__ = """\
This script modifies/adds certain object properties of URU prp objects
"""

import alcconfig
alcconfig.startup()

import Blender, time, sys, os
from Blender import Object
from os.path import *
#from alcurutypes import *
#from alcspecialobjs import *
#from alcprpfile import *
from alcGObjects import *
from alcresmanager import *

def add_collideinfo():
    print "Adding default colliderinfo"

    l = Blender.Object.GetSelected()
    for obj in l:
        # first remove the existing properties
        try:
            p = obj.getProperty("alctype")
            obj.removeProperty(p)
        except (AttributeError, RuntimeError):
            pass
        try:
            p = obj.getProperty("col_type")
            obj.removeProperty(p)
        except (AttributeError, RuntimeError):
            pass
        try:
            p = obj.getProperty("mass")
            obj.removeProperty(p)
        except (AttributeError, RuntimeError):
            pass
        try:
            p = obj.getProperty("rc")
            obj.removeProperty(p)
        except (AttributeError, RuntimeError):
            pass
        try:
            p = obj.getProperty("el")
            obj.removeProperty(p)
        except (AttributeError, RuntimeError):
            pass
        try:
            p = obj.getProperty("col_flags0")
            obj.removeProperty(p)
        except (AttributeError, RuntimeError):
            pass
        try:
            p = obj.getProperty("col_flags1")
            obj.removeProperty(p)
        except (AttributeError, RuntimeError):
            pass
        try:
            p = obj.getProperty("col_flags2")
            obj.removeProperty(p)
        except (AttributeError, RuntimeError):
            pass
        try:
            p = obj.getProperty("col_flags3")
            obj.removeProperty(p)
        except (AttributeError, RuntimeError):
            pass
        try:
            p = obj.getProperty("col_flags4")
            obj.removeProperty(p)
        except (AttributeError, RuntimeError):
            pass
        try:
            p = obj.getProperty("col_flags5")
            obj.removeProperty(p)
        except (AttributeError, RuntimeError):
            pass

        # now add the new properties
        obj.addProperty("col_type","4")
        obj.addProperty("mass",0.0)
        obj.addProperty("rc",4.0)
        obj.addProperty("el",0.0)
        obj.addProperty("col_flags0","0200")
        obj.addProperty("col_flags1","00000000")
        obj.addProperty("col_flags2","02000000")
        obj.addProperty("col_flags3","0000")
        obj.addProperty("col_flags4","00000080")
        obj.addProperty("col_flags5","00000004")
    Blender.Redraw()

def convert_props():
    l = Blender.Object.Get()
    for obj in l:
        name = str(obj.name)
        obj_type=obj.getType()
        try:
            p=obj.getProperty("alctype")
            alctype=str(p.getData())
        except (AttributeError, RuntimeError):
            alctype="object"
        try:
            p=obj.getProperty("alcspecial")
            alcspecial=str(p.getData())
        except (AttributeError, RuntimeError):
            alcspecial="none"
        
        if (obj_type == "Mesh" and alctype == "collider"):
            if alcspecial in ["footsteprgn","paniclnkrgn","swimrgn","swimplainsfc","swimscursfc","swimccursfc","climbregion","clickregion"]:
                p=obj.getProperty("alctype")
                obj.removeProperty(p)
                p=obj.getProperty("alcspecial")
                obj.removeProperty(p)
                obj.addProperty("alctype","region")
                
                #do a conversion to new object names when neccessary
                prpregion = alcspecial
                    
                obj.addProperty("prpregion",prpregion)

                #remove default properties (depending on the type of region)
                
               
                if(prpregion == "swimrgn"):
                    deldefaultproperty(obj,"mass",0.0);
                    deldefaultproperty(obj,"rc",0.0);
                    deldefaultproperty(obj,"el",0.0);
                    deldefaultproperty(obj,"col_type","1");
                    deldefaultproperty(obj,"col_flags0","0000");
                    deldefaultproperty(obj,"col_flags1","00020000");
                    deldefaultproperty(obj,"col_flags2","00000000");
                    deldefaultproperty(obj,"col_flags3","0000");
                    deldefaultproperty(obj,"col_flags4","00000000");
                    deldefaultproperty(obj,"col_flags5","00000000");
                elif (prpregion == "swimplainsfc") or (prpregion == "swimccursfc") or (prpregion == "swimscursfc"):
                    deldefaultproperty(obj,"mass",0.0);
                    deldefaultproperty(obj,"rc",0.0);
                    deldefaultproperty(obj,"el",0.0);
                    deldefaultproperty(obj,"col_type","4");
                    deldefaultproperty(obj,"col_flags0","0000");
                    deldefaultproperty(obj,"col_flags1","00000000");
                    deldefaultproperty(obj,"col_flags2","00000000");
                    deldefaultproperty(obj,"col_flags3","0000");
                    deldefaultproperty(obj,"col_flags4","00000000");
                    deldefaultproperty(obj,"col_flags5","00000080");
                elif (prpregion == "clickrgn"):
                    deldefaultproperty(obj,"mass",1.0);
                    deldefaultproperty(obj,"rc",0.0);
                    deldefaultproperty(obj,"el",0.0);
                    deldefaultproperty(obj,"col_type","3");
                    deldefaultproperty(obj,"col_flags0","0400");
                    deldefaultproperty(obj,"col_flags1","08000000");
                    deldefaultproperty(obj,"col_flags2","00000000");
                    deldefaultproperty(obj,"col_flags3","0000");
                    deldefaultproperty(obj,"col_flags4","00000004");
                    deldefaultproperty(obj,"col_flags5","00000000");
                elif (prpregion != "unknown"):
                    deldefaultproperty(obj,"mass",1.0);
                    deldefaultproperty(obj,"rc",0.0);
                    deldefaultproperty(obj,"el",0.0);
                    deldefaultproperty(obj,"col_type","3");
                    deldefaultproperty(obj,"col_flags0","0400");
                    deldefaultproperty(obj,"col_flags1","08000000");
                    deldefaultproperty(obj,"col_flags2","00000000");
                    deldefaultproperty(obj,"col_flags3","0000");
                    deldefaultproperty(obj,"col_flags4","00000004");
                    deldefaultproperty(obj,"col_flags5","00000000");
                
                print "Converted region object \"%s\"" % name 
        pass

def CopyProperties():

    print "---------------"

    # get the selected objects
    obj_list = Blender.Object.GetSelected()
    if(len(obj_list) > 1):
        mainobj = obj_list[0]
        
        prop_list = mainobj.getAllProperties()  
        
        for obj in obj_list:
            if(obj != mainobj):
                print "From [%s] to [%s]" % (mainobj.name,obj.name)
                for prop in prop_list:
                    try:
                        obj.addProperty(prop.name,prop.data)
                        print " Copied property " + prop.name + " => " + prop.data
                    except:
                        pass
    else:
        print "Select Multiple objects for this to work..."


def deldefaultproperty(obj,propertyname,defaultvalue):
    try:
        p=obj.getProperty(propertyname)
        if(p.getData() == defaultvalue):
            obj.removeProperty(p)
    except (AttributeError, RuntimeError):
        print "Error removing %s property" % propertyname

def showObjectInfo():
    HullTypes = {"BOX" : 0, "SPHERE" : 1, "CYLINDER" : 2, "CONE" : 3, "TRIANGLEMESH" : 4, "CONVEXHULL" : 5}

    l = Blender.Object.GetSelected()
    for obj in l:
        name = str(obj.name)

        print "Info on Object [%s]" % name
        if obj.rbFlags & Object.RBFlags["BOUNDS"]:
            print " Object has bounds set"

            if obj.rbShapeBoundType == HullTypes["BOX"]:
                print " Hull shape is box"
            elif obj.rbShapeBoundType == HullTypes["SPHERE"]:
                print " Hull shape is sphere"
            elif obj.rbShapeBoundType == HullTypes["CYLINDER"]:
                print " Hull shape is cylinder"
            elif obj.rbShapeBoundType == HullTypes["CONE"]:
                print " Hull shape is cone"
            elif obj.rbShapeBoundType == HullTypes["TRIANGLEMESH"]:
                print " Hull shape is trianglemesh"
            elif obj.rbShapeBoundType == HullTypes["CONVEXHULL"]:
                print " Hull shape is convexhull"
             
        print "==="
        if obj.rbFlags & (Object.RBFlags["DYNAMIC"] | Object.RBFlags["ACTOR"]):
            print " Object has DYNAMIC properties"
            print "  Mass: %f" % obj.rbMass

        print "==="
        if obj.isSB():
            print " Object has a softbody"
            print " Refriction: %f" % obj.getSBFriction()
            print " Mass: %f" % obj.getSBMass()
            print " Elasticity: %f" % obj.SBSpeed
            




def do_main():
    args = __script__['arg']
    w = args.split("_")
    if w[1]=="collide":
        add_collideinfo()
    elif w[1]=="fixregions":
        convert_props()
    elif w[1]=="CopyProperties":
        CopyProperties()
    elif w[1]=="objinfo":
        showObjectInfo()
    else:
        raise "Unknown options %s" %(w)



#Main code
do_main()

