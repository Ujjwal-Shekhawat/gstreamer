from os import link
from threading import Thread
from time import sleep
import gi
from utils import *
import pathlib
import sys

gi.require_version("Gst", "1.0")

from gi.repository import Gst, GLib

# Add all elements
def add_many(*args):
    for x in range(len(args) - 1):
        args[0].add(args[x + 1])

# Link elements
def link_many(*args):
    for x in range(len(args) - 1):
        args[x].link(args[x + 1])

# Sets the given element props
def ele_prop_set(element, props):
    for x in range(len(props)):
        element.set_property(props[x][0], props[x][1])

Args = cli_setup()

Gst.init()

main_loop = GLib.MainLoop()
thread = Thread(target=main_loop.run)
thread.start()

# main code
def video_input():
    def demuxer_callback(demuxer, pad):
        caps = pad.query_caps()
        structure_name = caps.to_string()
        if structure_name.startswith("video"):
            sink_pad = videoconvert1.get_static_pad("sink")
            print("Type: ", structure_name)
            if(pad.link(sink_pad) != Gst.PadLinkReturn.OK):
                print("Video linking error")
                sys.exit(0)
        elif structure_name.startswith("audio"):
            sink_pad = que.get_static_pad("sink")
            print("Type: ", structure_name)
            if(pad.link(sink_pad) != Gst.PadLinkReturn.OK):
                print("Audio linking error")
                sys.exit(0)

    pipeline = Gst.Pipeline.new("main-pipeline")

    # When input file is Video
    source = Gst.ElementFactory.make("filesrc", "file-source")
    demuxer = Gst.ElementFactory.make("decodebin", "decoder")
    videoconvert1 = Gst.ElementFactory.make("videoconvert", "vconvert1")
    videoconvert2 = Gst.ElementFactory.make("videoconvert", "vconvert2")
    videoconvert3 = Gst.ElementFactory.make("videoconvert", "vconvert3")
    effects = Gst.ElementFactory.make(Args.filter, "effect")
    overlay = Gst.ElementFactory.make("gdkpixbufoverlay", "overlay")
    svgoverlay = Gst.ElementFactory.make("rsvgoverlay", "svgoverlay")
    rotate = Gst.ElementFactory.make("rotate", "rotation")
    x264enc = Gst.ElementFactory.make("x264enc", "videoencoder")
    que = Gst.ElementFactory.make("queue", "que")
    avenc_aac = Gst.ElementFactory.make("avenc_aac", "audioencoder")
    mp4mux = Gst.ElementFactory.make("mp4mux", "mp4mux")
    filesink = Gst.ElementFactory.make("filesink", "fsink")

    # Adding all elements to pipeline
    add_many(pipeline, source, demuxer, videoconvert1, videoconvert2, videoconvert3, svgoverlay, overlay, effects, rotate, x264enc, que, avenc_aac, mp4mux, filesink)

    # Settings up element properties
    source_props = [
        ("location", Args.inputfile)
    ]
    ele_prop_set(source, source_props)

    filesink_props = [
        ("location", "video.mp4")
    ]
    ele_prop_set(filesink, filesink_props)

    # Overlay element properties
    overlay_props = [
        ("location", Args.overlay),
        ("relative-x", Args.positionx),
        ("relative-y", Args.positiony),
        ("overlay-width", Args.scalex),
        ("overlay-height", Args.scaley),
    ]
    ele_prop_set(overlay, overlay_props)

    svgoverlay_props = [
        ("location", "overlay.svg"),
        ("y-relative", 0)
    ]
    ele_prop_set(svgoverlay, svgoverlay_props)

    # Rotate element properties
    rotate_props = [
        ("angle", Args.rotation)
    ]
    ele_prop_set(rotate, rotate_props)

    avenc_aac_props = [
        ("bitrate", 64000)
    ]
    ele_prop_set(avenc_aac, avenc_aac_props)

    # Linking source to demuxer and setting demuxer pad-added callbacks
    link_many(source, demuxer)
    demuxer.connect("pad-added", demuxer_callback)

    # Linking VideoLine
    link_many(videoconvert1, effects, overlay, rotate, videoconvert2, svgoverlay, videoconvert3, x264enc)

    # Linking AudioLine
    link_many(que, avenc_aac)

    # Linking multiplexer to filesink
    link_many(mp4mux, filesink)

    # Mux Video pad link
    mp4mux_video_template = mp4mux.get_pad_template("video_%u")
    mp4mux_video_pad = mp4mux.request_pad(mp4mux_video_template, None, None)
    print("Obtained request pad {0} for video branch".format(mp4mux_video_pad.get_name()))
    videoconvert2_src_pad = x264enc.get_static_pad("src")
    if (videoconvert2_src_pad.link(mp4mux_video_pad) != Gst.PadLinkReturn.OK):
        print("ERROR: Videoconvert src cant be linked with mp4mux video sink")
        sys.exit(1)

    # Mux Audio pad link
    mp4mux_audio_template = mp4mux.get_pad_template("audio_%u")
    mp4mux_audio_pad = mp4mux.request_pad(mp4mux_audio_template, None, None)
    print("Obtained request pad {0} for audio branch".format(mp4mux_audio_pad.get_name()))
    audioresample_src_pad = avenc_aac.get_static_pad("src")
    if (audioresample_src_pad.link(mp4mux_audio_pad) != Gst.PadLinkReturn.OK):
        print("ERROR: Audioresample src cant be linked with mp4mux audio sink")
        sys.exit(1)

    # Finally set the pipeline to the playing state and check for any errors
    ret = pipeline.set_state(Gst.State.PLAYING)
    if ret == Gst.StateChangeReturn.FAILURE:
        print("Unable to set the pipeline to the playing state.")
        sys.exit(1)

    terminate = False
    bus = pipeline.get_bus()
    while True:
        try:
            msg = bus.timed_pop_filtered(
                0.5 * Gst.SECOND,
                Gst.MessageType.ERROR | Gst.MessageType.EOS)
            if msg:
                terminate = True
                print("Processed Terminating...")
        except KeyboardInterrupt:
            terminate = True
        if terminate:
            break
    pipeline.set_state(Gst.State.NULL)
    main_loop.quit()
    thread.join()

