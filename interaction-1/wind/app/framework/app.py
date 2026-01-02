import machine
import gc

from time import ticks_cpu, sleep

from framework.config import Config
from framework.utils.abstract_singleton import SingletonBase


class AppState:
    SETUP = 0
    RUNNING = 1
    STOPPED = 2
    SHUTDOWN = 3
    IDLE = 4


class App(SingletonBase):
    # Event hooks
    setup = []
    update = []
    shutdown = []
    on_frame_received = []

    # Constants
    SLOWED = True
    DEBUG = False

    # App state
    state = AppState.SETUP
    old_state = AppState.SETUP

    def _init_once(self):
        self.config = Config()
        self.shutdown_request = False
        self.ticks = ticks_cpu
        self.DEBUG = self.config.debug
        self.SLOWED = self.config.slowed

    def idle(self):
        self.state = AppState.IDLE
        machine.idle()

    def run(self):
        for setup in self.setup:
            try:
                setup()
            except RuntimeError as e:
                print(f"An error occurred while setting up the app: {e}")
                continue
              
        self.state = AppState.RUNNING
        while not self.shutdown_request:
            gc.collect()

            if self.state != self.old_state:
                self.old_state = self.state
                if self.DEBUG:
                    print(f"App state: {self.state}")
                    
            if self.state == AppState.RUNNING:
                for update in self.update:
                    update()
                if self.SLOWED:
                    sleep(0.3)
        else:
            self.state = AppState.SHUTDOWN
            for shutdown in self.shutdown:
                shutdown()

    def broadcast_frame(self, frame):
        if self.DEBUG:
            print(frame)
        # Broadcast frame to all registered handlers
        for hooks in self.on_frame_received:
            hooks(frame)
