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

import struct,StringIO,cStringIO,time
import Image,ImageFilter
from prp_HexDump import *

class tColor:
    def __init__(self,r=0,g=0,b=0):
        self.r=r
        self.g=g
        self.b=b


class tImage:
    def __init__(self,w=0,h=0):
        self.w=w
        self.h=h
        self.data=None #RGBA image
        self.rawdata=cStringIO.StringIO() #compressed raw image
        self.alpha=tColor(255,0,255)
        self.hasalpha=0


    def read(self,buf):
        self.rawdata.write(buf.read((self.w * self.h)*4))


    def write(self,buf):
        self.rawdata.seek(0)
        buf.write(self.rawdata.read())


    def show(self):
        self.toRGBA()
        self.applyAlpha()
        im = Image.new("RGBA",(self.w,self.h))
        self.data.seek(0)
        im.fromstring(self.data.read())
        im.show()

    def resize(self,w,h,blur=False):
        im = Image.new("RGBA",(self.w,self.h))
        self.data.seek(0)
        im.fromstring(self.data.read())
        im2=im.resize((w,h),Image.ANTIALIAS)

        if blur:
            im3 = im2.filter(ImageFilter.SMOOTH)
        else:
            im3 = im2
        self.data=cStringIO.StringIO()
        self.data.write(im3.tostring())
        #print self.data.tell(),w,h
        self.w=w
        self.h=h

    def resize_alphamult(self,w,h,alphamult=1.0,blur=False):
        im = Image.new("RGBA",(self.w,self.h))
        self.data.seek(0)
        im.fromstring(self.data.read())
        im2=im.resize((w,h),Image.ANTIALIAS)
        if blur and w > 2 and h > 2:
            # No point in blurring if there's only 2 pixels left :)
            # Besides that, it gives trouble if you do it with less than 2 pixels
            im3 = im2.filter(ImageFilter.BLUR)
        else:
            im3 = im2

        self.data=cStringIO.StringIO()
        self.data.write(im3.tostring())
        self.w=w
        self.h=h

        if not float(alphamult) == 1.0: # No point in doing this for alphamults of 1.0 exactly....
            self.alphamult(alphamult)


    def alphamult(self,value):
        # Multiplies the alpha value for all pixels in this image with the given value

        if float(value) < 0.0:
            value = 0.0

        aux=cStringIO.StringIO()
        self.data.seek(0)
        w = self.data.read(4)
        while w!="":                #RGBA
            r,g,b,a = struct.unpack("BBBB",w)

            a = float(a) * float(value)
                                  #RGBA
            if a > 255:
                a = 255

            aux.write(struct.pack("BBBB",r,g,b,a))
            w = self.data.read(4)
        self.data=aux

    def save(self,name):
        self.toRGBA()
        #self.fromRGBA()
        #self.toRGBA()
        if name[-4:]!=".png":
            self.applyAlpha()
        im = Image.new("RGBA",(self.w,self.h))
        #self.data.read()
        #print self.data.tell(), self.w, self.h, self.w*self.h*4
        self.data.seek(0)
        im.fromstring(self.data.read())
        im.save(name)


    def applyAlpha(self,bitbased=0):
        if not self.hasalpha:
            return
        aux=cStringIO.StringIO()
        self.data.seek(0)
        w = self.data.read(4)
        while w!="":                #RGBA
            r,g,b,a = struct.unpack("BBBB",w)
            if bitbased:
                if a<128:
                    r=self.alpha.r
                    g=self.alpha.g
                    b=self.alpha.b
                    a=0
                else:
                    a=255
            else:
                #alpha
                r=((r * a) / 255) + ((self.alpha.r * (255-a)) / 255)
                g=((g * a) / 255) + ((self.alpha.g * (255-a)) / 255)
                b=((b * a) / 255) + ((self.alpha.b * (255-a)) / 255)
                                  #RGBA
            aux.write(struct.pack("BBBB",r,g,b,a))
            w = self.data.read(4)
        self.data=aux


    def convert(self):
        self.data=cStringIO.StringIO()
        self.rawdata.seek(0)
        w = self.rawdata.read(4)
        while w!="":                #BGRA
            b,g,r,a = struct.unpack("BBBB",w)
                                        #RGBA
            self.data.write(struct.pack("BBBB",r,g,b,a))
            if a!=255:
                self.hasalpha=1
            w = self.rawdata.read(4)


    def iconvert(self):
        self.rawdata=cStringIO.StringIO()
        self.data.seek(0)
        w = self.data.read(4)
        while w!="":                #RGBA
            b,g,r,a = struct.unpack("BBBB",w)
                                           #BGRA
            self.rawdata.write(struct.pack("BBBB",r,g,b,a))
            w = self.data.read(4)


    def toRGBA(self):
        self.convert()


    def fromRGBA(self):
        self.iconvert()


    def set(self):
        self.fromRGBA()


