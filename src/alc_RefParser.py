#
# $Id: alc_RefParser.py 843 2007-09-13 01:19:29Z Trylon $
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


import md5, random, binascii, cStringIO, copy, Image, math, struct, StringIO, os, os.path, pickle
from alcurutypes import *

class ScriptRefParser:
    NameToType = \
    { \
        "scnobj"        : 0x0001, \
        "audioiface"    : 0x0011, \
        "logicmod"      : 0x002D, \
        "pyfileMod"     : 0x00A2, \
        "sitmod"        : 0x00AE, \
        "animeventmod"  : 0x00C4, \
        "npcspawnmod"   : 0x00F5, \
        "respondermod"  : 0x007C, \
        "dyntextmap"    : 0x00AD, \
        "guidialogmod"  : 0x0098, \
        "exregionmod"   : 0x00A4, \
        "agmastermod"   : 0x006D, \
        "msgfwder"      : 0x00A8, \
        "oneshotmod"    : 0x0077, \
        "mstagebehmod"  : 0x00C1, \
        "mipmap"        : 0x0004, \
        "waveset"       : 0x00FB, \
        "swimcircular"  : 0x0134, \
        "swimstraight"  : 0x0136, \
        "clustergroup"  : 0x012B, \
        "layeranim"     : 0x0043, \
        "softvolume"    : 0x0088, \
        "svunion"       : 0x008A, \
        "svintersect"   : 0x008B, \
        "svinvert"      : 0x008C, \
    }

    def __init__(self,page,basename="",defaulttype = None, allowlist = [],version=5):
        self.page = page
        self.basename = basename
        self.defaulttype = defaulttype
        self.allowlist = allowlist
        self.version=5

    # This class helps with figuring out object references in pages
    # It is in a separate file to allow access from any class
    #
    # Definitions:
    # - "TagString" refers to a generic descriptor of type ":<name>", "$tag"
    # - "RefString" refers to "<type>:<name>[@<pagename>]" 
    # - "MixedRef" refers to both types


    def _MixedRef_GetType(value):
        svalue = str(value)
        if value == str(None) or svalue == "/" or svalue == "":
            return "NONE"
        elif svalue[0] == ":":
            #value is a full name ref, ($<fullname>)
            return "NAME"
        elif svalue[0] == "$":
            #value is tag ($<tag>)
            return "TAG"
        elif ScriptRefParser.IsRefString(svalue):
            return "REFSTRING"
        else:
            # neither - up to the caller to determine how to handle it
            return "DEFAULT"

    MixedRef_GetType = staticmethod(_MixedRef_GetType)

    def _TagString_GetBareName(value):
        svalue = str(value)
        reftype = ScriptRefParser.MixedRef_GetType(svalue)
        if reftype == "NONE":
            return ""
        elif reftype == "NAME" or reftype == "TAG":
            #value is a name ref or tag...
            return svalue[1:len(value)]
        elif reftype == "REFSTRING":
            # since refstrings are trouble in these circumstances, consider it as NONE
            return ""
        else:
            return value

    TagString_GetBareName = staticmethod(_TagString_GetBareName)

    def _TagString_ParseName(value,rootname):
        reftype = ScriptRefParser.MixedRef_GetType(value)
        if reftype == "NONE":
            return rootname
        elif reftype == "NAME" or reftype == "DEFAULT":
            #value is a full name ref, (:<fullname>)
            return ScriptRefParser.TagString_GetBareName(value)
        elif reftype == "TAG":
            #value is tag ( $<tag>)
            return rootname + "_" + ScriptRefParser.TagString_GetBareName(value)
        elif reftype == "REFSTRING":
            # since refsctrings are trouble in these circumstances, consider it as NONE
            return rootname
        else:
            # value is not a tag reference but we'll default to it in this case...
            return rootname + "_" + ScriptRefParser.TagString_GetBareName(value)

    TagString_ParseName = staticmethod(_TagString_ParseName)

    def _IsRefString(keystring):
        keyinfo = ScriptRefParser.RefString_Decode(keystring)
        
        if not keyinfo is None:
            return True
        else:
            return False
    IsRefString = staticmethod(_IsRefString)

    def _RefString_Decode(keystring):
        if type(keystring) == str:
            # <typenr>:<fullname>[@<page>]
            
            # first split it on page name - Just don't use @'s in names....
            a = keystring.split('@')
            if len(a) > 0:
                if len(a) > 1:
                    pagename = a[1]
                    
                else:
                    pagename = None
                        
                type_name = a[0]
                
                # split the type from the name (':'s can be used in names, as there is always a type nr
                b = type_name.split(':') 
                if len(b) > 1:
                    type_id = b[0] # get type nr
                    # concatenate remaining args again
                    name = b[1]
                    for i in range(2,len(b)):
                        name += ":" + b[i]

                    # try to decode the first param as a typename
                    try:
                        keytype = ScriptRefParser.NameTypeDecode(type_id)
                    except:
 #                       print "Error decoding keytype:",type_id
                        return None

                    return { 'type': keytype, "name": name,"pagename": None }
                
                else:
                    return None
            else:
                return None
        else:
            return None
    RefString_Decode = staticmethod(_RefString_Decode)

    def _NameTypeDecode(_type):
        # try to decode the first param as a typename
        if ScriptRefParser.NameToType.has_key(_type):
            return ScriptRefParser.NameToType[_type]
        else:
            if type(_type) == int:
                return _type
            else:
                # or as number if not in list
                try:
                    # type needs to be in base 16 coding
                    return int(_type,16)
                except:
