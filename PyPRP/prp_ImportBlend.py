#!BPY
#
# Note: the original code of this script is in the Blender Python API documentation.
# I only performed a small modification to import everything.
# You can find the specific example at: http://www.blender.org/modules/documentation/236PythonDoc/Library-module.html

"""
Name: 'Import *.blend...'
Blender: 237
Group: 'Import'
Tooltip: 'Why blender does not natively support this?'
"""

import Blender
from Blender import Library

def f(name):
    open_library(name)


def open_library(name):
    Library.Open(name)
    groups = Library.LinkableGroups()
    for db in groups:
        print db
        for obname in Library.Datablocks(db):
            print obname
            Library.Load(obname,db,0)   
    Library.Update()
    Library.Close()
    Blender.Redraw()


Blender.Window.FileSelector(f,"Choose Library")
