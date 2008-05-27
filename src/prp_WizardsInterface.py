#!BPY
#
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

"""
Name: 'PyPRP Wizards'
Blender: 245
Group: 'Wizards'
Submenu: 'Upgrade Book' i_book
Submenu: 'Add missing Blender materials and textures' i_mattex
Submenu: 'Upgrade properties' i_props
Submenu: 'Assign default bounds to selected objects' i_bounds
Tooltip: 'GoW PyPRP Upgrade'
"""

__author__ = "GoW PyPRP Team"
__url__ = ("blender", "elysiun",
"Author's homepage, http://www.guildofwriters.com")
__version__ = "GoW PRP Exporter"

__bpydoc__ = """\
This script attempts to upgrade outdated styles from the PRP format
used in URU.
"""

import prp_Config
prp_Config.startup()

import Blender, time, sys, os
from os.path import *

import prp_Wizards
from prp_Wizards import *

def upgrade_book():
    REMOVE_OLD = Blender.Draw.Create(1)
    pup_block = [\
    ('Delete old book objects',REMOVE_OLD,'After converting them to AlcScript, delete the old book objects.'),\
    ]

    if not Blender.Draw.PupBlock('Upgrade books...', pup_block):
        return
    RemoveOld = (REMOVE_OLD.val == 1)

    print "Upgrading Book Settings"
    Wizard_BookUpgrade(RemoveOld)
    if RemoveOld:
        message = "Upgraded books and deleted the old objects."
    else:
        message = "Upgraded books and kept the old objects."
    Blender.Draw.PupMenu(message)

def setbounds():
    objects = Blender.Scene.GetCurrent().objects.selected
    for sobject in objects:
        sobject.rbFlags |= Blender.Object.RBFlags.BOUNDS
        print Object.RBShapes
        sobject.rbShapeBoundType = Blender.Object.RBShapes["POLYHEDERON"]

def do_main():
    args = __script__['arg']
    w = args.split("_")
    if w[1]=="book":
        upgrade_book()
    elif w[1]=="props":
        Wizard_property_update()
    elif w[1]=="bounds":
        setbounds()
    elif w[1]=="mattex":
        Wizard_mattex_create()
    else:
        raise "Unknown options %s" %(w)


#Main code
do_main()

