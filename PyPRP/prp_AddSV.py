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
Name: 'PyPRP Soft Volumes'
Blender: 243
Group: 'Add'
Submenu: 'Add a Soft Volume Plane' i_svplane
Submenu: 'Add a Soft Volume Cube' i_svcube
Tooltip: 'GoW PyPRP Softvolumes'
"""

__author__ = "GoW PyPRP Team"
__url__ = ("blender", "elysiun",
"Author's homepage, http://www.guildofwriters.com")
__version__ = "GoW PRP Exporter"

__bpydoc__ = """\
This script creates soft volumes in the PRP format
used in URU.
"""

import Blender, time, sys, os
from os.path import *
from PyPRP.prp_Functions import *
from PyPRP.prp_ResManager import *


def new_softvolumeplane():
    print "Adding a new Soft Volume - Plane"
    alcCreateSoftVolumePlane()
    Blender.Redraw()

def new_softvolumecube():
    print "Adding a new Soft Volume - Cube"
    alcCreateSoftVolumeCube()
    Blender.Redraw()

def do_main():
    args = __script__['arg']
    w = args.split("_")
    if w[1]=="svplane":
        new_softvolumeplane()
    elif w[1]=="svcube":
        new_softvolumecube()
    else:
        raise "Unknown options %s" %(w)


#Main code
do_main()

