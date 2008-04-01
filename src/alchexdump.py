#
# $Id: alchexdump.py 431 2006-04-02 02:10:02Z AdamJohnso $
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

from binascii import *
import struct
import string

def hexdump(what):
    x=0
    y=0
    print "    ",
    for i in range(0x10):
        print " %X" % i,
    print ""
    info=""
    rinfo=""
    for a in what:
        if x==0:
            print "%04X" %y,
        i=struct.unpack("B",a)
        print "%02X" % i,
        z,=struct.unpack("B",a)
        z=struct.pack("B",z ^ 0xFF)
        if a=="\n" or not a in string.printable:
            a="_"
        if z=="\n" or not z in string.printable:
            z="_"
        info = info + a
        rinfo = rinfo + z
        x=x+1
        if x==0x10:
            x=0
            y=y+1
            print info + " " + rinfo
            info=""
            rinfo=""
    if x!=0x10:
        for i in range(x,0x10):
            print "  ",
        print info,
        for i in range(x,0x10):
            print "",
        print rinfo


#hexdump("aeiou \nasdfghijklmnopqrstuvwxyz" )

