#
# $Id: alcspecialobjs.py 795 2007-04-16 01:11:02Z Robert The Rebuilder $
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

# Help library

try:
    import Blender
except ImportError:
    pass

import dircache, os, StringIO
from os.path import *
from binascii import *
from alc_AlcScript import *

class alcBook:
    PageFlags = \
    { \
        "none"       :  0x0, \
        "local"      :  0x1, \
        "volatile"   :  0x2, \
        "reserved"   :  0x4, \
        "builtin"    :  0x8, \
        "itinerant"  : 0x10  \
    }
    
    def __init__(self,parent):
        # Parent is of type alcUruPage - and uses this class to load settings
        self.age=parent
        self.pages=None

        bookscript = AlcScript.book
        self.book = bookscript.FindOrCreate('age')
        
        self.globals = bookscript.FindOrCreate('config')
        
        self.texs = bookscript.FindOrCreate('textures')
    

    def getFromBlender(self):
        # Reset the parent
        self.age.setDefaults()
        self.age.addBuiltInPages() # we don't want to have to add these....

        # Load in several settings
        value = FindInDict(self.book,"starttime")
        if not value is None:
            self.age.addOpt("StartDateTime",str(value))
        
        value = FindInDict(self.book,"daylength")
        if not value is None:
            self.age.addOpt("DayLength",value)
        
        value = FindInDict(self.book,"maxcapacity")
        if not value is None:
            self.age.addOpt("MaxCapacity",value)
        
        value = FindInDict(self.book,"lingertime")
        if not value is None:
            self.age.addOpt("LingerTime",value)
        
        value = FindInDict(self.book,"sequenceprefix")
        if not value is None:
            self.age.addOpt("SequencePrefix",value)
        
        if str(FindInDict(self.globals,"agesdlhook","false")).lower() == 'true':
            self.age.attach['AgeSDLHook'] = True
        else:
            self.age.attach['AgeSDLHook'] = False
        
        value = FindInDict(self.texs,"pack", [])
        if type(value) == list:
            for _tex in value:
                self.age.specialtex.append(_tex)
            
        # Now process the page list....
        
        self.pages = FindInDict(self.book,'pages',[])
        if type(self.pages) == list:
            for _page in self.pages:
                num = FindInDict(_page,'index',-1)
                if num != -1 and num != -2: # No need to add the BuiltIn and Textures prp pages...
                    # Find the name
                    name = FindInDict(_page,'name','room'+str(num))
                    
                    # Find the hide setting (which defaults to none)
                    if str(FindInDict(_page,'hide','false')).lower() == 'true':
                        hide = 1
                    else:
                        hide = 0
                    
                    # Build up a page type from various flags...
                    pagetype = 0
                    typeflags = FindInDict(_page,'flags',[])
                    if type(typeflags) == list:
                        for flag in typeflags:
                            if alcBook.PageFlags.has_key(flag.lower()):
                                pagetype |= alcBook.PageFlags[flag.lower()]

                    # And add the page..
                    self.age.addPage(name,num,hide,pagetype)
        
    def storeToBlender(self):
        # Reset the alcscript
        self.book.clear()

        # Store several settings
        
        value = self.age.getOpt("StartDateTime")
        if not value is None:
            StoreInDict(self.book,"starttime",value)
        
        value = self.age.getOpt("DayLength")
        if not value is None:
            StoreInDict(self.book,"daylength",value)
        
        value = self.age.getOpt("MaxCapacity")
        if not value is None:
            StoreInDict(self.book,"maxcapacity",value)
        
        value = self.age.getOpt("LingerTime")
        if not value is None:
            StoreInDict(self.book,"lingertime",value)
        
        value = self.age.getOpt("SequencePrefix")
        if not value is None:
            StoreInDict(self.book,"sequenceprefix",value)

        if self.age.attach.has_key('AgeSDLHook') and self.age.attach['AgeSDLHook'] == True:
            StoreInDict(self.globals,"agesdlhook",True)
        else:
            StoreInDict(self.globals,"agesdlhook",False)

        # Now loop through all the pages
        PageList = []
        for page in self.age.pages:
            if page.num != -1 and page.num != -2: # Don't include the built in types....
                pagedict = {"index" : page.num,'name' : page.name}
                if page.hide > 0:
                    pagedict['hide'] = True
                
                if page.type > 0:
                    pagedict['flags'] = []
                    for flag in alcBook.PageFlags.keys():
                        if page.type & alcBook.PageFlags[flag]:
                            pagedict['flags'].append(flag)
                
                PageList.append(pagedict)
        StoreInDict(self.book,"pages",PageList)
        

