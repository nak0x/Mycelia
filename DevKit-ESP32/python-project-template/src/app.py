from src.config import Config
from time import ticks_cpu

class App:
    def __init__(self):
        self.config = Config()
        self.shutdown_request = False
        self.ticks = ticks_cpu

    def run(self):
        while not self.shutdown_request:
            print(self.ticks())
            pass

