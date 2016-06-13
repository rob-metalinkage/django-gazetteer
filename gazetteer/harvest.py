from django.shortcuts import render
#from django.db import transaction
from django.db.models import F
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
import json
from gazetteer.sources.abstractsource import AbstractSource, get_handler
from gazetteer.models import GazSource,LocationTypeField,CodeFieldConfig,NameFieldConfig

import requests


import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

from .settings import TARGET_NAMESPACE_FT 


def harvestsource(req, layerid):
    """
        Get data for a layer and its harvest config and harvest to gazetteer, using id of a GazSource object
        for each feature, build gaz object - then use to match, insert if necessary,  and record name usage
    """
    # get identified layer
    sourcelayer = _getlayerbyid(layerid)
    
    sourcetype='mapstory'
    # optional limit
    maxfeatures = req.GET.get('n')
    if maxfeatures :
        maxfeatures = int(maxfeatures)
    if req.GET.get('pdb') :
        import pdb; pdb.set_trace()

    endpoint =  req.build_absolute_uri(reverse('updateloc'))
    try:
        return HttpResponse ( status=201, mimetype="application/json", content= harvest(sourcetype, sourcelayer ,endpoint,maxfeatures) )
    except Exception as e:
        return HttpResponse( status=500, content=e)
  
def harvestlayer(req, sourcetype, layer_name):
    """
        Get data for a layer and its harvest config and harvest to gazetteersing sourcetype and layer name.
        for each feature, build gaz object - then use to match, insert if necessary,  and record name usages
        the layer set is definined in the settings - and hence the handler to extract the features - from shapefile, postgis etc.
    """
    # get identified layer
    sourcelayer = _getlayer(sourcetype,layer_name)
    
    sourcetype='mapstory'
    # optional limit
    maxfeatures = req.GET.get('n')
    if maxfeatures :
        maxfeatures = int(maxfeatures)
    if req.GET.get('pdb') :
        import pdb; pdb.set_trace()

    endpoint =  req.build_absolute_uri(reverse('updateloc'))
    try:
        return HttpResponse ( status=201, mimetype="application/json", content= harvest(sourcetype, sourcelayer ,endpoint,maxfeatures) )
    except Exception as e:
        return HttpResponse( status=500, content=e)
  
def harvest(sourcetype, sourcelayer,endpoint,maxfeatures = None) :

    # get the harvest mappings for that layer - or throw 400 if not available
    harvestconfig = _getharvestconfig(sourcetype,sourcelayer)
    if not harvestconfig :
        raise  Exception("Harvest configuration not found")
           
    # get an iterator over the features for that layer
    
    f_processed = 0
    f_added = 0
    newnames = 0
    updatednames = 0
    
    source = get_handler(sourcetype)
    if not source :
        raise  Exception("Harvest handler not defined for datasource configured")
    try:
        for f in source().getfeatures(sourcelayer) :
            (newloc, newnamecount, updatenamecount) =  _updategaz(f,harvestconfig,endpoint)
            if newloc :
                f_added += 1
            f_processed += 1
            newnames += newnamecount
            updatednames += updatenamecount
            if maxfeatures and f_processed >= maxfeatures :
                break
    except Exception as e:
        logger.error( "Gazetteer harvest failed during - layer = %s, error = %s" % (str(sourcelayer), e) )
        return e
            
    return "layer %s features %s, added %s" % (str(sourcelayer) , f_processed , f_added )

def _getlayer(sourcetype,layer):
    return GazSource.objects.get(source_type=sourcetype, source=layer)


def _getlayerbyid(layerid):
    return GazSource.objects.get(id=layerid)
 
 
def _updategaz(f,config,endpoint):
    """
        convert a feature to a gaz JSON structure and post it to the gazetteer transaction API
    """
    debugstr=''
    try:
        gazobj = {}
        ltfield = LocationTypeField.objects.get(config=config)
        if not ltfield :
            raise ValueError ('No valid location type specification found')
        elif ltfield.field[0] in ("'",'"') :
            loc_type_normalised = ltfield.field[1:-1]
        else  :
            loc_type_normalised = _lookup_skos_notation_map(TARGET_NAMESPACE_FT, ltfield.namespace, f[ltfield.field] )
        if not loc_type_normalised :
            raise ValueError ('Cannot find standard location type matching ' + config.get('locationType') )
        
            
            
        gazobj['locationType'] = loc_type_normalised
        gazobj['latitude'] = f[config.lat_field]
        gazobj['longitude'] = f[config.long_field]
        #gazobj['defaultName'] = f[config['defaultNameField']]
        
    
        # now record all the names - the API wont insert unless it finds a code, and no matches for that code.
        gazobj['names'] = []
        for namefield in CodeFieldConfig.objects.filter(config=config) :
            gazobj['names'].append( {'name':f[namefield.field],'namespace':namefield.namespace})
        for namefield in NameFieldConfig.objects.filter(config=config) :
            if namefield.languageField and f.get(namefield.languageField) :
                lang = f[namefield.languageField]
            elif namefield.language :
                lang = namefield.language
            else :
                lang = None 
            gazobj['names'].append( {'name':f[namefield.field],'language':lang})
            if namefield.as_default :
                gazobj['defaultName'] = f[namefield.field]
        
        # now post to the transaction API
        # import pdb; pdb.set_trace() 
        result = requests.post( endpoint,data=json.dumps(gazobj))
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
    
def _getharvestconfig(sourcetype,sourcelayer):
    return sourcelayer.config
    