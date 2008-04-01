#
# $Id: alcConvexHull.py 659 2006-10-01 14:35:11Z trylon $
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

import copy
from alc_GeomClasses import *

class alcConvexHull:
    def __init__(self,vertexs):
        self.vertexs=[]
        self.faces=[]
        overts=vertexs
        #print vertexs
        for v in vertexs:
            self.vertexs.append(Vertex(v[0],v[1],v[2]))
        vertexs=self.vertexs
        self.vertexs=[]
        #remove dups
        if(len(self.vertexs) > 4000): # only print this out if it is indeed a high vertexcount
            print "Computing a ConvexHull of %i vertices, processing can take some time..." %len(vertexs)
            print ""
        for v in vertexs:
            dup=0
            for j in vertexs:
                if v.isequal(j):
                    dup=dup+1
                    if dup>1:
                        break
            if dup==1:
                self.vertexs.append(v)
        vertexs=self.vertexs
        if len(vertexs)<3:
            raise "Not enough vertexs"
        elif len(vertexs)==3:
            face=[0,1,2]
            self.faces.append(face)
            self.vertexs=overts
            return
        ## compute the convex hull of a set of vertexs
        v1 = vertexs[0]
        v2 = vertexs[1]
        #collinear verts
        co=[]
        for i in range(2,len(vertexs)):
            idx=i
            v3=vertexs[idx]
            if self.collinear(v1,v2,v3):
                co.append(idx)
            else:
                face=[0,1,idx]
                break
        idx=idx+1
        for i in range(idx,len(vertexs)):
            idx=i
            v4=vertexs[idx]
            vol=self.volumeSign(face,v4)
            if vol==0:
                co.append(idx)
            else:
                self.toTetra(face,idx,vol)
                break
        idx=idx+1
        for i in range(idx,len(vertexs)):
            idx=i
            self.addVertex(idx)
        for i in co:
            self.addVertex(i)
        ##make simple vertexs
        vertexs=self.vertexs
        self.vertexs=[]
        for v in vertexs:
            vi=[v.x,v.y,v.z]
            self.vertexs.append(vi)


    def clean(self):
        #remove unused vertexs
        used=0
        for i in range(len(self.vertexs)):
            if i>=len(self.vertexs):
                break
            for f in self.faces:
                if f[0]==i or f[1]==i or f[2]==i:
                    used=1
            if not used:
                #print i
                v=self.vertexs[i]
                self.vertexs.remove(v)
                for f in self.faces:
                    for j in range(3):
                        if f[j]>i:
                            f[j]=f[j]-1
            used=0


    def addVertex(self,idx):
        edges=[]
        #print self.faces
        #print "edges", edges
        #print "add vertex", idx
        v=self.vertexs[idx]
        remove=[]
        #delete visible faces
        for face in self.faces:
            if self.volumeSign(face,v)<0:
                #print v, "visible from", face
                a=[face[0],face[1]]
                b=[face[1],face[2]]
                c=[face[2],face[0]]
                self.updateEdges(edges,a)
                self.updateEdges(edges,b)
                self.updateEdges(edges,c)
                #print "removing face", face
                #self.faces.remove(face)
                remove.append(face)
                #print self.faces
            #else:
                #print v, "NOT visible from", face
        for f in remove:
            self.faces.remove(f)
        #print "edges", edges
        for e in edges:
            a=[e[0],e[1],idx]
            self.faces.append(a)
            #print "adding face", a


    def updateEdges(self,edges,edge):
        for e in edges:
            if (e[0]==edge[0] and e[1]==edge[1]) or (e[0]==edge[1] and e[1]==edge[0]):
                #print "removing edge", e
                edges.remove(e)
                return
        #print "adding edge", edge
        edges.append(edge)


    def toTetra(self,face,idx,vol):
        self.faces.append(face)
        if vol<0:
            tmp=face[0]
            face[0]=face[2]
            face[2]=tmp
        a=[face[2],face[1],idx]
        b=[face[1],face[0],idx]
        c=[face[0],face[2],idx]
        self.faces.append(a)
        self.faces.append(b)
        self.faces.append(c)


    def collinear(self,v1,v2,v3):
        return ((v3.x-v1.x) * (v2.z-v1.z) - (v2.x - v1.x) * (v3.z - v1.z) == 0 \
            and (v3.y-v1.y) * (v2.x-v1.x) - (v2.y - v1.y) * (v3.x - v1.x) == 0 \
            and (v3.z-v1.z) * (v2.y-v1.y) - (v2.z - v1.z) * (v3.y - v1.y) == 0)


    def volumeSign(self,face,vert):
        v1=self.vertexs[face[0]]
        v2=self.vertexs[face[1]]
        v3=self.vertexs[face[2]]
        v4=vert
        ax=v1.x - v4.x
        ay=v1.y - v4.y
        az=v1.z - v4.z
        bx=v2.x - v4.x
        by=v2.y - v4.y
        bz=v2.z - v4.z
        cx=v3.x - v4.x
        cy=v3.y - v4.y
        cz=v3.z - v4.z
        vol= ax * (by * cz - bz * cy) + ay *(bz * cx - bx * cz) + az * (bx * cy - by * cx)
        if vol>0:
            return 1
        elif vol<0:
            return -1
        else:
            return 0


##verts=[[0.0,0.0,0.0],[10.0,0.0,0.0],[5.0,5.0,5.0],[0.0,10.0,0.0],[0.0,0.0,10.0],[20.0,20.0,20.0],[15.0,15.0,15.0]]
##
##a=alcConvexHull(verts)
##print a.faces
##print a.vertexs
##a.clean()
##print a.faces
##print a.vertexs