class tDxtImage(tImage):
    def __init__(self,w,h,type):
        tImage.__init__(self,w,h)
        self.type=type
        if type==1:
            self.texel=8
        else:
            self.texel=16


    def read(self,buf):
        if self.w<=2 or self.h<=2:
            if self.w==0:
                self.w=1
            if self.h==0:
                self.h=1
            self.rawdata.write(buf.read((self.w*self.h)*4))
            return
        if (self.w % 4) or (self.h % 4):
            raise RuntimeError, "Invalid DXT size %ix%i"%(self.w,self.h)
        #size=((self.w*self.h)*self.texel)/16
        texels=(self.w*self.h)/self.texel
        size=(self.w*self.h)
        if self.type==1:
            size=size/2
        self.rawdata.write(buf.read(size))


    def toRGBA(self):
        if self.w<=2 or self.h<=2:
            self.convert()
            return
        self.rawdata.seek(0)
        y=0
        self.data=cStringIO.StringIO()
        #self.data.truncate(self.h * self.w * 4)
        #print "chicki",self.data.tell()
        for i in range((self.h * self.w)/4):
            self.data.write("                ")
        assert(self.data.tell()==(self.h * self.w)*4)
        self.data.seek(0)
        horn = (self.w)*4
        hell = (self.w-4)*4
        while y<self.h:
            x=0
            #print y,self.h,self.w, self.data.tell()
            #start=time.clock()
            while x<self.w:
                self.texel2rgba(self.rawdata,x,y,hell)
                x+=4
                if x<self.w:
                    self.data.seek(-3 * horn,1)
            #end = time.clock()
            #print "time %0.3f" % (end-start)
            y+=4
            #self.data.seek(3*horn,1)


    def fromRGBA(self):
        if self.w<=2 or self.h<=2:
            self.iconvert()
            return
        if (self.w % 4) or (self.h % 4):
            raise RuntimeError, "Invalid DXT size %ix%i"%(self.w,self.h)
        self.data.seek(0)
        self.rawdata=cStringIO.StringIO()
        horn = (self.w)*4
        hell = (self.w-4) * 4
        y=0
        while y<self.h:
            x=0
            while x<self.w:
                self.rgba2texel(self.data,hell)
                x+=4
                if x<self.w:
                    self.data.seek(-3 * horn,1)
            y+=4
            #self.data.seek(3*horn,1)


    def texel2rgba(self,texel,x,y,w):
        alpha=None
        if self.type!=1:
            alpha=self.getAlpha(texel)
            self.hasalpha=1
        u64, = struct.unpack("Q",texel.read(8))
        #print "<%X" %u64
        #a = 255
        c0 = u64 & 0xFFFF
        u64 = u64>>16
        c1 = u64 & 0xFFFF
        u64 = u64>>16
        b0 = (c0 & 0x1f) << 3
        g0 = ((c0>>5) & 0x3f) << 2
        r0 = ((c0>>11) & 0x1f) << 3
        b1 = (c1 & 0x1f) << 3
        g1 = ((c1>>5) & 0x3f) << 2
        r1 = ((c1>>11) & 0x1f) << 3
        #print b0,g0,r0,b1,g1,r1
        r=[]
        g=[]
        b=[]
        a=[]
        r.append(r0)
        r.append(r1)
        g.append(g0)
        g.append(g1)
        b.append(b0)
        b.append(b1)
        a.append(255)
        a.append(255)
        if self.type!=1 or c0>c1:
            max=2
        else:
            max=1
        for i in range(max):
            bi=(((max-i) * b0) + ((i+1)*b1))/(max+1)
            gi=(((max-i) * g0) + ((i+1)*g1))/(max+1)
            ri=(((max-i) * r0) + ((i+1)*r1))/(max+1)
            r.append(ri)
            g.append(gi)
            b.append(bi)
            a.append(255)
        if max==1:
            r.append(ri)
            g.append(gi)
            b.append(bi)
            a.append(0)
            self.hasalpha=1
        #mx=x
        #my=y
        for i in range(4):
            for e in range(4):
                test=u64 & 0x03
                u64 = u64>>2
                rf = r[test]
                gf = g[test]
                bf = b[test]
                if alpha==None:
                    af = a[test]
                else:
                    af = alpha[(i*4)+e]
                #print b,g,r                #RGBA
                self.data.write(struct.pack("BBBB",rf,gf,bf,af))
                #mx=mx+1
            if i!=3:
                self.data.seek(w,1)
            #my=my+1
            #mx=x


    def getAlpha(self,alpha):
        #alpha0, alpha1 = struct.unpack("BB",alpha.read(2))
        u64, = struct.unpack("Q",alpha.read(8))
        alpha0 = u64 & 0xFF
        u64 = u64>>8
        alpha1 = u64 & 0xFF
        u64 = u64>>8
        a=[]
        a.append(alpha0)
        a.append(alpha1)
        if alpha0 > alpha1:
            max=6
        else:
            max=4
        for i in range(max):
            ai=(((max-i) * alpha0) + ((i+1)*alpha1))/(max+1)
            a.append(ai)
        if max==4:
            a.append(0)
            a.append(255)
        result=[]
        for i in range(16):
            test=u64 & 0x07
            u64 = u64>>3
            res=a[test]
            result.append(res)
        return result


    def rgba2texel(self,input,w):
        r=[]
        g=[]
        b=[]
        a=[]
        alpha=0
        for i in range(4):
            for e in range(4):
                #print input.tell(),self.w,self.h,w
                ri,gi,bi,ai = struct.unpack("BBBB",input.read(4))
                r.append(ri)
                g.append(gi)
                b.append(bi)
                a.append(ai)
                if self.type!=1 or (alpha==0 and ai<128):
                    self.hasalpha=1
                    alpha=1
            if i!=3:
                input.seek(w,1)
        if self.type!=1:
            self.writeAlpha(a)
            #self.type=1
        maxi=0
        for i in range(16):
            for e in range(16):
                d=self.distance(r[i],r[e],g[i],g[e],b[i],b[e])
                if d>=maxi:
                    maxi=d
                    r0=r[i]
                    r1=r[e]
                    g0=g[i]
                    g1=g[e]
                    b0=b[i]
                    b1=b[e]
        c0 = r0>>3
        c0 = c0<<6
        c0 |= g0>>2
        c0 = c0<<5
        c0 |= b0>>3
        c1 = r1>>3
        c1 = c1<<6
        c1 |= g1>>2
        c1 = c1<<5
        c1 |= b1>>3
        #print b0,g0,r0,b1,g1,r1
        #check
        if c0==c1:
            if c0==0x00:
                c1=0xFF
                r1=0xFF
                g1=0xFF
                b1=0xFF
            else:
                c1=0x00
                r1=0x00
                g1=0x00
                b1=0x00
        rt=[]
        gt=[]
        bt=[]
        if (not alpha) or self.type!=1:
            aa = max(c0,c1)
            bb = min(c0,c1)
            maxi=2
        else:
            aa = min(c0,c1)
            bb = max(c0,c1)
            maxi=1
        if aa==c0:
            rt.append(r0)
            rt.append(r1)
            gt.append(g0)
            gt.append(g1)
            bt.append(b0)
            bt.append(b1)
        else:
            rt.append(r1)
            rt.append(r0)
            gt.append(g1)
            gt.append(g0)
            bt.append(b1)
            bt.append(b0)
        c0 = 0L
        c1 = 0L
        c0 |= aa
        c1 |= bb
        #assert(c0>c1)
        u64 = 0L
        u64 |= c0
        #print "%X" %u64
        #u64 = u64 << 16
        u64 |= c1<<16
        #print "%X" %u64
        #u64 = u64 << 2
        #print "%X" %u64
        #print ">%X %X %X" %(u64,c0,c1)
        for i in range(maxi):
            bi=(((maxi-i) * bt[0]) + ((i+1)*bt[1]))/(maxi+1)
            gi=(((maxi-i) * gt[0]) + ((i+1)*gt[1]))/(maxi+1)
            ri=(((maxi-i) * rt[0]) + ((i+1)*rt[1]))/(maxi+1)
            rt.append(ri)
            gt.append(gi)
            bt.append(bi)
        if maxi==1:
            rt.append(ri)
            gt.append(gi)
            bt.append(bi)
        for i in range(16):
            mini=255 ** 2 + 255 ** 2 + 255 ** 2
            if maxi==1 and a[i]<128:
                result=3L
            else:
                for e in range(maxi+1,-1,-1):
                    #print r[i],rt[e],g[i],gt[e],b[i]
                    d=self.distance(r[i],rt[e],g[i],gt[e],b[i],bt[e])
                    if d<=mini:
                        result=0L
                        result |=e
                        mini=d
            u64 |= result << ((2*i)+32)
            #if i!=15:
            #    u64 = u64 << 2
        #print ">%X" %u64
        self.rawdata.write(struct.pack("Q",u64))


    def distance(self,a1,a2,b1,b2,c1,c2):
        return pow(a1-a2,2) + pow(b1-b2,2) + pow(c1-c2,2)


    def writeAlpha(self,alpha):
        amin=255
        amax=0
        max=6
        for a in alpha:
            if a==0:
                max=4
            elif a<amin:
                amin=a
            if a==255:
                max=4
            elif a>amax:
                amax=a
        a0=0L
        a1=0L
        if max==6:
            a0 |=amax
            a1 |=amin
        else:
            a0 |=amin
            a1 |=amax
        u64 = 0L
        u64 |= a0
        #u64 = u64<<8
        u64 |= a1<<8
        #u64 = u64<<3
        if not a0>a1:
            max=4
        t=[]
        t.append(a0)
        t.append(a1)
        for i in range(max):
            ai=(((max-i) * a0) + ((i+1)*a1))/(max+1)
            t.append(ai)
        if max==4:
            t.append(0)
            t.append(255)
        w=0
        x=0
        for a in alpha:
            dis=255
            for e in range(7,-1,-1):
                if abs(a-t[e])<=dis:
                    dis=abs(a-t[e])
                    w=0L
                    w|=e
            x=x+1
            u64 |= w << ((3*(x-1))+16)
            #if x!=16:
            #    u64 = u64<<3
        self.rawdata.write(struct.pack("Q",u64))


