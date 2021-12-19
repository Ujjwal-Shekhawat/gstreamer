# gstreamer
### Usage
---
How to run:
```
git clone https://github.com/Ujjwal-Shekhawat/gstreamer
cd gstreamer
python3 main.py -h
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
  -sx [], --scalex []   Set the scale of the overlay. Range (0 - 1)
  -sy [], --scaley []   Set the scale of the overlay. Range (0 - 1)
  ```
### Examples
---
An example to overlay an image on top of a video and apply a filter on the video
```
python3 main.py -f /path/to/vid.ogg -o /path/to/overlay.jpg -fl frei0r-filter-emboss
```
The above command takes an ogg __video format__ inputfile and an __image format__ overlay file. It overlays the image on the video and applies the frei0r-filter-emboss filter and then it writes the output as an __video.mp4__.

Another example which takes two image format imputs and overlays one on top of the other
```
python3 main.py -f /path/to/image -o /path/to/overlayimage -sx 0.5 -sy 0.5
```
The above command takes two image format inputs and overlays one on top of the other.
```-sx 0.5``` sets the x-position of the overlay to the center position releative to the imput image width
```-sy 0.5``` sets the y-position of the overlay to the center position releative to the input image height