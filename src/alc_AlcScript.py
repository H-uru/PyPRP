#
# $Id: alc_AdvScript.py 777 2007-11-2 9:00:00Z Trylon $
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
#    Foundation, Inc., 59 Temple Place, Suite ##0, Boston, MA  02111-1#07  USA
#
#    Please see the file COPYING for the full license.
#    Please see the file DISCLAIMER for more details, before doing nothing.

#    This file contains the basic classes for interpreting the advanced settings of objects
#    It uses yaml for the script

import sys, os
import yaml

try:
    import Blender
except ImportError:
    pass

from alc_Functions import *


# Guide for PYPRP programmers:
# 
# This set of classes reads in a yaml (www.yaml.org) formatted scriptset
#
# The AlcScript class uses PyYaml to read this in and format it as a Python Dictionary.
# It also provides a way to convert it from a Python Dictionary into a Yaml script.
#

class AlcScript:

    ObjectTextFileName="AlcScript"
    objects=None
    BookTextFileName="Book"
    book=None # As this one needs to be used for creating a new book as well....

    Debug=False
    def __init__(self,text=""):
        self.Read(text)
        # Initialize to a blank dict if it does not return a list or dict
        if not (type(self.content) == list or type(self.content) == dict): 
            self.content = {}
        
    
    def Read(self,text):
        if AlcScript.Debug:
            print "Parsing Content..."
            print text
            print "---"
            
        self.content = yaml.safe_load(text)

        if AlcScript.Debug:
            print "Parsed result: "
            print self.content
    
    def Write(self):
        return self.WritePart(self.content)
        
    def WritePart(self,data,level=0,AlreadyIndented = False):
        s = ""
        NoIndent = AlreadyIndented
        if type(data) == dict:
            #print "\nDict:",data,"\n"
            keys = data.keys()
            keys.sort()
            for key in keys:
                # Ignore empty dictionaries
                if not (type(data[key]) == dict and len(data[key].keys()) == 0):
                    if not NoIndent:
                        s += "\n"
                        for i in range(level):
                            s += "  "
                    else:
                        NoIndent = False
    
                    s += str(key) + ": "
                    s += self.WritePart(data[key],level + 2) # recurse into next level
                    if(level == 0):
                        s += "\n"
                
        elif type(data) == list:
            #print "\nList:",data,"\n"
            data.sort()
            for item in data:
                # Ignore empty dictionaries
                if not (type(item) == dict and len(item.keys()) == 0):
                    if not NoIndent:
                        s += "\n"
                        for i in range(level):
                            s += "  "
                    else:
                        NoIndent = False
    
                    s += "- "
                    s += self.WritePart(item,level + 1,True) # recurse into next level
                    if(level == 0):
                        s += "\n"
            
        else: # it's a value
            if type(data) == str:
                s += "\"" + str(data) + "\""
            else:
                s += str(data)
        return s
    
    ## Management functions - use these to append or find root dictionary objects for blender objects
    ## They can handle it when we have a root list as well as if we have a root dictionary. That way we're more 
    ## flexible to the user (two different ways of writing are both accepted, less bugs, etc, etc)
    def FindStrict(self,name): # Does return None on return
        if type(self.content) == list:
            # if the items were specifies in a "- name:" fasion, it gets in a list, so spit through those lists...
            for item in self.content:
                for key in item.keys():
                    if key == name:
                        return item[key]
            return None # if not found
        else: # type(self.content) == dict:
            # just look through the dict's keys
            for key in self.content.keys():
                if key == name:
                    return self.content[key]

            return None # if not found
    
    def Find(self,name): # returns empty dict if none found
        result = self.FindStrict(name)

        if result is None:
            return {}
        else:
            return result

    def FindOrCreate(self,name):
        result = self.FindStrict(name)
        if not result is None:
            return result
        else:
            if type(self.content) == list:
                dict = {} # createa new dict to put into the list
                dict[name] = {} # make a new dictionary object, that will be the new item
                
                self.content.append(dict) # append new dict containing item to the list
                return dict[name] # and return the new item
            else: # type(self.content) == dict:
                self.content[name] = {} # create new dict object as item
                return self.content[name] # return this item

    def GetRootScript(self):
        return self.content

    ## Static functions - used to obtain the blender text, and store it to the blender text,
    def _StoreToBlender():
        print "Storing AlcScript to Blender"
        if not AlcScript.objects is None:
            blendtext = alcFindBlenderText(AlcScript.ObjectTextFileName)
            blendtext.clear()
            alctext = AlcScript.objects.Write()
            blendtext.write(alctext)

        if not AlcScript.book is None:
            blendtext = alcFindBlenderText(AlcScript.BookTextFileName)
            blendtext.clear()
            alctext = AlcScript.book.Write()
            blendtext.write(alctext)
        

    def _LoadFromBlender():
        print "[AlcScript Parser]"

        if AlcScript.Debug:
            print " Contents of AlcScript:"
        blendtext = alcFindBlenderText(AlcScript.ObjectTextFileName)
        txt=""
        for line in blendtext.asLines():
            txt=txt + line + "\n"
        text = txt.expandtabs(4) # replace any tabs by 4 spaces, since yaml doesn't accept tabs, and blender tabs are 4 spaces
        AlcScript.objects = AlcScript(text)
        
        if AlcScript.objects is None:
            AlcScript.objects = AlcScript()

        if AlcScript.Debug:
            print " Contents of Book:"
        blendtext = alcFindBlenderText(AlcScript.BookTextFileName)
        txt=""
        for line in blendtext.asLines():
            txt=txt + line + "\n"
        text = txt.expandtabs(4) # replace any tabs by 4 spaces, since yaml doesn't accept tabs, and blender tabs are 4 spaces
        AlcScript.book = AlcScript(text)
        
        if AlcScript.book is None:
            AlcScript.book = AlcScript()
    
    def _Init():
        AlcScript.objects = AlcScript()
        AlcScript.book = AlcScript()
    
    ## Static shortcut functions for workign with the default blender text
    def _FindItem(name):
        if not AlcScript.current is None:
            object = AlcScript.objects.Find(name)
            return object
        else:
            return None

    def _FindOrCreateItem(name):
        if not AlcScript.current is None:
            object = AlcScript.objects.FindOrCreate(name)
            return object
        else:
            return None
      
 
    ## Yeah, python quirk of declaring static functions
    StoreToBlender = staticmethod(_StoreToBlender)
    LoadFromBlender = staticmethod(_LoadFromBlender)
    Init = staticmethod(_Init)
    FindItem = staticmethod(_FindItem)
    FindOrCreateItem = staticmethod(_FindOrCreateItem)

