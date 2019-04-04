'''
image georeferencer
'''
import matplotlib.image as mimg
import constants
import math
import os

from osgeo import gdal
from osgeo.gdal import GRA_NearestNeighbour
from geographiclib.geodesic import Geodesic
from json_parser import JsonParser

'''
This class provides an API for image georeferencing.
It extracts the infromation from descriptor file and
warps the image to defined projection.
'''

class Georeferencer:

    '''
    Class for georeferencing
    '''

    def georef(self, descriptor, output_file):

        '''Main georeferencing routine

        Args:
            descriptor (:obj:`dict`): descriptor dictionary
            output_file (:obj:`string`): name of the output file
        '''

        # os.system("gdal_translate/gdalwarp") is an alternative approach
        file_name = descriptor["image_name"]
        image     = mimg.imread(file_name)
        center    = descriptor["center"]
        direction = descriptor["direction"]

        gcps = self.compute_gcps(image, center, direction)

        options = gdal.TranslateOptions(format="GTiff",
                                        outputSRS=constants.DEFAULT_RS,
                                        GCPs=gcps)

        gdal.Translate(destName=constants.TEMP_TIFF_FILE,
                        srcDS=file_name,
                        options=options)

        options = gdal.WarpOptions(srcSRS=constants.DEFAULT_RS,
                                    dstSRS=constants.DEFAULT_RS,
                                    tps=True,
                                    resampleAlg=GRA_NearestNeighbour)

        gdal.Warp(destNameOrDestDS=output_file,
                    srcDSOrSrcDSTab=constants.TEMP_TIFF_FILE,
                    options=options)

        os.remove(constants.TEMP_TIFF_FILE)
        self.create_desc(descriptor, output_file)

    def create_desc(self, descriptor, output_file):

        '''Create desctiptor file

        Args:
            descriptor (:obj:`dict`): descriptor dictionary
            output_file (:obj:`string`): name of the output file
        '''

        desc = {
            "image_name": output_file,
            "sat_type": descriptor["sat_type"],
            "date_time": descriptor["date_time"],
            "center": descriptor["center"],
            "direction": 0
        }

        name, extension = os.path.splitext(output_file)
        desc_name = name + "_desc.json"
        JsonParser.save(desc, desc_name)

    def compute_gcps(self, image, center, direction):

        '''Compute set of GCPs

        Args:
            image (:obj:`np.ndarray`): input image
            center (:obj:`list`): coordinates of center point
            direction (:obj:`float`): direction of the satellite
        '''

        height = image.shape[0]
        width  = image.shape[1]
        self.center = center
        self.center_w = width/2
        self.center_h = height/2
        self.A = direction
        self.B = math.atan(width / height) * 180 / math.pi

        gcps = []

        gcps.append(gdal.GCP(center[1], center[0], 0, self.center_h, self.center_w))

        gcps.append(self.compute_gcp(0, 0, 360 - self.A - self.B))
        gcps.append(self.compute_gcp(0, width, 360 - self.A - self.B - (180 - 2*self.B)))
        gcps.append(self.compute_gcp(height, width, self.B - self.A + (180 - 2*self.B)))
        gcps.append(self.compute_gcp(height, 0, self.B - self.A))

        #gcps.append(self.compute_gcp(height/2, 0, 360 - self.A))
        #gcps.append(self.compute_gcp(0, width/2, 360 - self.A - 90))
        #gcps.append(self.compute_gcp(height/2, width, 360 - self.A - 180))
        #gcps.append(self.compute_gcp(height, width/2, 360 - self.A - 270))

        #gcps.append(self.compute_gcp(height/4, width/4, 360 - self.A - self.B))
        #gcps.append(self.compute_gcp(height/4, 3*width/4, 360 - self.A - self.B - (180 - 2*self.B)))
        #gcps.append(self.compute_gcp(3*height/4, 3*width/4, self.B - self.A + (180 - 2*self.B)))
        #gcps.append(self.compute_gcp(3*height/4, width/4, self.B - self.A))

        #gcps.append(self.compute_gcp(height/2, width/4, 360 - self.A))
        #gcps.append(self.compute_gcp(height/4, width/2, 360 - self.A - 90))
        #gcps.append(self.compute_gcp(height/2, 3*width/4, 360 - self.A - 180))
        #gcps.append(self.compute_gcp(3*height/4, width/2, 360 - self.A - 270))

        #gcps.append(gdal.GCP(-11.79, 60.75, 0, 0, 0))
        #gcps.append(gdal.GCP(34.65, 66.0025, 0, 1002, 0))
        #gcps.append(gdal.GCP(5.63, 33.105, 0, 0, 910))
        #gcps.append(gdal.GCP(41, 38.879, 0, 1002, 910))

        return gcps

    def compute_gcp(self, h, w, angle):

        '''Compute single GCP

        Args:
            h (:obj:`float`): h-axis coordinate
            w (:obj:`float`): w-axis coordinate
            angle (:obj:`float`): azimuth of point
        '''

        distance = self.dist(w, h, self.center_w, self.center_h)
        coords = Geodesic.WGS84.Direct(self.center[0], self.center[1], angle, distance)
        #print(coords['lon2'], coords['lat2'], 0, h, w, distance)
        return gdal.GCP(coords['lon2'], coords['lat2'], 0, h, w)

    def dist(self, w1, h1, w2, h2):

        '''Compute distance between two points

        Args:
            h1 (:obj:`float`): h-axis coordinate of point 1
            w1 (:obj:`float`): w-axis coordinate of point 1
            h2 (:obj:`float`): h-axis coordinate of point 2
            w2 (:obj:`float`): w-axis coordinate of point 2
        '''

        return 1000 * 3.18 * math.sqrt((w1 - w2)**2 + (h1 - h2)**2)

if __name__ == "__main__":
    file_name = "../samples/image_desc.json"
    output_file = "../samples/image_sat_19_1.tiff"
    descriptor = JsonParser.from_file(file_name)

    referencer = Georeferencer()
    referencer.georef(descriptor, output_file)
