from threading import Thread
import gi
import pipeline
from utils import *
import pathlib

from pipeline.image_pipeline import ImagePipeline
from pipeline.video_pipeline import VideoPipeline, Mp4MovPipeLine

gi.require_version("Gst", "1.0")

from gi.repository import Gst, GLib

Args = cli_setup()

Gst.init()

main_loop = GLib.MainLoop()
thread = Thread(target=main_loop.run)
thread.start()

def video_input(file_extension):
    match file_extension:
        case file_format.MP4.value | file_format.MOV.value:
            vid_pipeline = Mp4MovPipeLine()
            vid_pipeline.compose(Args.inputfile, Args.filter, Args.overlay, Args.positionx ,Args.positiony, Args.scalex, Args.scaley, Args.rotation)
            vid_pipeline.run()

        case file_format.OGG.value:
            vid_pipeline = VideoPipeline()
            vid_pipeline.compose(Args.filter, Args.inputfile, Args.overlay, Args.positionx, Args.positiony, Args.scalex, Args.scaley, Args.rotation)
            vid_pipeline.run()

def image_input(file_extension):
    img_pipeline = ImagePipeline()
    img_pipeline.compose(file_extension, Args.inputfile, Args.overlay, Args.scalex, Args.scaley, Args.positionx, Args.positiony)
    img_pipeline.run()

def main():
    file_extension = pathlib.Path(Args.inputfile).suffix

    match file_extension:
        case file_format.MP4.value | file_format.MOV.value | file_format.OGG.value:
            video_input(file_extension)

        case file_format.JPG.value | file_format.PNG.value:
            image_input(file_extension)

        case _:
            print("Try providing ogg, mov, mp4 or jpg, png")

    main_loop.quit()
    thread.join()

if __name__ == "__main__":
    main()