# A function to find subkeys in a recursive dictionary, or return a default value ('None' if not specified)
def FindInDict(dct,params,default=None):
    if type(params) == list or type(params) == tuple:
        pass
    elif type(params) == type(''):
        params = params.split(".")
    else:
        raise ValueError, "FindInDict: 'params' is not a list, tuple or string"

    if not type(dct) == dict:
        raise ValueError, "FindInDict: 'dct' is not a dictionary object"

    
    value = dct
    try:
        for i in range(len(params)):
            value = value[params[i]]
        
        if not value is None:
            return value
        else:
            return default
    except:
        return default

def StoreInDict(dct,params,value):
    if type(params) == list or type(params) == tuple:
        pass
    elif type(params) == type(''):
        params = params.split(".")
    else:
        try:
            params = str(params).split(".")
        except:
            raise ValueError, "StoreInDict: 'params' is not a list, tuple or string"
    
    if not type(dct) == dict:
        raise ValueError, "StoreInDict: 'dct' is not a dictionary object"
    
    mydict = dct

    for i in range(len(params)):
        if i == len(params) - 1:
            if type(mydict) == dict:
                mydict[params[i]] = value
            else:
                print "StoreInDict Not a Dictionary"
        else:
            if type(mydict) == dict:
                if mydict.has_key(params[i]):
                    if type(mydict[params[i]]) != dict:
                        mydict[params[i]] = {}
                else:
                        mydict[params[i]] = {}
                mydict = mydict[params[i]]
            else:
                print "StoreInDict Error: Not a Dictionary"

# Some Debugging tools for AlcScript:
if False:
    script = AlcScript("""
---
arguments:
  - type: sceneobjectlist
    objects:
      - obj1
      - obj2
  - type: float
    value: 0.1
  - type: string
    value: "testing"
    
    """)

    print "Contents of test1:"
    print script.Find("test1")
    
    print "Result of rewrite:"
    print script.Write()

   
    lst = list(FindInDict(script.GetRootScript(),"arguments",[]))
    print lst
    
    for i in range(len(lst)):
        print "---\nItem nr",i
        print lst[i]
    
    print "----------------------"
    
    i = 0
    for itm in lst:
        print "---\nItem nr",i
        print itm
        i += 1

    print "\n----------------------\n"

    