class tJpgImage(tImage):
    def __init__(self,w,h,type=1):
        tImage.__init__(self,w,h)
        self.type=type
        self.extra=None
        self.jpg1size=0
        self.jpg2size=0
        # 0x00 - jpg1 RGB + jpg2 R=Alpha
        # 0x01 - RLE RGB  + jpg2 R=Alpha
        # 0x02 - jpg1 RGB + RLE alpha 0x00FF0000
        # 0x03 - RLE RGB  + RLE alpha 0x00FF0000


    def read(self,buf):
        self.type, = struct.unpack("B",buf.read(1))
        self.rawdata=cStringIO.StringIO()
        self.rawdata.write(struct.pack("B",self.type))
        if self.type not in [0x00,0x01,0x02,0x03]:
            raise "type is %02X" %(self.type)
        #The image
        if self.type & 0x01: #RLE 1
            count=1
            while count:
                count,color = struct.unpack("II",buf.read(8))
                self.rawdata.write(struct.pack("II",count,color))
        else: #JPG 1
            self.jpg1size, = struct.unpack("I",buf.read(4))
            self.rawdata.write(struct.pack("I",self.jpg1size))
            self.rawdata.write(buf.read(self.jpg1size))
        #The alpha channel encoded in the red channel
        if self.type & 0x02: #RLE 2
            count=1
            while count:
                count,color = struct.unpack("II",buf.read(8))
                self.rawdata.write(struct.pack("II",count,color))
        else: #JPG 1
            self.jpg2size, = struct.unpack("I",buf.read(4))
            self.rawdata.write(struct.pack("I",self.jpg2size))
            self.rawdata.write(buf.read(self.jpg2size))


    def toRGBA(self):
        self.rawdata.seek(0)
        self.data=cStringIO.StringIO()
        aux=cStringIO.StringIO()
        self.type, = struct.unpack("B",self.rawdata.read(1))
        #Note: It does not make much sense to store images with flags 0x03,
        #that one of the reasons of the little amount of found examples.
        if self.type & 0x01: #RLE
            count=1
            tcount=0
            while count:
                count, = struct.unpack("I",self.rawdata.read(4))
                tcount=tcount + count
                b,g,r,a = struct.unpack("BBBB",self.rawdata.read(4))
                for i in range(count):
                    aux.write(struct.pack("BBB",r,g,b))
            assert(tcount==self.w * self.h)
        else: #JPG
            self.jpg1size, = struct.unpack("I",self.rawdata.read(4))
            jpg1=cStringIO.StringIO()
            jpg1.write(self.rawdata.read(self.jpg1size))
            jpg1.seek(0)
            me=Image.open(jpg1)
            #me.show()
            aux.write(me.tostring())
            del jpg1
            del me
        aux.seek(0)
        self.hasalpha=0
        if self.type & 0x02: #RLE
            count=1
            tcount=0
            while count:
                count, = struct.unpack("I",self.rawdata.read(4))
                tcount=tcount + count
                b,g,r,a = struct.unpack("BBBB",self.rawdata.read(4))
                assert(a==0)
                assert(b==0)
                assert(g==0)
                if r!=255:
                    self.hasalpha=1
                for i in range(count):
                    rx,gx,bx = struct.unpack("BBB",aux.read(3))
                    self.data.write(struct.pack("BBBB",rx,gx,bx,r))
            assert(tcount==self.w * self.h)
        else: #JPG
            self.jpg2size, = struct.unpack("I",self.rawdata.read(4))
            jpg2=cStringIO.StringIO()
            jpg2.write(self.rawdata.read(self.jpg2size))
            jpg2.seek(0)
            me=Image.open(jpg2)
            #me.show()
            alpha=cStringIO.StringIO()
            alpha.write(me.tostring())
            alpha.seek(0)
            del jpg2
            del me
            for i in range(self.w * self.h):
                rx,gx,bx = struct.unpack("BBB",aux.read(3))
                r,g,b = struct.unpack("BBB",alpha.read(3))
                self.data.write(struct.pack("BBBB",rx,gx,bx,r))
                if r!=255:
                    self.hasalpha=1


    def fromRGBA(self):
        self.rawdata=cStringIO.StringIO()
        self.data.seek(0)
        self.rawdata.write(struct.pack("B",self.type))
        if self.type not in [0x00,0x01,0x02,0x03]:
            raise "Unsupported type"
        #the image
        if self.type & 0x01: #RLE 1
            count=0
            ri=0
            gi=0
            bi=0
            first=0
            for i in range(self.w * self.h):
                r,g,b,a = struct.unpack("BBBB",self.data.read(4))
                if not first:
                    first=1
                    ri=r
                    gi=g
                    bi=b
                if ri==r and gi==g and bi==b:
                    count=count+1
                else:
                    self.rawdata.write(struct.pack("I",count))
                    self.rawdata.write(struct.pack("BBBB",bi,gi,ri,0))
                    count=1
                    ri=r
                    gi=g
                    bi=b
            if count:
                self.rawdata.write(struct.pack("I",count))
                self.rawdata.write(struct.pack("BBBB",bi,gi,ri,0))
            self.rawdata.write(struct.pack("II",0,0))
        else: #jpg 1
            jpg1=cStringIO.StringIO()
            me = Image.new("RGBA",(self.w,self.h))
            me.fromstring(self.data.read(self.w * self.h * 4))
            me.save(jpg1,"JPEG")
            del me
            jpg1.read()
            self.jpg1size = jpg1.tell()
            self.rawdata.write(struct.pack("I",self.jpg1size))
            jpg1.seek(0)
            self.rawdata.write(jpg1.read())
            del jpg1
        self.data.seek(0)
        #alpha channel
        if self.type & 0x02: #RLE 2
            count=0
            ai=0
            first=0
            for i in range(self.w * self.h):
                r,g,b,a = struct.unpack("BBBB",self.data.read(4))
                if not first:
                    first=1
                    ai=a
                if ai==a:
                    count=count+1
                else:
                    self.rawdata.write(struct.pack("I",count))
                    self.rawdata.write(struct.pack("BBBB",0,0,ai,0))
                    count=1
                    ai=a
            if count:
                self.rawdata.write(struct.pack("I",count))
                self.rawdata.write(struct.pack("BBBB",0,0,ai,0))
            self.rawdata.write(struct.pack("II",0,0))
        else: #jpg 2
            aux=cStringIO.StringIO()
            for i in range(self.w * self.h):
                r,g,b,a = struct.unpack("BBBB",self.data.read(4))
                aux.write(struct.pack("BBBB",a,0,0,255))
            aux.seek(0)
            jpg1=cStringIO.StringIO()
            me = Image.new("RGBA",(self.w,self.h))
            me.fromstring(aux.read(self.w * self.h * 4))
            me.save(jpg1,"JPEG")
            del me
            jpg1.read()
            self.jpg2size = jpg1.tell()
            self.rawdata.write(struct.pack("I",self.jpg2size))
            jpg1.seek(0)
            self.rawdata.write(jpg1.read())
            del jpg1
