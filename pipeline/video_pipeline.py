import enum
from pipeline import Pipeline

import sys

import gi
gi.require_version("Gst", "1.0")

from gi.repository import Gst

class Mp4MovPipeLine():
    class Errors(enum.Enum):
        UNKNOWN_ERROR = "UNKNOWN_ERROR"
        NO_ERROR = "NO_ERROR"

    err = Errors

    def __init__(self):
        self._pipeline = None
        self._terminate = False

    def compose(self, inputfile, filter, media_overlay, positionx, positiony, scalex, scaley, rotation):
        self._pipeline = Gst.parse_launch("filesrc location="+ inputfile +" ! qtdemux name=demux qtmux name=mux ! filesink location=video.mp4  demux.audio_0 ! queue ! decodebin ! audioconvert ! avenc_aac ! mux.   demux.video_0 ! queue ! decodebin ! videoconvert ! "+ filter +"! videoconvert ! gdkpixbufoverlay location="+ media_overlay +" relative-x={} relative-y={} overlay-width={} overlay-height={} ! rotate angle={} ! mux.".format(positionx, positiony, scalex, scaley, rotation))

    def run(self):
        self._pipeline.set_state(Gst.State.PLAYING)

        bus = self._pipeline.get_bus()
        while True:
            try:
                msg = bus.timed_pop_filtered(
                    0.5 * Gst.SECOND,
                    Gst.MessageType.ERROR | Gst.MessageType.EOS)

                if msg:
                    if msg.type == Gst.MessageType.EOS:
                        self._terminate = True
                        print("Processed Terminating...")

                    elif msg.type == Gst.MessageType.ERROR:
                        print("Unexpected error occured")
                        self._pipeline.set_state(Gst.State.NULL)
                        return self.err.UNKNOWN_ERROR

            except KeyboardInterrupt:
                self._terminate = True
            if self._terminate:
                break
        self._pipeline.set_state(Gst.State.NULL)
        return self.err.NO_ERROR

# Class to handle OGG format video files
class VideoPipeline(Pipeline):
    class Errors(enum.Enum):
        PLAY_ERROR = "PLAY_ERROR"
        UNKNOWN_ERROR = "UNKNOWN_ERROR"
        NO_ERROR = "NO_ERROR"

    err = Errors

    def __init__(self):
        super().__init__()
        self.source = Gst.ElementFactory.make("filesrc", "file-source")
        self.demuxer = Gst.ElementFactory.make("decodebin", "decoder")
        self.videoconvert1 = Gst.ElementFactory.make("videoconvert", "vconvert1")
        self.videoconvert2 = Gst.ElementFactory.make("videoconvert", "vconvert2")
        self.videoconvert3 = Gst.ElementFactory.make("videoconvert", "vconvert3")
        self.overlay = Gst.ElementFactory.make("gdkpixbufoverlay", "overlay")
        self.svgoverlay = Gst.ElementFactory.make("rsvgoverlay", "svgoverlay")
        self.rotate = Gst.ElementFactory.make("rotate", "rotation")
        self.x264enc = Gst.ElementFactory.make("x264enc", "videoencoder")
        self.que = Gst.ElementFactory.make("queue", "que")
        self.avenc_aac = Gst.ElementFactory.make("avenc_aac", "audioencoder")
        self.mp4mux = Gst.ElementFactory.make("mp4mux", "mp4mux")
        self.filesink = Gst.ElementFactory.make("filesink", "fsink")

    def compose(self, filter, inputfile, media_overlay, positionx, positiony, scalex, scaley, rotation):

        self.effects = Gst.ElementFactory.make(filter, "effect")

        self.add_many(self._pipeline, self.source, self.demuxer, self.videoconvert1, self.videoconvert2, self.videoconvert3, self.svgoverlay, self.overlay, self.effects, self.rotate, self.x264enc, self.que, self.avenc_aac, self.mp4mux, self.filesink)

        # Settings up element properties
        source_props = [
            ("location", inputfile)
        ]
        self.ele_prop_set(self.source, source_props)

        filesink_props = [
            ("location", "video.mp4")
        ]
        self.ele_prop_set(self.filesink, filesink_props)

        # Overlay element properties
        overlay_props = [
            ("location", media_overlay),
            ("relative-x", positionx),
            ("relative-y", positiony),
            ("overlay-width", scalex),
            ("overlay-height", scaley),
        ]
        self.ele_prop_set(self.overlay, overlay_props)

        svgoverlay_props = [
            ("location", "overlay.svg"),
            ("y-relative", 0)
        ]
        self.ele_prop_set(self.svgoverlay, svgoverlay_props)

        # Rotate element properties
        rotate_props = [
            ("angle", rotation)
        ]
        self.ele_prop_set(self.rotate, rotate_props)

        avenc_aac_props = [
            ("bitrate", 64000)
        ]
        self.ele_prop_set(self.avenc_aac, avenc_aac_props)

        # Linking source to demuxer and setting demuxer pad-added callbacks
        self.link_many(self.source, self.demuxer)
        self.demuxer.connect("pad-added", self.demuxer_callback)

        # Linking VideoLine
        self.link_many(self.videoconvert1, self.effects, self.overlay, self.rotate, self.videoconvert2, self.svgoverlay, self.videoconvert3, self.x264enc)

        # Linking AudioLine
        self.link_many(self.que, self.avenc_aac)

        # Linking multiplexer to filesink
        self.link_many(self.mp4mux, self.filesink)

        # Mux Video pad link
        mp4mux_video_template = self.mp4mux.get_pad_template("video_%u")
        mp4mux_video_pad = self.mp4mux.request_pad(mp4mux_video_template, None, None)
        print("Obtained request pad {0} for video branch".format(mp4mux_video_pad.get_name()))
        videoconvert2_src_pad = self.x264enc.get_static_pad("src")
        if (videoconvert2_src_pad.link(mp4mux_video_pad) != Gst.PadLinkReturn.OK):
            print("ERROR: Videoconvert src cant be linked with mp4mux video sink")
            sys.exit(1)

        # Mux Audio pad link
        mp4mux_audio_template = self.mp4mux.get_pad_template("audio_%u")
        mp4mux_audio_pad = self.mp4mux.request_pad(mp4mux_audio_template, None, None)
        print("Obtained request pad {0} for audio branch".format(mp4mux_audio_pad.get_name()))
        audioresample_src_pad = self.avenc_aac.get_static_pad("src")
        if (audioresample_src_pad.link(mp4mux_audio_pad) != Gst.PadLinkReturn.OK):
            print("ERROR: Audioresample src cant be linked with mp4mux audio sink")
            sys.exit(1)

    def run(self):
        # Finally set the pipeline to the playing state and check for any errors
        ret = self._pipeline.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            print("Unable to set the pipeline to the playing state.")
            return self.err.PLAY_ERROR

        terminate = False
        bus = self._pipeline.get_bus()
        while True:
            try:
                msg = bus.timed_pop_filtered(
                    0.5 * Gst.SECOND,
                    Gst.MessageType.ERROR | Gst.MessageType.EOS)

                if msg:
                    if msg.type == Gst.MessageType.EOS:
                        terminate = True
                        print("Processed Terminating...")

                    elif msg.type == Gst.MessageType.ERROR:
                        print("Unknown error occured")
                        return self.err.UNKNOWN_ERROR

            except KeyboardInterrupt:
                terminate = True
            if terminate:
                break
        self._pipeline.set_state(Gst.State.NULL)
        return self.err.NO_ERROR