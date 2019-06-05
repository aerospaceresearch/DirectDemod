import os
import argparse

from directdemod import constants


def generate(map_name, tms_dir):

    """generates leaflet map in `tms_dir` named `map_name`

    Args:
        map_name (:obj: `string`): name of map to generate
        tms_dir (:obj: `string`): path to tms directory
    """

    leaflet = open(constants.MAP_TEMPLATE).read()
    with open(tms_dir + "/" + map_name, 'w') as f:
        f.write(leaflet)


def main():
    """CLI interface for generating maps for noaa images"""

    parser = argparse.ArgumentParser(description="Map generator for NOAA images using gdal2tiles.py")
    parser.add_argument("-r", "--raster", required=True, help="Raster for visualization.")
    parser.add_argument("-m", "--map", default="map.html", required=False, help="Name output map.")
    parser.add_argument("-t", "--tms", default="tms", required=False, help="Tms directory name.")

    args = parser.parse_args()

    os.system("gdal2tiles.py --profile=mercator -z 1-6 -w none " + args.raster + " " + args.tms)

    generate(args.map, args.tms)


if __name__ == "__main__":
    main()
