import argparse
import enum

# Argparse setup
def cli_setup():
    parser = argparse.ArgumentParser(description = "Gstreamer pipeline")
    parser.add_argument('-f', '--inputfile', type=str, metavar='', required=True, help="Input file path")
    parser.add_argument('-o', '--overlay', type=str, metavar='', required=True, help="Overlay file path")
    parser.add_argument('-fl', '--filter', nargs='?', type=str, metavar='', required=False, const="vertigotv", default="vertigotv", help="Filter to apply")
    parser.add_argument('-r', '--rotation', nargs='?', type=float, metavar='', required=False, const=0.0, default=0.0, help="Rotatioon of the file. Range (0 - 1) is in Radians")
    parser.add_argument('-px', '--positionx', nargs='?', type=float, metavar='', required=False, const=0.0, default=0.0, help="X Position of the overlay releative to the input file (range 0 - 1)")
    parser.add_argument('-py', '--positiony', nargs='?', type=float, metavar='', required=False, const=0.0, default=0.0, help="Y Position of the overlay releative to the input file (range 0 - 1)")
    parser.add_argument('-sx', '--scalex', nargs='?', type=int, metavar='', required=False, const=1, default=200, help="Set the scale of the overlay")
    parser.add_argument('-sy', '--scaley', nargs='?', type=int, metavar='', required=False, const=1, default=200, help="Set the scale of the overlay")

    Args = parser.parse_args()
    return Args

# Sets the given element props
def ele_prop_set(element, props):
    for x in range(len(props)):
        element.set_property(props[x][0], props[x][1])

# Enum class for fileformats
class file_format(enum.Enum):
    MP4 = ".mp4"
    MOV = ".mov"
    OGG = ".ogg"
    JPG = ".jpg"
    PNG = ".png"