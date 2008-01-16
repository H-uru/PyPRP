#
# $Id: alc_Wizards.py 876 2007-12-15 22:15:11Z Paradox $
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

# Help library

try:
    import Blender
    try:
        from Blender import NMesh, Object, Mathutils
    except Exception, detail:
        print detail
except ImportError:
    pass

import random, md5,math, binascii, struct

from alc_AlcScript import *
from alcspecialobjs import *
import alc_Functions
from alc_Functions import *
from alc_ObjClasses import plHKPhysical, plPhysical
from alc_LogicClasses import plAvLadderMod
from alc_CamClasses import plCameraBrain1_Circle

def Wizard_BookUpgrade(RemoveOld = False):
    age = { \
        "sequenceprefix" : 99, \
        "startdatetime" : 12, \
        "daylength" : 24.4, \
        "maxcapacity" : 152, \
        "lingertime" : 181, \
        }
    config = {}
    pages = {}
    
    oldbookobjects = []
    
    scene = Blender.Scene.GetCurrent()
    for obj in list(scene.objects):
        # if this object has a "book" property, ignore it
        try:
            p=obj.getProperty("book")
            print " Found Book on object %s"%(obj.name)
            # If we haven't crashed, we have a book type
            
            try:
                # Now extract the properties
                p = obj.getProperty('SequencePrefix')
                print p
                age["sequenceprefix"] = getStrIntPropertyOrDefault(obj,"SequencePrefix",100)
    
                p = obj.getProperty('StartDateTime')
                print p
                time = getTextPropertyOrDefault(obj,"StartDateTime",0)
    
                try:
                    age["startdatetime"] = int(time,10)
                except:
                    age["startdatetime"] = 0
                    
                p = obj.getProperty('DayLength')
                print p
                age["daylength"] = float(getTextPropertyOrDefault(obj,"DayLength",24.0))
                
                p = obj.getProperty('MaxCapacity')
                print p
                age["maxcapacity"] = getStrIntPropertyOrDefault(obj,"MaxCapacity",150)
    
                p = obj.getProperty('LingerTime')
                print p
                age["lingertime"] = getStrIntPropertyOrDefault(obj,"LingerTime",180)
                
                config["agesdlhook"] = bool(getBoolPropertyOrDefault(obj,"AgeSDLHook",False))
                
                oldbookobjects.append(obj)
            except (AttributeError, RuntimeError),details:
                print "Exception: ",details
        except (AttributeError, RuntimeError),detail:
            pass
        
        # if this object has a "page" property, ignore it too...
        try:
            p=obj.getProperty("page")
            print " Found Page on object %s"%(obj.name)
            
            # If we haven't crashed, we have a book type
            # Now extract the properties
            page = {}

            index = getIntPropertyOrDefault(obj,"page",0)

            page["name"] = getTextPropertyOrDefault(obj,"name","Room"+str(index))

            page["type"] = getIntPropertyOrDefault(obj,"type",0)

            page["hide"] = getIntPropertyOrDefault(obj,"hide",0)
            
            print "  Contents:",page
            # And store this page...
            if index != -1 and index != -2:
                pages[index] = page
            
            oldbookobjects.append(obj)
                
        except (AttributeError, RuntimeError),details:
            pass
    
    if len(pages) == 0:
        pages[0] = {"name": "mainRoom","type": 0,"hide":0}
    
    # Now we can write out the stuff
    text = ""
    
    # First do the age block
    text += "age:\n"
    for key in age.keys():
        text += "\t" + key +": " + str(age[key]) + "\n"
    text += "\n"
    
    # Next print the age.pages block
    text += "\tpages:\n"
    pagekeys = pages.keys()
    pagekeys.sort()
    for key in pagekeys:
        text += "\t\t- index: " + str(key) + "\n"
        text += "\t\t  name: " + pages[key]["name"] + "\n"
        if pages[key]["hide"] > 0:
            text += "\t\t  hide: true\n"
        if pages[key]["type"] > 0:
            text += "\t\t  flags:\n"
            for flag in alcBook.PageFlags.keys():
                if pages[key]["type"] & alcBook.PageFlags[flag]:
                    text += "\t\t\t- " + flag + "\n"
    text += "\n"

    # And finish with the config block
    if len(config.keys()) > 0:
        text += "config:\n"
        for key in config.keys():
            text += "\t" + key +": " + str(config[key]) + "\n"
    
    
    blendtxt=alcFindBlenderText("Book")
    blendtxt.clear()
    blendtxt.write(text)
    
    if RemoveOld:
        for obj in oldbookobjects:
            scene.objects.unlink(obj)
    

