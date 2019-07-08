"""
This module provides an API for merging multiple images.
It extracts needed information and projects images on mercator
projection.
"""

import os
import argparse

from shutil import copyfile
from directdemod import constants


def main() -> None:
    """CLI interface for generating maps for noaa images"""

    parser = argparse.ArgumentParser(
        description="Map generator for NOAA images using gdal2tiles.py")
    parser.add_argument("-r",
                        "--raster",
                        required=True,
                        help="Raster for visualization.")
    parser.add_argument("-t",
                        "--tms",
                        default="tms",
                        required=False,
                        help="Tms directory name.")

    args = parser.parse_args()

    os.system("gdal2tiles.py --profile=mercator -z 1-6 -w none " +
              args.raster + " " + args.tms)

    copyfile(constants.MAP_TEMPLATE, args.tms + "/map.html")
    copyfile(constants.GLOBE_TEMPLATE, args.tms + "/globe.html")


if __name__ == "__main__":
    main()
