from gazetteer.sources.abstractsource import AbstractSource

from geonode.settings import MEDIA_ROOT
 
import json
import osgeo.ogr
import codecs
#import csv

class GeonodeSource(AbstractSource) :
    """ handler to find a geonode layer by name - locate the uploade  and create a feature iterator """
    
    
    def __init__(self):
        pass
   
 
    def getfeatures(self,sourcebinding):
        """
            Yields a feature iterator. Each feature is a dict
            Throws exceptions
            May want to switch to server-side cursor.
        """
        path = "/".join((MEDIA_ROOT,"layers",".".join((sourcebinding.source,"shp"))))
        shp = osgeo.ogr.Open(path)
        layer = shp.GetLayer()
        source_spatial_ref = layer.GetSpatialRef()
        target_spatial_ref = osgeo.osr.SpatialReference()
        target_spatial_ref.ImportFromEPSG(4326)
        transform = osgeo.osr.CoordinateTransformation(
            source_spatial_ref, target_spatial_ref
        )

        for feature in shp.GetLayer():

            feature = json.loads(feature.ExportToJson())
            geom = osgeo.ogr.CreateGeometryFromJson(json.dumps(feature['geometry']))
            # point -> centroid(geom)
#            point.Transform(transform)
#            point = point.ExportToJson()

#            pdata = json.loads(point)['coordinates']

            data = feature['properties']

#            data['src_longitude'] =  pdata[0]
#            data['src_latitude'] =  pdata[1]
                    
            yield (data)
