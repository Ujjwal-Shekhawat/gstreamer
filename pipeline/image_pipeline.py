import sys
import enum
from pipeline import Pipeline

from gi.repository import Gst

from utils import file_format

class ImagePipeline(Pipeline):
    class Errors(enum.Enum):
            PLAY_ERROR = "PLAY_ERROR"
            FILE_FORMAT_ERROR = "FILE_FORMAT_ERROR"
            UNKNOWN_ERROR = "UNKNOWN_ERROR"
            NO_ERROR = "NO_ERROR"

    err = Errors

    def __init__(self):
        super().__init__()
        self.source = Gst.ElementFactory.make("filesrc", "file-source")
        self.pngdec = Gst.ElementFactory.make("pngdec", "dec")
        self.jpegdec = Gst.ElementFactory.make("jpegdec", "dec1")
        self.overlay = Gst.ElementFactory.make("gdkpixbufoverlay", "overlay")
        self.pngenc = Gst.ElementFactory.make("pngenc", "enc")
        self.jpegenc = Gst.ElementFactory.make("jpegenc", "enc1")
        self.filesink = Gst.ElementFactory.make("filesink", "imgsink")


    # Function to build the pipeline and link the elements
    def compose(self, fileformat, inputfile, media_overlay, scalex, scaley, positionx, positiony):

        self.add_many(self._pipeline, self.source, self.jpegdec, self.pngdec, self.overlay, self.jpegenc, self.pngenc, self.filesink)

        self.ele_prop_set(self.source, [("location", inputfile)])

        match fileformat:
            case file_format.JPG.value:
                self.ele_prop_set(self.filesink, [("location", "image.jpg")])
                self.link_many(self.source, self.jpegdec, self.overlay, self.jpegenc, self.filesink)
            case file_format.PNG.value:
                self.ele_prop_set(self.filesink, [("location", "image.png")])
                self.link_many(self.source, self.pngdec, self.overlay, self.pngenc, self.filesink)
            case _:
                print("Invalid file format")
                return self.err.FILE_FORMAT_ERROR
        
        self.ele_prop_set(self.overlay, [("location", media_overlay), ("overlay-width", scalex), ("overlay-height", scaley), ("relative-x", positionx), ("relative-y", positiony)])
                

    # Function to set the pipeline to playing state
    def run(self):
        ret = self._pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            print("Unable to set the pipeline to the playing state.")
            return self.err.PLAY_ERROR

        bus = self._pipeline.get_bus()
        while True:
            try:
                msg = bus.timed_pop_filtered(
                    0.5 * Gst.SECOND,
                    Gst.MessageType.ERROR | Gst.MessageType.EOS)

                if msg.type == Gst.MessageType.EOS:
                    self._terminate = True
                    print("Processed Terminating...")

                elif msg.type == Gst.MessageType.ERROR:
                    print("Error occured Exiting")
                    self._pipeline.set_state(Gst.State.NULL)
                    return self.err.UNKNOWN_ERROR

            except KeyboardInterrupt:
                self._terminate = True
            if self._terminate:
                break
        self._pipeline.set_state(Gst.State.NULL)
        return self.err.NO_ERROR