def image_input(fformat):
    pipeline = Gst.Pipeline.new("main-pipeline")

    # When input file is Image
    source = Gst.ElementFactory.make("filesrc", "file-source")
    pngdec = Gst.ElementFactory.make("pngdec", "dec")
    jpegdec = Gst.ElementFactory.make("jpegdec", "dec1")
    overlay = Gst.ElementFactory.make("gdkpixbufoverlay", "overlay")
    pngenc = Gst.ElementFactory.make("pngenc", "enc")
    jpegenc = Gst.ElementFactory.make("jpegenc", "enc1")
    filesink = Gst.ElementFactory.make("filesink", "imgsink")

    ele_prop_set(source, [("location", Args.inputfile)])

    match fformat:
        case file_format.jpg:
            ele_prop_set(filesink, [("location", "image.jpg")])
        case _:
            ele_prop_set(filesink, [("location", "image.png")])
    
    ele_prop_set(overlay, [("location", Args.overlay), ("overlay-width", Args.scalex), ("overlay-height", Args.scaley), ("relative-x", Args.positionx), ("relative-y", Args.positiony)])

    add_many(pipeline, source, jpegdec, pngdec, overlay, jpegenc, pngenc, filesink)

    match fformat:
        case file_format.jpg:
            print("Working with JPEG")
            link_many(source, jpegdec, overlay, jpegenc, filesink)
        case _:
            print("Working with PNG")
            link_many(source, pngdec, overlay, pngenc, filesink)

    ret = pipeline.set_state(Gst.State.PLAYING)
    if ret == Gst.StateChangeReturn.FAILURE:
        print("Unable to set the pipeline to the playing state.")
        sys.exit(1)

    terminate = False
    bus = pipeline.get_bus()
    while True:
        try:
            msg = bus.timed_pop_filtered(
                0.5 * Gst.SECOND,
                Gst.MessageType.ERROR | Gst.MessageType.EOS)
            if msg:
                terminate = True
                print("Processed Terminating...")
        except KeyboardInterrupt:
            terminate = True
        if terminate:
            break
    pipeline.set_state(Gst.State.NULL)
    main_loop.quit()
    thread.join()

def mp4mov():
    pipeline = Gst.parse_launch("filesrc location="+ Args.inputfile +" ! qtdemux name=demux qtmux name=mux ! filesink location=video.mp4  demux.audio_0 ! queue ! decodebin ! audioconvert ! avenc_aac ! mux.   demux.video_0 ! queue ! decodebin ! videoconvert ! "+ Args.filter +"! videoconvert ! gdkpixbufoverlay location="+ Args.overlay +" relative-x={} relative-y={} overlay-width={} overlay-height={} ! rotate angle={} ! mux.".format(Args.positionx, Args.positiony, Args.scalex, Args.scaley, Args.rotation))
    pipeline.set_state(Gst.State.PLAYING)

    terminate = False
    bus = pipeline.get_bus()
    while True:
        try:
            msg = bus.timed_pop_filtered(
                0.5 * Gst.SECOND,
                Gst.MessageType.ERROR | Gst.MessageType.EOS)
            if msg:
                terminate = True
                print("Processed Terminating...")
        except KeyboardInterrupt:
            terminate = True
        if terminate:
            break
    pipeline.set_state(Gst.State.NULL)
    main_loop.quit()
    thread.join()

def main():
    fext = pathlib.Path(Args.inputfile).suffix
    match fext:
        case file_format.mp4.value:
            mp4mov()
        case file_format.mov.value:
            mp4mov()
        case file_format.ogg.value:
            video_input()
        case file_format.jpg.value:
            image_input(file_format.jpg)
        case file_format.png.value:
            image_input(file_format.png)
        case _:
            print("Try providing ogg, mov, mp4 or jpg, png")
            print(Args.inputfile)
            main_loop.quit()
            thread.join()
            sys.exit(1)

if __name__ == "__main__":
    main()