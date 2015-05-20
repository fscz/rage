from pygre import Scene
from input import HIDInput

import sys
import signal
import os
import collections
import re

re_evdev = re.compile("event\d+")

class Game(Scene):
    def __init__(self):
        Scene.__init__(self)
        for evdev in [evdev for evdev in os.listdir('/dev/input') if re_evdev.match(evdev) is not None ]:
            evdev = HIDInput("/dev/input/%s" % evdev, self)
            self.__eventqueue = []
            evdev.start()
        def handle_sigint(signum, frame):
            self.stop()
            sys.exit()
        signal.signal(signal.SIGINT, handle_sigint)

    def dispatch(self, ev_type, *args):
        print ev_type, args
        self.__eventqueue.append(ev_type)

    @property
    def events(self):
        pass

    @events.getter
    def events(self):
        l = self.__eventqueue
        self.__eventqueue = []
        return l 
