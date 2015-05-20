import threading
from select import select
from evdev import InputDevice, categorize, KeyEvent, list_devices
import time

class HIDInput:
    def __init__(self, listener, dev_file):
        self.dev = InputDevice(dev_file)
        self.listener = listener

    def start(self):
        self.__running = True
        self.thread = threading.Thread(
            target=self.__loop__,
            kwargs=dict())
        self.thread.daemon = True
        self.thread.start()
    
    def dispatch(self, event):
        if isinstance(event, KeyEvent):
            self.listener.dispatch( event.scancode, event.keycode, event.keystate )

    def __loop__(self):                
        self.dev.grab()
        while self.__running:
            r,w,x = select([self.dev], [], [])
            for ev in self.dev.read():
                self.dispatch(categorize(ev))
        self.dev.ungrab()

    def stop(self):
        self.__running = False
    

def get_devices():
    return list_devices()