def Wizard_property_update():
    l = Blender.Object.Get()
    AlcScript.objects = AlcScript()
    numProps = 0
    numObjects = 0
    lights = {}
    litObjects = []
    for obj in l:
        oldNumProps = numProps
        try:
            p=obj.getProperty("name")
            numProps += 1
            name = str(p.getData())
            obj.removeProperty(p)
            obj.setName(name)
        except (AttributeError, RuntimeError):
            pass
        name = str(obj.name)
        print "Object:",name
        obj_type=obj.getType()
        try:
            p=obj.getProperty("alctype")
            print p
            numProps += 1
            type=str(p.getData())
            obj.removeProperty(p)
            obj.addProperty("type",type)
        except (AttributeError, RuntimeError):
            pass

        try:
            p=obj.getProperty("prpregion")
            print p
            numProps += 1
            type=str(p.getData())
            obj.removeProperty(p)
            
            if type == "climbregion":
                type = "climbing"
            elif type == "swimregion" or type == "swimrgn":
                type = "swimdetect"
            elif type == "swimplainsfc" or type == "swimscursfc" or type == "swimccursfc":
                type = "swim"
            elif type == "paniclnkrgn":
                type = "panic"
            elif type == "footsteprgn":
                type = "footstep"
            elif type == "camerargn":
                type = "camera"
            elif type == "clickregion":
                type = "logic"
            
            obj.addProperty("regiontype",type)
            
        except (AttributeError, RuntimeError):
            pass
                            
        pass

        # Check whether the object should have bounds
        try:
            p = obj.getProperty("col_type")
            print p
            numProps += 1
            col_type=int(p.getData())
            obj.removeProperty(p)
        except (AttributeError, RuntimeError):
            col_type=-1
        if col_type != -1:
            # Flag the object as having a rigid body
            obj.rbFlags |= Blender.Object.RBFlags["BOUNDS"]
            if col_type == 1: # Bounding Box
                obj.rbShapeBoundType = plHKPhysical.HullTypes["BOX"]
            elif col_type == 2: # Bounding Sphere
                obj.rbShapeBoundType = plHKPhysical.HullTypes["SPHERE"]
            elif col_type == 3: # Convex Hull
                obj.rbShapeBoundType = plHKPhysical.HullTypes["CONVEXHULL"]
            elif col_type == 4 or col_type == 5:
                obj.rbShapeBoundType = plHKPhysical.HullTypes["TRIANGLEMESH"]

        # Check whether the object should be dynamic
        try:
            p = obj.getProperty("mass")
            print p
            numProps += 1
            mass=float(p.getData())
            obj.removeProperty(p)
        except (AttributeError, RuntimeError):
            mass=-1
        if (mass > 0):
            # Set the actor flag and the dynamic flag
            # Note: old files didn't have a way to indicate actors that were not kickable
            obj.rbFlags |= Blender.Object.RBFlags["ACTOR"]
            obj.rbFlags |= Blender.Object.RBFlags["DYNAMIC"]
            # Set the mass
            obj.rbMass = mass

        # Translate col_flags0 values
        try:
            p = obj.getProperty("col_flags0")
            print p
            numProps += 1
            col_flags0=alcAscii2Hex(str(p.getData()),2)
            obj.removeProperty(p)
        except (AttributeError, RuntimeError):
            col_flags0=0
        if (col_flags0 > 0):
            if (col_flags0 == plHKPhysical.Collision["cStorePosition"]):
                value = "storepos"
            elif (col_flags0 == plHKPhysical.Collision["cResetPosition"]):
                value = "resetpos"
            elif (col_flags0 == plHKPhysical.Collision["cDetector"]):
                value = "detect"
            obj.addProperty("physlogic",value)

        # Translate col_flags1 values 
        # (just delete the property; this is automatically set by other code)
        try:
            p = obj.getProperty("col_flags1")
            print p
            numProps += 1
            obj.removeProperty(p)
        except (AttributeError, RuntimeError):
            pass

        # Translate col_flags2 values
        # (just delete the property; this is automatically set by other code)
        try:
            p = obj.getProperty("col_flags2")
            print p
            numProps += 1
            obj.removeProperty(p)
        except (AttributeError, RuntimeError):
            pass

        # Translate col_flags3 values
        # (just delete the property; this is replaced by two bool flags that are always false)
        try:
            p = obj.getProperty("col_flags3")
            print p
            numProps += 1
            obj.removeProperty(p)
        except (AttributeError, RuntimeError):
            pass

        # Translate col_flags4 values
        try:
            p = obj.getProperty("col_flags4")
            print p
            numProps += 1
            col_flags4=alcAscii2Hex(str(p.getData()),4)
            obj.removeProperty(p)
        except (AttributeError, RuntimeError):
            col_flags4=0
        if (col_flags4 & 0x4 > 0):
            # Pin this object
            objscript = AlcScript.objects.FindOrCreate(obj.name)
            StoreInDict(objscript,"physical.pinned","true")
            
        # Translate col_flags5 values
        try:
            p = obj.getProperty("col_flags5")
            print p
            numProps += 1
            col_flags5=alcAscii2Hex(str(p.getData()),4)
            obj.removeProperty(p)
            bHasColFlags5 = True
        except (AttributeError, RuntimeError):
            col_flags5=0
            bHasColFlags5 = False
        if bHasColFlags5 and (col_flags5 & plPhysical.plLOSDB["kLOSDBCameraBlockers"] == 0):
            # User has explicitly disabled camera blocking
            # (Since new plugin enables camera blocking by default, 
            # just convert explicit disabling)
            objscript = AlcScript.objects.FindOrCreate(obj.name)
            StoreInDict(objscript,"physical.campassthrough","true")
        if (col_flags5 & plPhysical.plLOSDB["kLOSDBAvatarWalkable"] > 0):
            # Delete the friction property, if it exists
            try:
                p = obj.getProperty("rc")
                obj.removeProperty(p)
            except (AttributeError, RuntimeError):
                pass

        # Convert ladders        
        try:
            p = obj.getProperty("regiontype")
            regiontype = str(p.getData())
        except (AttributeError, RuntimeError):
            regiontype = None
        if regiontype == "climbing":
            # Determine whether it is a bottom or top region
            try:
                p=obj.getProperty("bottomFlag")
                print p
                numProps += 1
                bottomFlag=alcAscii2Hex(str(p.getData()),1)
                obj.removeProperty(p)
            except (AttributeError, RuntimeError):
                bottomFlag = True
            try:
                p=obj.getProperty("climbOffset")
                print p
                numProps += 1
                type=int(p.getData())
                obj.removeProperty(p)
            except (AttributeError, RuntimeError):
                type=0
            # Get the number of loops
            try:
                p=obj.getProperty("climbHeight")
                print p
                numProps += 1
                climbHeight=int(p.getData())
                obj.removeProperty(p)
            except (AttributeError, RuntimeError):
                climbHeight=1                
            # Write the script values
            objscript = AlcScript.objects.FindOrCreate(obj.name)
        
            if type == plAvLadderMod.fTypeField["kBig"]:
                StoreInDict(objscript,"region.ladder.style","big")
            elif type == plAvLadderMod.fTypeField["kFourFeet"]:
                StoreInDict(objscript,"region.ladder.style","fourfeet")
            elif type == plAvLadderMod.fTypeField["kTwoFeet"]:
                StoreInDict(objscript,"region.ladder.style","twofeet")
            else:
                StoreInDict(objscript,"region.ladder.style","big")

            StoreInDict(objscript,"region.ladder.loops",climbHeight)

            if bottomFlag:
                StoreInDict(objscript,"region.ladder.direction","up")
            else:
                StoreInDict(objscript,"region.ladder.direction","down")

        # Check for camera regions
        elif regiontype == "camera":
            # Write the script values
            objscript = AlcScript.objects.FindOrCreate(obj.name)
            StoreInDict(objscript,"region.type","camera")
            msgscripts = []
            msgscript = {}
            try:
                p = obj.getProperty("camera")
                cameraName = str(p.getData())
                print p
                numProps += 1
                obj.removeProperty(p)
            except (AttributeError, RuntimeError):
                cameraName = None
            if cameraName != None:
                StoreInDict(msgscript,"newcam",cameraName)
            # Write the script values
            objscript = AlcScript.objects.FindOrCreate(obj.name)
            try:
                p = obj.getProperty("setDefCam")
                setDefCam = bool(str(p.getData()).lower() == "true")
                print p
                numProps += 1
                obj.removeProperty(p)
            except (AttributeError, RuntimeError):
                setDefCam = False
            if setDefCam:
                # Setting this seems to disable the region
                # StoreInDict(msgscript,"cmds",["setasprimary",])
                pass
            msgscripts.append(msgscript)
            StoreInDict(objscript,"region.camera.messages",msgscripts)

        # Check for cameras
        if obj_type == 'Camera':
            # Write the script values
            objscript = AlcScript.objects.FindOrCreate(obj.name)
            try:
                p = obj.getProperty("cambrain")
                cambrain = str(p.getData())
                print p
                numProps += 1
                obj.removeProperty(p)
            except (AttributeError, RuntimeError):
                cambrain = "fixed"
            StoreInDict(objscript,"camera.brain.type",cambrain)
            try:
                p = obj.getProperty("POA_X")
                POA_X = float(p.getData())
                print p
                numProps += 1
                obj.removeProperty(p)
            except (AttributeError, RuntimeError):
                POA_X = None
            try:
                p = obj.getProperty("POA_Y")
                POA_Y = float(p.getData())
                print p
                numProps += 1
                obj.removeProperty(p)
            except (AttributeError, RuntimeError):
                POA_Y = None
            try:
                p = obj.getProperty("POA_Z")
                POA_Z = float(p.getData())
                print p
                numProps += 1
                obj.removeProperty(p)
            except (AttributeError, RuntimeError):
                POA_Z = None
            if POA_X != None and POA_Y != None and POA_Z != None:
                StoreInDict(objscript,"camera.brain.poa","%f,%f,%f"%(POA_X,POA_Y,POA_Z))
            try:
                p = obj.getProperty("Circle_flags")
                Circle_flags = int(p.getData())
                print p
                numProps += 1
                obj.removeProperty(p)
            except (AttributeError, RuntimeError):
                Circle_flags = None
            if Circle_flags != None:
                flaglist = []
                for flag in plCameraBrain1_Circle.ScriptCircleFlags.keys():
                    if Circle_flags & plCameraBrain1_Circle.ScriptCircleFlags[flag] > 0:
                        flaglist.append(flag)
                StoreInDict(objscript,"camera.brain.circleflags",flaglist)
            try:
                p = obj.getProperty("AvCam_X")
                AvCam_X = float(p.getData())
                print p
                numProps += 1
                obj.removeProperty(p)
            except (AttributeError, RuntimeError):
                AvCam_X = None
            try:
                p = obj.getProperty("AvCam_Y")
                AvCam_Y = float(p.getData())
                print p
                numProps += 1
                obj.removeProperty(p)
            except (AttributeError, RuntimeError):
                AvCam_Y = None
            try:
                p = obj.getProperty("AvCam_Z")
                AvCam_Z = float(p.getData())
                print p
                numProps += 1
                obj.removeProperty(p)
            except (AttributeError, RuntimeError):
                AvCam_Z = None
            if AvCam_X != None and AvCam_Y != None and AvCam_Z != None:
                StoreInDict(objscript,"camera.brain.offset","%f,%f,%f"%(AvCam_X,AvCam_Y,AvCam_Z))
            # Just delete the FpCam_* properties - they are not used
            try:
                p = obj.getProperty("FpCam_X")
                print p
                numProps += 1
                obj.removeProperty(p)
            except (AttributeError, RuntimeError):
                pass
            try:
                p = obj.getProperty("FpCam_Y")
                print p
                numProps += 1
                obj.removeProperty(p)
            except (AttributeError, RuntimeError):
                pass
            try:
                p = obj.getProperty("FpCam_Z")
                print p
                numProps += 1
                obj.removeProperty(p)
            except (AttributeError, RuntimeError):
                pass

        # Check for lamps and lit objects
        elif obj_type == 'Lamp':
            lights[obj.name] = obj
            # The export code doubles the energy and multiplies it against
            # the diffuse and ambient lights.  To preserve the light's current
            # settings, set energy to 0.5
            lamp = obj.data
            lamp.energy = 0.5
            if lamp.type == Blender.Lamp.Types["Spot"] or lamp.type == Blender.Lamp.Types["Lamp"]:
                # To keep the effects of quadratic attenuation the same,
                # set the quad and sphere modes
                lamp.mode |= Blender.Lamp.Modes["Quad"]
                lamp.mode |= Blender.Lamp.Modes["Sphere"]
                # The exporter now divides quad1 and quad2 by the distance,
                # so multiply them by the distance
                lamp.quad1 = lamp.quad1 * lamp.dist
                lamp.quad2 = lamp.quad2 * lamp.dist
                # The exporter now divides the distance by 16
                lamp.dist = lamp.dist * 16
        elif obj_type == 'Mesh':
            mesh = Blender.Mesh.Get(obj.data.name)
            lightName = None
            try:
                p=obj.getProperty("lights000")
                lightName=str(p.getData())
                print p
                numProps += 1
            except (AttributeError, RuntimeError):
                pass
            if len(mesh.materials) > 0:
                if lightName == None:
                    # Set this object's materials to SHADELESS mode    
                    mat = mesh.materials[0]
                    mat.mode |= Blender.Material.Modes["SHADELESS"]     
                else:
                    # Add this mesh to the list (for further processing)
                    litObjects.append(obj)
           
        if (oldNumProps != numProps):
            numObjects += 1

    # Loop through lit meshes, now that we know how many lights there are
    for obj in litObjects:
        lightNames = []
        # Determine which lights affect this object
        for lint in range(1000):
            cstrl="lights%03i" %lint
            lightName=None
            try:
                p=obj.getProperty(cstrl)
                lightName=str(p.getData())
                obj.removeProperty(p)
            except (AttributeError, RuntimeError):
                break
            if lightName != None:
               lightNames.append(lightName)
        # Decide if a light group is needed
        if len(lightNames) < len(lights):
            # Create the light group
            print "Creating light group for object",obj.name
            mesh = Blender.Mesh.Get(obj.data.name)
            mat = mesh.materials[0]
            lightGroup = Blender.Group.New(str(mat.name))
            for lightName in lightNames:
                lightObj = lights[lightName]
                if (lightObj != None):
                    print "  Adding light",lightName,"to group"
                    lightGroup.objects.link(lightObj)
            # Assign the group to the material
            mat.lightGroup = lightGroup
            mat.mode |= Blender.Material.Modes["GROUP_EXCLUSIVE"]

    if len(AlcScript.objects.content) > 0:
        # Write out the alcscript to a text object, then delete the script
        blendtext = alcFindBlenderText(AlcScript.ObjectTextFileName)
        blendtext.clear()
        alctext = AlcScript.objects.Write()
        blendtext.write(alctext)
        AlcScript.objects = None

    Blender.Draw.PupMenu('Converted %d properties for %d objects.' % (numProps,numObjects))