#                    print "WARNING: Could not decode %s to an object type code. Type of object:"%(_type),type(_type)
                    raise ValueError, "Decoding error"   
    NameTypeDecode = staticmethod(_NameTypeDecode)

    # Next we have object functions

    def SetDefaultType(self,defaulttype):
        self.defaulttype = defaulttype
    
    def ClearDefaultType(self):
        self.defaulttype = None
    
    def SetAllowList(self,allowlist):
        self.allowlist = allowlist
    
    def ClearAllowList(self):
        self.allowlist = []


    def TagString_FindCreate(self,keystring,create=True):
        # it's a simple reference (name or tag) = so parse it accordingly on the current
        # page...
        # This function needs "defaulttype" to be set, and prefers "self.basename" to be set
        if not self.defaulttype is None:
            # try to decode the first param as a typename
            try:
                keytype = ScriptRefParser.NameTypeDecode(self.defaulttype)
            except ValueError,detail:
#                print "Error:",detail,"on keystring",keystring,"and basetype",self.defaulttype
                return None                
        
            refname = ScriptRefParser.TagString_ParseName(keystring,self.basename)

            if refname != "":
                return self.page.find(keytype,refname,create)
            else:
                return None
        else:
            return None

    def TagString_Find(self,keystring):
        return self.TagString_FindCreate(keystring,False)

    def TagString_FindCreateRef(self,keystring):
        return self.ObjToRef(self.TagString_FindCreate(keystring))

    def TagString_FindRef(self,keystring):
        return self.ObjToRef(self.TagString_Find(keystring))


    def RefString_FindCreate(self,keystring,create=True):
        # this parses a RefString for the current page if possible
        # 
        resmgr = self.page.resmanager

        keyinfo = ScriptRefParser.RefString_Decode(keystring)
                    
        if not keyinfo is None:
            # if we havea basename set, we can see if it is a tag, and act on that accordingly
            # in a refstring we accept "$<tag>" for tags and  "/" for default name - but only if a 
            # basename is set
            
            if not self.basename is None and self.basename != "":
                nametype = ScriptRefParser.MixedRef_GetType(keyinfo['name'])
                if nametype == "TAG" or nametype == "NONE":
                    name = ScriptRefParser.TagString_ParseName(keyinfo['name'],self.basename)
                else:
                    name = keyinfo['name']
            else:
                name = keyinfo['name']

            if name != "":
    
                # Try to find the page referenced...
                # If not possible, we default back to the current page
                if not keyinfo["pagename"] is None:
                    page=resmgr.findPrp(str(keyinfo["pagename"]))
                    if page is None:
                        page = self.page
                else:
                    page = self.page
                
                # see if the object type is in the allow list
                if len(self.allowlist) == 0 or keyinfo["type"] in self.allowlist:
                    return page.find(keyinfo["type"],name,create)
                else:
                    print "Warning: Key type",keyinfo["type"],"is not list of allowes types:",self.allowlist
                    return None
            else:
                return None
        else:
            return None

    def RefString_Find(self,keystring):
        return self.RefString_FindCreate(keystring,False)

    def RefString_FindCreateRef(self,keystring):
        return self.ObjToRef(self.RefString_FindCreate(keystring))

    def RefString_FindRef(self,keystring):
        return self.ObjToRef(self.RefString_Find(keystring))

    
    def MixedRef_FindCreate(self,keystring,create=True):
#        print " Decoding MixedRef:",keystring
        reftype = ScriptRefParser.MixedRef_GetType(keystring)

        plobj = None
        if reftype != "REFSTRING" and (not self.defaulttype is None):
            plobj = self.TagString_FindCreate(keystring,create)
        else: # reftype == "REFSTRING":
            plobj = self.RefString_FindCreate(keystring,create)

        return plobj
    
    def MixedRef_Find(self,keystring):
        return self.MixedRef_FindCreate(keystring,False)

    def MixedRef_FindCreateRef(self,keystring):
        return self.ObjToRef(self.MixedRef_FindCreate(keystring))

    def MixedRef_FindRef(self,keystring):
        return self.ObjToRef(self.MixedRef_Find(keystring))

    def ObjToRef(self,obj):
        if obj is None:
            return UruObjectRef(self.version)
        else:
            return obj.data.getRef()
