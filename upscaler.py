from PIL import Image
from collections import defaultdict
from os.path import exists
import os
import random
#acc is used as the look radius (higher is more noisy)
acc = 2

def getImage(path,max):
    global sumw, sumh, ic
    img = Image.open(path,'r')
    img = img.convert('RGBA')
    img.thumbnail((max,max))
    return img
def surround(x,y,r,maxX,maxY):
    sur = []
    for w in range(-r+1,r):
        for h in range(-r+1,r):
            cw,ch = x+w,y+h
            if (cw >= 0 and ch >= 0 and cw < maxX and ch < maxY):
                sur.append((cw,ch))
    return sur

def posToRGB(img,arr):
    px = img.load()
    tmp = []
    for x,y in arr:
        val = px[x,y]
        tmp.append(val)
    return tmp

def genGrabBag(img):
    print('looking at art...')
    px = img.load()
    grabBag = defaultdict(lambda: [])
    for h in range(img.height):
        for w in range(img.width):
            sur = surround(w,h,acc,img.width,img.height)
            sur = posToRGB(img,sur)
            for rgb in sur:
                grabBag[rgb].append(px[w,h])
    return grabBag

def copyFrame(img1,img2,offset):
    px1 = img1.load()
    px2 = img2.load()
    pw = [offset,img2.width-1-offset]
    ph = [offset,img2.height-1-offset]
    for w in pw:
        for h in range(offset,img2.height-offset):
            px2[w,h] = px1[w,h]
    for h in ph:
        for w in range(offset,img2.width-offset):
            px2[w,h] = px1[w,h]
    return img2

def dream(out,grabBag):
    print('dreaming... zzz...')
    ox = out.load()
    for w in range(out.width):
        for h in range(out.height):
            if ox[w,h] != (0,0,0,0): continue
            sur = surround(w,h,acc,out.width,out.height)
            sur = posToRGB(out,sur)
            random.shuffle(sur)
            c = 0
            choices = []
            while len(choices)<1 and c < len(sur):
                choices = grabBag[sur[c]]
                if (len(choices)>0):
                    ox[w,h] = random.choice(choices)
                c += 1
    return out

def avgPix(outImg):
    avgRow(outImg)
    avgColumn(outImg)
    return outImg

def avgColumn(outImg):
    ox = outImg.load()
    for w in range(outImg.width):
        for h in range(outImg.height):
            if (ox[w,h] != (0,0,0,0) or h%2==0): continue
            if (h+1 == outImg.height):
                avg = [ox[w,h-1]]
            else:
                avg = [ox[w,h-1], ox[w,h-1]]
            avg = tuple(int(sum(a) / len(a)) for a in zip(*avg))
            ox[w,h] = avg
    return outImg

def avgRow(outImg):
    ox = outImg.load()
    for h in range(outImg.height):
        for w in range(outImg.width):
            if (ox[w,h] != (0,0,0,0) or w%2==0): continue
            if (w+1 == outImg.width):
                avg = [ox[w-1,h]]
            else:
                avg = [ox[w-1,h], ox[w+1,h]]
            avg = tuple(int(sum(a) / len(a)) for a in zip(*avg))
            ox[w,h] = avg
    return outImg

def mapImage(old:Image,new:Image):
    pxold = old.load()
    pxnew = new.load()
    wi, hi = new.width/old.width,new.height/old.height
    wo = 0
    for w in range(old.width):
        ho = 0
        for h in range(old.height):
            pxnew[wo,ho] = pxold[w,h]
            ho += hi
        wo += wi
    return new

def main(path,scale,isDream):
    img = getImage(path,20000)
    gb = genGrabBag(img)
    output = Image.new(img.mode, (img.width*int(scale),img.height*int(scale)))
    output = mapImage(img,output)
    if isDream:
        output = dream(output,gb)
    else:
        output = avgPix(output)
    path = path[path.find('/'):]
    path = path[:-4] + "-upscaled.png"
    output.save('output/' + path)
    print('saved: ' + path)

if __name__ == '__main__':
    scale = float(input("Scale Multiplier (2 is max): "))
    isDream = input("Classic or Dream method?: ").lower().startswith('d')
    pictures = os.listdir('input')
    for pic in pictures:
        main('input/'+pic,scale,isDream)