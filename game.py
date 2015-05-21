from pygre import Scene
from input import HIDInput, get_devices

import sys
import signal
import os
import collections
import threading

class Game(Scene):
    def __init__(self):
        self.__lock__ = threading.Lock()
        self.downed_keys = {}
        Scene.__init__(self)
        self.__events = {}
        self.input_providers = []
        for devname in get_devices():
            evdev = HIDInput(self, devname)            
            self.input_providers.append(evdev)
            evdev.start()
        def handle_sigint(signum, frame):
            for evdev in self.input_providers:
                evdev.stop()                
            self.stop()
        signal.signal(signal.SIGINT, handle_sigint)

    def quit(self):
        for evdev in self.input_providers:
            evdev.stop()                
        self.stop()

    def dispatch(self, *args):
        with self.__lock__:
            if args[2] == 0:
                del self.__events[args[0]]
            else:
                self.__events[args[0]] = args

    @property
    def events(self):
        pass

    @events.getter
    def events(self):
        return self.__events

    def __update__(self, overruns):
        with self.__lock__:            
            self.update(overruns)            
