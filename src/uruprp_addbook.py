#!BPY
#
# $Id: uruprp_addbook.py 813 2007-04-27 03:16:10Z Robert The Rebuilder $
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

"""
Name: 'PyPRP'
Blender: 243
Group: 'Add'
Submenu: 'Create a New Book' i_book
Submenu: 'Create a New SpawnPoint' i_swpoint
Submenu: 'Add a (Generic) Logic Region' i_region
Submenu: 'Add a Footstep Sound Region' i_footstepregion
Submenu: 'Add a Panic Link Region' i_paniclnkregion
Tooltip: 'GoW PyPRP'
"""

__author__ = "GoW PyPRP Team"
__url__ = ("blender", "elysiun",
"Author's homepage, http://www.guildofwriters.com")
__version__ = "GoW PRP Exporter"

__bpydoc__ = """\
This script attempts to provide easy Age Writing options to be used in URU.
"""

import alcconfig
alcconfig.startup()

import Blender, time, sys, os
from Blender import NMesh
from Blender.BGL import *
from Blender.Draw import *
from os.path import *
from alcresmanager import *
from alc_AlcScript import *
from alc_Functions import *

import math
from math import *

def new_book():
	print "Creating default Book..."
	txt=alcFindBlenderText("Book")
	txt.clear()
	txt.write("""age:
	sequenceprefix: 100
	daylength: 24.0
	maxcapacity: 10
	starttime: 0
	lingertime: 180

	pages:
		- index: 0
		  name: mainRoom

config:
	agesdlhook: true
	""")
	print "Done."
	print "Setting default Funny settings..."
	txt=alcFindBlenderText("init")
	txt.clear()
	txt.write("#--Fog settings--\n#Graphics.Renderer.SetYon float yon\n#Visibility distance\nGraphics.Renderer.SetYon 100000\n\n#Graphics.Renderer.Fog.SetDefLinear float start, float end, float density\n#Fog depth\nGraphics.Renderer.Fog.SetDefLinear 1 1000 1\n\n#Graphics.Renderer.Fog.SetDefExp2 float end, float density\n#Graphics.Renderer.Fog.SetDefExp2 100000 20\n\n#Graphics.Renderer.Fog.SetDefColor float r, float g, float b\nGraphics.Renderer.Fog.SetDefColor 0 0 0\n\n#Graphics.Renderer.SetClearColor float r, float g, float b\nGraphics.Renderer.SetClearColor 0 0 0\n")
	print "Done."
	print "Setting default AlcScript settings..."
	txt=alcFindBlenderText("AlcScript")
	txt.clear()
	txt.write("""# insert AlcScript code here""")
	print "Done. Book successfully created!"

def new_point():
    print "Adding a new SpawnPoint"
    alcCreateLinkInPoint()
    Blender.Redraw()

def new_region():
    print "Adding a new General Region"
    alcCreateRegion()
    Blender.Redraw()

def new_footstepregion():
    print "Adding a new Footstep Sound Region"
    alcCreateFootstepRegion()
    Blender.Redraw()

def new_paniclnkregion():
    print "Adding a new Panic Link Region"
    alcCreatePanicLnkRegion()
    Blender.Redraw()

def do_main():
    args = __script__['arg']
    w = args.split("_")
    if w[1]=="book":
        new_book()
    elif w[1]=="swpoint":
        new_point()
    elif w[1]=="region":
        new_region()
    elif w[1]=="footstepregion":
        new_footstepregion()
    elif w[1]=="paniclnkregion":
        new_paniclnkregion()

    else:
        raise "Unknown options %s" %(w)


#Main code
do_main()