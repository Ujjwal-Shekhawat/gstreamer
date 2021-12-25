from abc import ABC, abstractmethod

import sys

import gi
gi.require_version("Gst", "1.0")

from gi.repository import Gst


class Pipeline(ABC):
    def __init__(self):
        self._pipeline = Gst.Pipeline.new("main-pipeline")
        self._terminated = False

    # Add all elements
    @staticmethod
    def add_many(*args):
        for x in range(len(args) - 1):
            args[0].add(args[x + 1])
    
    # Link elements
    @staticmethod
    def link_many(*args):
        for x in range(len(args) - 1):
            args[x].link(args[x + 1])

    # Sets the given element props
    @staticmethod
    def ele_prop_set(element, props):
        for x in range(len(props)):
            element.set_property(props[x][0], props[x][1])

    def demuxer_callback(self, demuxer, pad):
        caps = pad.query_caps()
        structure_name = caps.to_string()
        if structure_name.startswith("video"):
            sink_pad = self.videoconvert1.get_static_pad("sink")
            print("Type: ", structure_name)
            if(pad.link(sink_pad) != Gst.PadLinkReturn.OK):
                print("Video linking error")
                sys.exit(0)
        elif structure_name.startswith("audio"):
            sink_pad = self.que.get_static_pad("sink")
            print("Type: ", structure_name)
            if(pad.link(sink_pad) != Gst.PadLinkReturn.OK):
                print("Audio linking error")
                sys.exit(0)

    @abstractmethod
    def compose(self):
        pass

    @abstractmethod
    def run(self):
        pass