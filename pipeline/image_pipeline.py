import sys
from pipeline import Pipeline

from gi.repository import Gst

from utils import file_format

class ImagePipeline(Pipeline):
    def __init__(self):
        super().__init__()

    # Function to build the pipeline and link the elements
    def compose(self, fileformat, inputfile, media_overlay, scalex, scaley, positionx, positiony):
        self.source = Gst.ElementFactory.make("filesrc", "file-source")
        self.pngdec = Gst.ElementFactory.make("pngdec", "dec")
        self.jpegdec = Gst.ElementFactory.make("jpegdec", "dec1")
        self.overlay = Gst.ElementFactory.make("gdkpixbufoverlay", "overlay")
        self.pngenc = Gst.ElementFactory.make("pngenc", "enc")
        self.jpegenc = Gst.ElementFactory.make("jpegenc", "enc1")
        self.filesink = Gst.ElementFactory.make("filesink", "imgsink")

        self.ele_prop_set(self.source, [("location", inputfile)])

        match fileformat:
            case file_format.JPG.value:
                self.ele_prop_set(self.filesink, [("location", "image.jpg")])
            case _:
                self.ele_prop_set(self.filesink, [("location", "image.png")])
        
        self.ele_prop_set(self.overlay, [("location", media_overlay), ("overlay-width", scalex), ("overlay-height", scaley), ("relative-x", positionx), ("relative-y", positiony)])

        self.add_many(self._pipeline, self.source, self.jpegdec, self.pngdec, self.overlay, self.jpegenc, self.pngenc, self.filesink)

        match fileformat:
            case file_format.JPG.value:
                self.link_many(self.source, self.jpegdec, self.overlay, self.jpegenc, self.filesink)
            case _:
                self.link_many(self.source, self.pngdec, self.overlay, self.pngenc, self.filesink)

    # Function to set the pipeline to playing state
    def run(self):
        ret = self._pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            print("Unable to set the pipeline to the playing state.")
            sys.exit(1)

        bus = self._pipeline.get_bus()
        while True:
            try:
                msg = bus.timed_pop_filtered(
                    0.5 * Gst.SECOND,
                    Gst.MessageType.ERROR | Gst.MessageType.EOS)
                if msg:
                    self._terminate = True
                    print("Processed Terminating...")
            except KeyboardInterrupt:
                self._terminate = True
            if self._terminate:
                break
        self._pipeline.set_state(Gst.State.NULL)