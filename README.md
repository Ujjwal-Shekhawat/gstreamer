# gstreamer

### Dependencies
---
##### <u>To install Install GStreamer on Debian/Ubuntu</u>
```
sudo apt-get install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-doc gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio
```

##### <u>To install GStreamer on Fedora</u>
```
sudo dnf install gstreamer1-devel gstreamer1-plugins-base-tools gstreamer1-doc gstreamer1-plugins-base-devel gstreamer1-plugins-good gstreamer1-plugins-good-extras gstreamer1-plugins-ugly gstreamer1-plugins-bad-free gstreamer1-plugins-bad-free-devel gstreamer1-plugins-bad-free-extras
```

##### <u>For ArchLinux and Manjaro</u>
```
sudo pacman -S gstreamer gst-plugins-{base,good,bad,ugly} python python-gobject
```

##### <u>For windows </u>
Follow the  [official docs](https://docs.rocos.io/prod/docs/gstreamer-on-windows)
But i woud recommend following this [docs.rocos.io/prod/docs/gstreamer-on-windows](https://docs.rocos.io/prod/docs/gstreamer-on-windows)

### Usage
---
How to run:
```
git clone https://github.com/Ujjwal-Shekhawat/gstreamer
cd gstreamer
python3 main.py --help
```
### CLI
---
```python3 main.py -h``` gives information about avalable cli options
```
usage: main.py [-h] -f  -o  [-fl ] [-r ] [-px ] [-py ] [-sx ] [-sy ]

Gstreamer pipeline

options:
  -h, --help            show this help message and exit
  -f , --inputfile      Input file path
  -o , --overlay        Overlay file path
  -fl [], --filter []   Filter to apply
  -r [], --rotation []  Rotatioon of the file. Range (0 - 1) is in Radians
  -px [], --positionx []
                        X Position of the overlay releative to the input file (range 0 - 1)
  -py [], --positiony []
                        Y Position of the overlay releative to the input file (range 0 - 1)
  -sx [], --scalex []   Set the scale of the overlay
  -sy [], --scaley []   Set the scale of the overlay
  ```

### Examples
---
An example to overlay an image on top of a video and apply a filter on the video
```
python3 main.py -f /path/to/vid.ogg -o /path/to/overlay.jpg -fl frei0r-filter-emboss
```
The above command takes an ogg __video format__ input file and an __image format__ overlay file. It overlays the image on the video and applies the __frei0r-filter-emboss__ filter and then it writes the output as an __video.mp4__.

Another example which takes two image format imputs and overlays one on top of the other and writes the output on __image.{jpg,png}__
```
python3 main.py -f /path/to/image -o /path/to/overlayimage -sx 0.5 -sy 0.5
```
The above command takes two image format inputs and overlays one on top of the other.

```-sx 0.5``` sets the x-position of the overlay to the center position releative to the imput image width.

```-sy 0.5``` sets the y-position of the overlay to the center position releative to the input image height.
### Sample output
---
#### Image example
command: ```python3 main.py -f 1.jpg -o 1.png```
Image 1 | Image 2
:-:|:-:
|<img src="media_files/1.jpg" alt="alt text" width="50%"/>|<img src="media_files/2.png" alt="alt text" width="50%"/>|

__Output Image__
<img src="media_files/image.jpg" alt="alt text" width="100%"/>