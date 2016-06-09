from django.shortcuts import render
from django.db import transaction
from django.db.models import F
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from geonode.utils import json_response
import json
# from mapstory.models import Location, LocationName
import psycopg2
import psycopg2.extras
from psycopg2.extensions import AsIs
import requests


import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

from .settings import TARGET_NAMESPACE_FT 


def harvestlayer(req, layerid):
    """
        Get data for a layer and its harvest config and harvest to gazetteer.
        for each feature, build gaz object - then use to match, insert if necessary,  and record name usages
        the layer set is definined in the settings - and hence the handler to extract the features - from shapefile, postgis etc.
    """
    
    # optional limit
    maxfeatures = req.GET.get('n')
    if maxfeatures :
        maxfeatures = int(maxfeatures)
    if req.GET.get('pdb') :
        import pdb; pdb.set_trace()

    # get identified layer
    sourcelayer = _getlayer(layerid)
    # get the harvest mappings for that layer - or throw 400 if not available
    harvestconfig = _getharvestconfig(sourcelayer)
    if not harvestconfig :
        return HttpResponse(
            "Harvest configuration not found",
            mimetype="text/plain",
            status=400)
            
    # get an iterator over the features for that layer
    
    f_processed = 0
    f_added = 0
    newnames = 0
    updatednames = 0
    
    try:
        conn = _get_sourceconn(sourcelayer)
        for f in _getfeatures(conn, harvestconfig) :
            (newloc, newnamecount, updatenamecount) =  _updategaz(req,f,harvestconfig)
            if newloc :
                f_added += 1
            f_processed += 1
            newnames += newnamecount
            updatednames += updatenamecount
            if maxfeatures and f_processed >= maxfeatures :
                break
    except Exception as e:
        logger.error( "Gazetteer harvest failed during - layer = %s, error = %s" % (layerid, e) )
        if conn :
            conn.close()
        
    return json_response({'features':f_processed, 'added':f_added, 'layer':layerid})

def _getlayer(layerid):
    return None

def _get_sourceconn(sourcelayer) :
   # get db connection
    connect_params = "host=localhost dbname=mapstory_data user=mapstory password=foobar"
    return psycopg2.connect(connect_params) 

def _getfeatures(conn,config):
    """
        Yields a feature iterator. Each feature is a dict
        Throws exceptions
        May want to switch to server-side cursor.
    """
    cur = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
    SQL = "select * from %s "  
    if config.get('filter') :
        filterclause = 'WHERE '

        # process clauses in an injection-safe way and append to SQL 
    try :
        cur.execute(SQL, (AsIs(config.get('source')), ))
    except Exception as e:
        # import pdb; pdb.set_trace() 
        raise e
    for r in cur :
        yield r
        # break
    # refactor if necessary to force connection close on failure
    
def _updategaz(req,f,config):
    """
        convert a feature to a gaz JSON structure and post it to the gazetteer transaction API
    """
    if req.GET.get('pdb2') :
        debugstr = 'pdb=1'
    else:
        debugstr = ''
    try:
        gazobj = {}
        if config.get('locationTypeField') :
            loc_type_normalised = _lookup_skos_notation_map(TARGET_NAMESPACE_FT, config.get('locationTypeField')['namespace'], f[config.get('locationTypeField')['field']] )
        elif config.get('locationType') :
            loc_type_normalised = config.get('locationType')
            if not loc_type_normalised :
                raise ValueError ('Cannot find standard location type matching ' + config.get('locationType') )
        else :
            raise ValueError ('No valid location type specification found')
            
        gazobj['locationType'] = loc_type_normalised
        gazobj['latitude'] = f[config['lat_field']]
        gazobj['longitude'] = f[config['long_field']]
        gazobj['defaultName'] = f[config['defaultNameField']]
        
    
        # now record all the names - the API wont insert unless it finds a code, and no matches for that code.
        gazobj['names'] = []
        for namefield in config.get('codes') :
            gazobj['names'].append( {'name':f[namefield['field']],'namespace':namefield['namespace']})
        for namefield in config.get('names') :
            if namefield.get('languageField') and f.get(namefield['languageField']) :
                lang = f[namefield['languageField']]
            elif namefield.get('language') :
                lang = namefield['language']
            else :
                lang = None 
            gazobj['names'].append( {'name':f[namefield['field']],'language':lang})
        # now post to the transaction API
        # import pdb; pdb.set_trace() 
        result = requests.post( "?".join((req.build_absolute_uri(reverse('updateloc')), debugstr)),data=json.dumps(gazobj))
        if result.status_code > 300 :
            logger.error("Error response updating gazetteer %s" % result )
        if debugstr :
            # stop doing more calls now!
            return (True, 0, 0)
    except Exception as e:
        logger.error("Error updating gazetteer %s " % e )
        raise e
        
    return (True, 0, 0)

def _lookup_skos_notation_map( tns, ns_localft, term ) :
    from skosxl.models import Notation, Concept, MapRelation
    # find notation

    lft = Notation.objects.filter(code=term, namespace__uri = ns_localft )
    if lft :
        code = lft[0].concept.get_related_term(ns = tns ) 
        return code
    else:
        lft = Concept.objects.filter(term=term, scheme__uri =  ns_localft[:-1] )
        if lft :
            code = lft[0].get_related_term(ns = tns )
            return code
    return None
    
def _getharvestconfig(sourcelayer):
    config = {
        'source': 'tu_sample',
        'filter': None , 
        'locationTypeField' : { 'field': 'dsg', 'namespace':'http://mapstory.org/def/ft/nga/' },
        'defaultNameField' : 'full_name_' ,
        'codes' : [ 
            {'field': 'ufi', 'namespace':'http://geonames.nga.mil/id/', 'uid':True  }
            ],
        'names' : [
            {'field': 'full_name_', 'languageField':'LC' , 'languageNamespace':'http://geonames.nga.mil/def/lang/','language':None, 'name_type':'Endonym'},
            {'field': 'full_nam_1', 'languageField':'LC' ,'language':'en', 'languageNamespace':'http://geonames.nga.mil/def/lang/', 'name_type':'Exonym'},
            {'field': 'short_form', 'languageField':'LC' ,'language':'en', 'languageNamespace':'http://geonames.nga.mil/def/lang/', 'name_type':'Exonym'}
            ],
        'partOf' : [
            {'field': 'cc1', 'namespace':'http://id.sirf.net/id/siset/UNGEGN'},
            ],
            
        'lat_field' : 'lat',
        'long_field' : 'long',
        'geom_field' : None,
        }
    return( config )