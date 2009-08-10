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
Submenu: '1.5 to 1.6 - Compatibility Report' w_Wizard_15_to_16_report
Submenu: '1.5 to 1.6 - Convert Texture Transform' w_Wizard_15_to_16_textransform
Submenu: '0.5 to 1.x - Upgrade Book' i_upgrade_book
Submenu: '0.5 to 1.x - Upgrade properties' w_Wizard_property_update
Submenu: 'Add missing Blender materials and textures' w_Wizard_mattex_create
Submenu: 'Assign default bounds to selected objects' i_setbounds
Submenu: 'Clear Shadbuf from all Materials' w_antiShadow
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

from PyPRP import prp_Config
prp_Config.startup()

import Blender, time, sys, os
from os.path import *

import PyPRP
from PyPRP.prp_Wizards import Wizard_BookUpgrade

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
        print Blender.Object.RBShapes
        sobject.rbShapeBoundType = Blender.Object.RBShapes["POLYHEDERON"]

def do_main():
    args = __script__['arg']
    w = args.split("_", 1)
    if w[0] == "i":
        # call function defined in this file
        globals()[w[1]]()
    elif w[0] == "w":
        # call function defined in prp_Wizards
        getattr(PyPRP.prp_Wizards, w[1])()
    else:
        raise "Unknown options %s" %(w)


#Main code
do_main()

