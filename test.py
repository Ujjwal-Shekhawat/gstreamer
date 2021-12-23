import unittest

from threading import Thread
import gi

from pipeline import video_pipeline

gi.require_version("Gst", "1.0")

from gi.repository import Gst
Gst.init()

from pipeline.image_pipeline import ImagePipeline
from pipeline.video_pipeline import VideoPipeline, Mp4MovPipeLine

def image_input(file_extension, inputfile, media_overlay):
    img_pipeline = ImagePipeline()
    img_pipeline.compose(file_extension, inputfile, media_overlay, 100, 100, 0.2, 0.2)
    return img_pipeline.run()

def video_input(file_extension, inputfile, filter, media_overaly):
    match file_extension:
        case ".mp4" | ".mov":
            vid_pipeline = Mp4MovPipeLine()
            vid_pipeline.compose(inputfile, filter, media_overaly, 0.2, 0.2, 100, 100, 0.0)
            return vid_pipeline.run()

        case ".ogg":
            vid_pipeline = VideoPipeline()
            vid_pipeline.compose(filter, inputfile, media_overaly, 0.2, 0.2, 100, 100, 0.0)
            return vid_pipeline.run()
        case _:
            return -1

class Tests(unittest.TestCase):
    def test_image_input(self):
        self.assertEqual(image_input(".jpg", "test_files/1.jpg", "test_files/2.jpg"), ImagePipeline.err.NO_ERROR)
        self.assertEqual(image_input(".jpg", "test_files/2.jpg", "test_files/1.jpg"), ImagePipeline.err.NO_ERROR)
        self.assertEqual(image_input(".jpg", "test_files/3.jpg", "test_files/1.jpg"), ImagePipeline.err.NO_ERROR)
        self.assertEqual(image_input(".jpg", "test_files/1.jpg", "test_files/2.jpg"), ImagePipeline.err.NO_ERROR)

        self.assertEqual(image_input(".png", "test_files/1.png", "test_files/2.png"), ImagePipeline.err.NO_ERROR)
        self.assertEqual(image_input(".png", "test_files/2.png", "test_files/1.png"), ImagePipeline.err.NO_ERROR)
        self.assertEqual(image_input(".png", "test_files/3.png", "test_files/1.png"), ImagePipeline.err.NO_ERROR)
        self.assertEqual(image_input(".png", "test_files/1.png", "test_files/2.png"), ImagePipeline.err.NO_ERROR)

    def test_video_input(self):
        self.assertEqual(video_input(".mov", "test_files/1.mov", "vertigotv", "test_files/1.jpg"), Mp4MovPipeLine.err.NO_ERROR)
        self.assertEqual(video_input(".ogg", "test_files/1.ogg", "vertigotv", "test_files/1.jpg"), VideoPipeline.err.NO_ERROR)

if __name__ == "__main__":
    unittest.main()