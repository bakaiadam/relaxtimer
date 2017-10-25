#!/usr/bin/env python
"""Make the X cursor wrap-around.

Adapted from http://appdb.winehq.org/objectManager.php?sClass=version&iId=12599
to work around lack of relative mouse movement http://wiki.winehq.org/Bug6971
for Thief: Dark Shadows (and possibly others)

This version is a little kinder to your CPU than the shell script with
the busy-loop that starts a new process for every pointer query.
"""
from ctypes import cdll, c_int, c_voidp, byref
import time
import ctypes as ct
import os

xlib = cdll.LoadLibrary('libX11.so')

# Maximum screen width and height
MAX_X = 1280
MAX_Y = 1024

class WorkingMeas():
  def __init__(self):
    self.noworktime=30 # after 30 secs, its no work.
    self.pihenotime=2
    self.worksession=0
    self.pihenosession=0
    self.allworkcounter=0
    self.allpihenocounter=0
    self.work=True
    self.lastactivity=time.time()
    self.dialogsent=False
    
  def message(self,activity):
    t=time.time()
    if activity:
      if (self.work):
        self.allworkcounter+=t-self.lastactivity
        self.worksession+=t-self.lastactivity
      self.work=True
      self.pienosession=0
      self.lastactivity=t
    else:
      if self.work:
        if (self.lastactivity+self.noworktime<t):
          self.allpihenocounter+=t-self.lastactivity
          self.pihenosession+=t-self.lastactivity
          self.worksession=0
          self.work=False
          self.dialogsent=False
      else:
        self.allpihenocounter+=t-self.lastactivity
        self.lastactivity=t
    print(self.worksession,self.pihenosession,t-self.lastactivity)
    if (self.pihenotime<self.worksession):
      print("pihenjééé")
      if (not self.dialogsent):
        os.system("zenity --info --text='pihenjé'&")
        self.dialogsent=True
    
    
    
    

keyboard = (ct.c_char * 32)()

# Number of seconds to sleep between polling mouse position.
SLEEPTIME = 1.05

def _main(display):
    w=WorkingMeas()
    root = xlib.XDefaultRootWindow(display)
    mousex = c_int()
    mousey = c_int()
    # pointer for unused return values 
    unused_int = c_int()
    # likewise, querypointer wants a window pointer to write to.  We don't
    # really want to create a new window, but this was the shortest way I
    # could think of to get the memory allocated.
    tmp_win = c_voidp(xlib.XCreateSimpleWindow(display, root, 0, 0, 1, 1,
                                               0, 0, 0))
    def resetMouse(x, y):
        xlib.XWarpPointer(display,None,root,0,0,0,0,x,y)

    def getMouse():
        xlib.XQueryPointer(display, root,
                           byref(tmp_win), byref(tmp_win),
                           byref(mousex), byref(mousey),
                           byref(unused_int),
                           byref(unused_int),
                           byref(unused_int))
    xlib.XQueryKeymap(display, keyboard)
    oldx=c_int(0)
    oldy=c_int(0)
    
    while 1:
        act=False
        keyboard2 = (ct.c_char * 32)()
        
        xlib.XQueryKeymap(display, keyboard2)
        for i in range(32):
          if (keyboard[i]!=keyboard2[i]):
#            print("not eq")
            act=True
          keyboard[i]=keyboard2[i]
        
        
#        print("b",mousex,mousey,oldx,oldy)
        getMouse()
        #if (mousex.value < 2):
        #    resetMouse(x=MAX_X-2, y = mousey.value)
        #elif (mousex.value > (MAX_X-2)):
        #    resetMouse(x=2, y=mousey.value)
#        print("a",mousex,mousey,oldx,oldy)
        if mousex.value!=oldx or mousey.value!=oldy:
          oldx=mousex.value
          oldy=mousey.value
#          print("not eq")
          act=True
        time.sleep(SLEEPTIME)
        w.message(act)


def main():
    try:
        display = xlib.XOpenDisplay(None)
        _main(display)
    finally:
        xlib.XCloseDisplay(display)


if __name__ == '__main__':
    main()
