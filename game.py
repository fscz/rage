from pygre import Scene
from input import HIDInput

import sys
import signal
import os
import collections
import re
import threading

re_evdev = re.compile("event\d+")


class Game(Scene):
    def __init__(self):
        self.__lock__ = threading.Lock()
        Scene.__init__(self)
        self.__events = []
        for devname in [evdev for evdev in os.listdir('/dev/input') if re_evdev.match(evdev) is not None ]:
            evdev = HIDInput("/dev/input/%s" % devname, self)            
            evdev.start()
        def handle_sigint(signum, frame):
            self.stop()
            sys.exit()
        signal.signal(signal.SIGINT, handle_sigint)

    def dispatch(self, *args):
        with self.__lock__:
            self.__events.append(args)

    @property
    def events(self):
        pass

    @events.getter
    def events(self):
        return self.__events

    def __update__(self, overruns):
        with self.__lock__:
            self.update(overruns)
            del self.__events[:]
