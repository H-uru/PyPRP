#!BPY
#
# $Id: uruprp_addbook.py 813 2007-04-27 03:16:10Z Robert The Rebuilder $
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

"""
Name: 'PyPRP Wizards'
Blender: 245
Group: 'Wizards'
Submenu: 'Upgrade Book (Keep old objects)' i_book_keepold
Submenu: 'Upgrade Book (Delete old objects)' i_book_delold
Submenu: 'Upgrade properties' i_props
Tooltip: 'Alcugs PyPRP Upgrade'
"""

__author__ = "Almlys"
__url__ = ("blender", "elysiun",
"Author's homepage, http://alcugs.almlys.org")
__version__ = "Alcugs PRP exporter 2.45 $Revision: 859 $"

__bpydoc__ = """\
This script attempts to upgrade used styles from the PRP format
used in URU.
"""

import alcconfig
alcconfig.startup()

import Blender, time, sys, os
from os.path import *

import alc_Wizards
from alc_Wizards import *
    
def upgrade_book(RemoveOld):
    print "Upgrading Book Settings"
    Wizard_BookUpgrade(RemoveOld)
    
def do_main():
    args = __script__['arg']
    w = args.split("_")
    if w[1]=="book":
        if w[2] == "delold":
            upgrade_book(True)
        else:
            upgrade_book(False)
    elif w[1]=="props":
        Wizard_alctype_update()
    else:
        raise "Unknown options %s" %(w)


#Main code
do_main()

