#!BPY
#
# $Id: uruprp_objectopts.py 425 2006-03-15 20:52:43Z Robert The Rebuilder $
#
#    Copyright (C) 2005-2008  Alcugs PyPRP Project Team and 2008 GoW PyPRP Project Team
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
Blender: 245
Group: 'Object'
Submenu: 'Copy Logic Properties from main selection to secondary selection' i_CopyProperties
Submenu: 'Ignore textures during per-page-texture export' i_ignore
Tooltip: 'GoW PyPRP'
"""

__author__ = "GoW PyPRP Team"
__url__ = ("blender", "elysiun",
"Author's homepage, http://www.guildofwriters.com")
__version__ = "GoW PRP Exporter"

__bpydoc__ = """\
This script modifies/adds certain object properties of URU PRP objects.
"""

import alcconfig
alcconfig.startup()

import Blender, time, sys, os
from Blender import Object
from os.path import *
from alc_Functions import *
from alcresmanager import *


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



def ignoreTextures():
    l = Blender.Object.GetSelected()
    for obj in l:
        try:
            p = obj.getProperty("ignorePPT")
            obj.removeProperty(p)
        except:
            pass
        obj.addProperty("ignorePPT",True,'BOOL')
    Blender.Draw.PupMenu('Ignored textures in %d objects.' % (len(l)))


def do_main():
    args = __script__['arg']
    w = args.split("_")
    if w[1]=="CopyProperties":
        CopyProperties()
    elif w[1]=="ignore":
        ignoreTextures()
    else:
        raise "Unknown options %s" %(w)



#Main code
do_main()
