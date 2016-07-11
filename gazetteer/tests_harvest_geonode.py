from django.test import TestCase
from django.core.urlresolvers import reverse
import datetime
import json
from gazetteer.models import Location,LocationName
#from skosxl.models import Concept, Scheme, MapRelation
from gazetteer.settings import TARGET_NAMESPACE_FT
from gazetteer.harvest import harvest, _getlayer

class GazHarvestTest(TestCase):

    def setUp(self):
        #import pdb; pdb.set_trace()
        import gazetteer.test_geonode_config
        
    def test_harvest(self):
        """
        Tests the harvester endpoint - assumes a config and data are loaded..
        """
        #import pdb; pdb.set_trace()
        sourcelayer=_getlayer('geonode','tm_world_borders_2005')
        report = harvest('geonode',sourcelayer, 1)
        print report
        
 