import box_interface as box
from blessings import Terminal

t = Terminal()

with t.location(0,0):
    print ('This is', t.underline('pretty!'))
