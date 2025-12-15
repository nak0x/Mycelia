from framework.app import App
from framework.utils.frames.frame import Frame

class Controller:
    def __init__(self):
        App().setup.append(self.setup)
        App().update.append(self.update)
        App().shutdown.append(self.shutdown)
        App().on_frame_received.append(self.on_frame_received)

    def setup(self):
        pass

    def update(self):    
        pass

    def shutdown(self):
        pass

    def on_frame_received(self, frame: Frame):
        pass