def Wizard_mattex_create():
    l = Blender.Object.Get()
    numMatCreated = 0
    numTexCreated = 0
    for obj in l:
        if obj.type == 'Mesh':
            mesh = Blender.Mesh.Get(obj.data.name)
            try:
                p = obj.getProperty("type")
                type=str(p.getData())
            except (AttributeError, RuntimeError):
                try:
                    p = obj.getProperty("alctype")
                    type=str(p.getData())
                except (AttributeError, RuntimeError):
                    type=None
            try:
                p=obj.getProperty("book")
                type = "book"
            except (AttributeError, RuntimeError):
                pass             
            try:
                p=obj.getProperty("page")
                type = "page"
            except (AttributeError, RuntimeError):
                pass             

            # Check for existence of materials for the mesh
            mat = None
            if len(mesh.materials)>0:
                mat = mesh.materials[0]
            elif type != "region" and type != "svconvex" and type != "collider" and type != "book" and type != "page":
                # Create a material
                matName = alcUniqueName(obj.name,0,0,"m");
                mat = Blender.Material.New(matName)
                matmode = mat.getMode()
                mat.setMode(matmode)
                numMatCreated += 1
                mesh.materials = [mat,]
                obj.colbits = 0x01
                obj.activeMaterial = 1
                #DEBUG
                print "Created material",matName,"for object",obj.getName()
            else:
                continue
            # Check for existence of UV coordinates on the face
            if (mat != None) and (len(mesh.faces) > 0):
                # Set specular to black (otherwise all lit stuff will be shiny)
                mat.setSpecCol([0,0,0])
                if (mesh.faceUV):
                    # Check for existence of textures
                    numTextures = 0
                    for tex in mat.getTextures():
                        if (tex != None):
                            numTextures += 1
                            if tex.texco == Blender.Texture.TexCo["ORCO"]:
                                # Use UV coordinates
                                tex.texco = Blender.Texture.TexCo["UV"]
                    if (numTextures == 0):
                        # Create a texture based on the image associated with the faces
                        face = mesh.faces[0]
                        try:
                            newTex = Blender.Texture.Get(face.image.getName())
                        except Exception:
                            newTex = None
                        if (newTex == None):
                            newTex = Blender.Texture.New(face.image.getName())
                            newTex.setType('Image')
                            newTex.setImage(face.image)
                        mat.setTexture(0,newTex,Blender.Texture.TexCo.UV,Blender.Texture.MapTo.COL)
                        numTexCreated += 1
                        #DEBUG
                        print "Created texture",newTex.getName(),"for object",obj.getName()

    Blender.Draw.PupMenu('Added %d materials and %d textures.' % (numMatCreated,numTexCreated))


