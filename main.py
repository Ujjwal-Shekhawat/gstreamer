from threading import Thread
from time import sleep
import gi
import argparse
import pathlib
import sys

gi.require_version("Gst", "1.0")

from gi.repository import Gst, GLib

def addall_to_pipeline(*args):
    for x in range(len(args) - 1):
        args[0].add(args[x+1])

def linkall_elements(*args):
    for x in range(len(args) - 1):
        args[x].link(args[x+1])

def ele_prop_set(element, props):
    for x in range(len(props)):
        element.set_property(props[x][0], props[x][1])

Gst.init()

main_loop = GLib.MainLoop()
thread = Thread(target=main_loop.run)
thread.start()

parser = argparse.ArgumentParser(description = "Gstreamer pipeline")
parser.add_argument('-f', '--inputfile', type=str, metavar='', required=True, help="Input file path")
parser.add_argument('-o', '--overlay', type=str, metavar='', required=True, help="Overlay file path")
parser.add_argument('-fl', '--filter', nargs='?', type=str, metavar='', required=False, const="vertigotv", default="vertigotv", help="Filter to apply")
parser.add_argument('-r', '--rotation', nargs='?', type=float, metavar='', required=False, const=0.0, default=0.0, help="Rotatioon of the file. Range (0 - 1) is in Radians")
parser.add_argument('-px', '--positionx', nargs='?', type=float, metavar='', required=False, const=0.0, default=0.0, help="X Position of the overlay releative to the input file (range 0 - 1)")
parser.add_argument('-py', '--positiony', nargs='?', type=float, metavar='', required=False, const=0.0, default=0.0, help="Y Position of the overlay releative to the input file (range 0 - 1)")
parser.add_argument('-sx', '--scalex', nargs='?', type=float, metavar='', required=False, const=1, default=200, help="Set the scale of the overlay. Range (0 - 1) releative to the inputfile")
parser.add_argument('-sy', '--scaley', nargs='?', type=float, metavar='', required=False, const=1, default=200, help="Set the scale of the overlay. Range (0 - 1) releative to the inputfile")

Args = parser.parse_args()

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

    # When imput file is Image
    imgsrc = Gst.ElementFactory.make("filesrc", "image-source")

    # Temp Sinks
    audiosink = Gst.ElementFactory.make("autoaudiosink", "asink")
    videosink = Gst.ElementFactory.make("autovideosink", "vsink")

    # Adding all elements to pipeline
    addall_to_pipeline(pipeline, source, demuxer, videoconvert1, videoconvert2, videoconvert3, svgoverlay, overlay, effects, rotate, x264enc, que, avenc_aac, mp4mux, filesink)

    # Settings up element properties
    source_props = [
        ("location", Args.inputfile)
    ]
    ele_prop_set(source, source_props)

    filesink_props = [
        ("location", "gst_fast.mp4")
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

    # Some tweaks for faster procesing
    avenc_aac_props = [
        ("bitrate", 64000)
    ]
    ele_prop_set(avenc_aac, avenc_aac_props)

    # Linking source to demuxer and setting demuxer pad-added callbacks
    linkall_elements(source, demuxer)
    demuxer.connect("pad-added", demuxer_callback)

    # Linking VideoLine
    linkall_elements(videoconvert1, effects, overlay, rotate, videoconvert2, svgoverlay, videoconvert3, x264enc)

    # Linking AudioLine
    linkall_elements(que, avenc_aac)

    # Linking muxer to filesink
    linkall_elements(mp4mux, filesink)

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

def image_input(format = 0):
    pipeline = Gst.Pipeline.new("main-pipeline")

    # When input file is Video
    source = Gst.ElementFactory.make("filesrc", "file-source")
    pngdec = Gst.ElementFactory.make("pngdec", "dec")
    jpegdec = Gst.ElementFactory.make("jpegdec", "dec1")
    overlay = Gst.ElementFactory.make("gdkpixbufoverlay", "overlay")
    pngenc = Gst.ElementFactory.make("pngenc", "enc")
    jpegenc = Gst.ElementFactory.make("jpegenc", "enc1")
    filesink = Gst.ElementFactory.make("filesink", "imgsink")

    ele_prop_set(source, [("location", Args.inputfile)])
    ele_prop_set(filesink, [("location", "new.jpg")])
    ele_prop_set(overlay, [("location", Args.overlay), ("overlay-width", Args.scalex), ("overlay-height", Args.scaley), ("relative-x", Args.positionx), ("relative-y", Args.positiony)])

    addall_to_pipeline(pipeline, source, jpegdec, pngdec, overlay, jpegenc, pngenc, filesink)

    if(format == 1):
        print("Working with JPEG")
        linkall_elements(source, jpegdec, overlay, jpegenc, filesink)
    else:
        print("Working with PNG")
        linkall_elements(source, pngdec, overlay, pngenc, filesink)

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

def main():
    fext = pathlib.Path(Args.inputfile).suffix
    if(fext.find("ogg") == True):
        print("Video input", Args.inputfile)
        video_input()
    elif(fext.find("jpg") == True or fext.find("png") == True):
        print("Image input", Args.inputfile)
        if(fext.find("jpg") == True):
            print("JPEG")
            image_input(1)
        else:
            print("PNG")
            image_input()
    else:
        print("Try providing ogg or jpg")
        print(Args.inputfile)
        main_loop.quit()
        thread.join()
        sys.exit(1)

if __name__ == "__main__":
    main()