#!/usr/bin/env python
# encoding: utf-8

import npyscreen
import threading
import pyechonest.artist
import pyechonest.config
import textwrap
import time, sys, random
# you need to install libjpeg before installing PIL like via brew install libjpeg
from PIL import Image
from bisect import bisect
import urllib2 as urllib
from cStringIO import StringIO

# Config-things
pyechonest.config.ECHO_NEST_API_KEY="YOUR_KEY_HERE"
_TIME_PER_PICTURE = 90
_THE_YEAR_IS = 1984

npyscreen.disableColor()

def ascii(text, errors='ignore'):
    return text.encode('ascii', errors)

def URL_to_ASCII(url, width=80, height=24):
    # good bits from http://stevendkay.wordpress.com/2009/09/08/generating-ascii-art-from-photographs-in-python/
    # and http://blog.hardlycode.com/pil-image-from-url-2011-01/
    # TODO: MouseText
    greyscale = [" ", " ",".,-","_ivc=!/|\\~","gjez2]/(YL)t[+T7Vf","mdK4ZGbNDXY5P*Q","W8KMA","#%$"]
    greyscale.reverse() # white on black
    zonebounds=[36,72,108,144,180,216,252]
    img_file = urllib.urlopen(url)
    im = StringIO(img_file.read())
    im = Image.open(im)
    (w,h) = im.size
    # change width but not height
    new_width = int(width)
    new_height = int((float(width)/float(w)) * float(h))
    im=im.resize((new_width, new_height),Image.BILINEAR)
    im=im.convert("L")
    pic=""
    for y in range(0,im.size[1]):
        for x in range(0,im.size[0]):
            lum=255-im.getpixel((x,y))
            row=bisect(zonebounds,lum)
            possibles=greyscale[row]
            pic=pic+possibles[random.randint(0,len(possibles)-1)]
        pic=pic+"\n"
    return pic

class KioskApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.artistForm = self.addForm('MAIN', ArtistForm, name='The Echo Nest MUSICAL INFORMATION KIOSK (c) ' + str(_THE_YEAR_IS))
        self.pictureForm = self.addForm('PICTURE', PictureForm, name='HERE IS A PICTURE')
        self.biographyForm = self.addForm('BIOGRAPHY', BiographyForm, name='THEIR BIOGRAPHY')
        self.noArtistForm = self.addForm('NOARTIST', NoArtistForm, name='SORRY NO SUCH ARTIST')

class BiographyForm(npyscreen.Form):
    def create(self):
        self.biographyBox = self.add(npyscreen.Pager, values = ['no','biography'])

    def beforeEditing(self):
        self.biographyBox.start_display_at = 0
        self.biography_text = None
        i = 0
        while not self.biography_text:
            try:
                if not self.parentApp.artistForm.artist.biographies[i].has_key("truncated"):
                    self.biography_text = self.parentApp.artistForm.artist.biographies[i]["text"]
                else:
                    i = i + 1
            except (ValueError, KeyError, IndexError):
                i = i + 1
            if i > 10:
                self.biography_text = "sorry!\n\n\n   NO BIO\n\n"            
        self.biographyBox.values = textwrap.wrap(self.biography_text,width=70)
    
    def afterEditing(self):
        self.parentApp.NEXT_ACTIVE_FORM = 'MAIN'

class PictureForm(npyscreen.Form):
    def create(self):
        self.pictureBox = self.add(npyscreen.Pager,values=['no','picture'])

    def beforeEditing(self):
        self.pictureBox.start_display_at = 0
        self.image_text = None
        i = 0
        while not self.image_text:
            try:
                self.image_text = URL_to_ASCII(self.parentApp.artistForm.artist.images[i]["url"], width=70, height=19)
            except (urllib.HTTPError, ValueError, IndexError):
                i = i + 1
            if i > 10:
                self.image_text = "sorry!\n\n\n   NO PICTURE\n\n"            
        self.pictureBox.values = self.image_text.split('\n')
        
    def afterEditing(self):
        self.parentApp.NEXT_ACTIVE_FORM = 'BIOGRAPHY'
        
class ArtistForm(npyscreen.Form):
    def create(self):
        self.artistBox = self.add(npyscreen.TitleText, name = "Enter an ARTIST NAME:", value="")

    def beforeEditing(self):
        self.artistBox.value = ""
        
    def afterEditing(self):
        self.artist = pyechonest.artist.search(name=self.artistBox.value,artist_start_year_before=_THE_YEAR_IS+1)
        if len(self.artist) > 0:
            self.artist = self.artist[0]
            self.parentApp.NEXT_ACTIVE_FORM = 'PICTURE'
        else:
            self.parentApp.NEXT_ACTIVE_FORM = 'NOARTIST'
            
class NoArtistForm(npyscreen.Form):
    def afterEditing(self):
        self.parentApp.NEXT_ACTIVE_FORM='MAIN'
        
def pretty_print_artist(a):
    """Pretty print a pyechonest artist w/ their years active and location."""
    ya = ""
    loc =""
    if a.cache.has_key("years_active"):
        if len(a.cache["years_active"]) > 0:
            ya = str(a.cache["years_active"][0]["start"]) + " - "
            if a.cache["years_active"][0].has_key("end"):
                if a.cache["years_active"][0]["end"] < _THE_YEAR_IS+1: # remember the time capsule
                    ya = ya + str(a.cache["years_active"][0]["end"])
    if a.cache.has_key('artist_location'):
        loc = a.cache["artist_location"]["location"]
    
    if len(loc) > 1 and len(ya) > 1:
        return a.name + " (" + ya + ")" + " from " + loc
    if len(loc) > 1:
        return a.name + " from " + loc
    if len(ya) > 1:
        return a.name + " (" + ya + ")"
    return a.name

def tick():
    global _pager, _F
    if (( int(time.time()) % _TIME_PER_PICTURE) == 0):
        show()
    else:
        _pager.h_scroll_line_down(None)
        _F.display()
    threading.Timer(1, tick).start()

def show(*args):
    global _pager, _F
    a = random.choice(_artists)
    image_text = None
    i = 0
    while not image_text:
        try:
            image_text = URL_to_ASCII(a.images[i]["url"], width=70, height=19)
        except (urllib.HTTPError, ValueError, IndexError):
            i = i + 1
        if i > 10: # too many retries or no good images
            image_text = "sorry"

    if image_text is not "sorry":
        _F = npyscreen.Form(name=ascii(pretty_print_artist(a)).upper())
        _pager = _F.add(npyscreen.Pager,values=image_text.split('\n'))
        _F.display()

if __name__ == "__main__":
    """Run this like python kiosk.py to enter an auto mode that just cycles through band pictures,
        or without any arguments to enter interactive mode."""

    if len(sys.argv)>1 and sys.argv[1]=="auto":
        _artists = []
        # Get 500 pop artists around your time
        for x in xrange(5):
            _artists = _artists + pyechonest.artist.search(
                results=100,
                start=x*100,
                artist_start_year_before=_THE_YEAR_IS,
                artist_start_year_after=_THE_YEAR_IS-5,
                style="pop",
                sort="familiarity-desc",
                buckets=["years_active","artist_location"])
        npyscreen.wrapper_basic(show)
        threading.Timer(1, tick).start()
    else:
        # interactive mode
        _app = KioskApp()
        _app.run()  
