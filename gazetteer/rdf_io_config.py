#
# Configures RDF_IO mappings to make gazetteer source links available as Linked Data resources
#
from uriredirect.models import *
from gazetteer.models import GazSource,GazSourceConfig,LocationTypeField,CodeFieldConfig,NameFieldConfig
from rdf_io.models import ObjectMapping, ObjectType
from gazetteer.settings import TARGET_NAMESPACE_FT
from django.conf import settings
SITEURL=settings.SITEURL
try:
    TARGET_NAMESPACE_FT=settings.TARGET_NAMESPACE_FT
except:
    pass 

RDFSTORE=settings.RDFSTORE
RDFSERVER=settings.RDFSERVER

from rdf_io.models import Namespace, ObjectType,ObjectMapping,AttributeMapping,EmbeddedMapping 
from django.contrib.contenttypes.models import ContentType
from skosxl.models import Scheme

BASE_URI="https://gazetteer.mapstory.org/def/gazetteer/sources"

# mappings for format codes for different technologies
RDFLIB_CODES = { 'xml': 'xml' , 'ttl' : 'turtle', 'json' : 'json-ld', 'html' : 'html' , 'rdf' : 'xml' }
GEOSERVER_CODES = { 'xml': 'gml3' , 'gml' : 'gml3', 'json' : 'json', 'kml' : 'kml' }

def load_base_namespaces():
    """
        load namespaces for the meta model
    """
    _loadNamespace( uri='http://www.w3.org/1999/02/22-rdf-syntax-ns#', prefix='rdf' , defaults={ 'notes' :  'RDF' } )
    _loadNamespace( uri='http://www.w3.org/2000/01/rdf-schema#', prefix='rdfs' , defaults = {  'notes' :  'RDFS' } )
    _loadNamespace( uri='http://www.w3.org/2004/02/skos/core#', prefix='skos' , defaults = {  'notes' :  'SKOS' } )
    _loadNamespace( uri='http://www.w3.org/2008/05/skos-xl#', prefix='skosxl' , defaults = {  'notes' :  'SKOSXL' } )
    _loadNamespace( uri='http://xmlns.com/foaf/0.1/', prefix='foaf' , defaults = {  'notes' :  'FOAF' } )
    _loadNamespace( uri='http://purl.org/dc/terms/', prefix='dct' , defaults = {  'notes' :  'Dublin Core Terms' } )
    _loadNamespace( uri='http://www.w3.org/ns/dcat#', prefix='dcat' , defaults = {  'notes' :  'DCAT' } )
    _loadNamespace( uri='http://www.w3.org/2001/XMLSchema#', prefix='xsd' , defaults = {  'notes' :  'XSD' } )

    _loadNamespace( uri='http://id.sirf.net/def/schema/lid/', prefix='lid' , defaults = {  'notes' :  'LID - allows characterisation of resources such as VoiD:technicalFeatures against Linked Data API view names' } )
    
    _loadNamespace( uri='http://rdfs.org/ns/void#', prefix='void' , defaults = {  'notes' :  'VoiD - vocabulary of interlinked datasets' } )
    _loadNamespace( uri='http://www.w3.org/2003/01/geo/wgs84_pos#', prefix='geo' , defaults = {  'notes' :  'geo WGS84 positioning' } )

    # TODO - should point to stable defs once published
    _loadNamespace( uri='https://gazetteer.mapstory.org/def/ontology/mapstory_api/', prefix='msapi' , defaults = {  'notes' :  'Mapstory API definitions - VoiD descriptions to generate links to resources' } )
    _loadNamespace( uri='https://gazetteer.mapstory.org/def/ontology/geonode_api/', prefix='gnapi' , defaults = {  'notes' :  

    # TODO - global master or local FT list?
    'Geonode API definitions - VoiD descriptions to generate links to resources' } )
    _loadNamespace( uri=TARGET_NAMESPACE_FT, prefix='gft' , defaults = {  'notes' :  'Gazetteer Feature Types'} )
  
    # these are for generated resources and should be synced to SITEURL - unless some other hostname spoofing technique is to be used.
    _loadNamespace( uri=''.join((SITEURL,'def/gazetteer/sources/')), prefix='gazsrc' , defaults = {  'notes' :  'Gazetteer sources - uploaded layers from which locations are mapped' } )
    _loadNamespace( uri=''.join((SITEURL,'def/gazetteer/index/')), prefix='gaz' , defaults = {  'notes' :  'Master gazetteer dataset - the index of all place names' } )
    _loadNamespace( uri='https://gazetteer.mapstory.org/def/ft/', prefix='gftsrc' , defaults = {  'notes' :  'source feature type codes' } )
   
    print "loading base namespaces"
    
def _loadNamespace(uri,prefix,defaults):
    """Brutally load namespace killing any existing namespace with uri or prefix that matches"""
    msg = ""
    try:
        pre = Namespace.objects.get(uri=uri)
        msg = "Replacing ns with URI %s" % uri
        pre.delete()
    except:
        pass
    try:
        pre = Namespace.objects.get(prefix=prefix)
        msg = " , ".join(("Replacing ns with Prefix %s" % prefix,msg))
        pre.delete()
    except:
        pass
    
    Namespace.objects.get_or_create( uri=uri, prefix=prefix, defaults = defaults )
    # TODO should log these I guess.
    return msg

    
def _rdf4j_push_context(rdfstore, resttgt, model, obj, gr ):
    #import pdb; pdb.set_trace()
    headers = {'Content-Type': 'application/x-turtle;charset=UTF-8'} 
  
    for h in rdfstore.get('headers') or [] :
        headers[h] = _resolveTemplate( rdfstore['headers'][h], model, obj )
    
    result = requests.put( resttgt, headers=headers , data=gr.serialize(format="turtle"))
    logger.info ( "Updating resource {} {}".format(resttgt,result.status_code) )
    if result.status_code > 400 :
#         print "Posting new resource"
#         result = requests.post( resttgt, headers=headers , data=gr.serialize(format="turtle"))
        logger.error ( "Failed to publish resource {} {}".format(resttgt,result.status_code) )
        return HttpResponse ("Failed to publish resource {} {}".format(resttgt,result.status_code) , status = result.status_code )
    return result 

def _clean_rules(label):
    try: 
        apirule = RewriteRule.objects.get(label=label)
        AcceptMapping.objects.filter(rewrite_rule=apirule).delete()
        RewriteRule.objects.get(label=label).delete()
    except:
        pass

        
def load_urirules() :
    """Load uriredirect rules for Gazetteer object types.
    
        Loads a set of URL rewriting rules for objects managed or specified as links in the Gazetteer model
        these namespaces apply:
        
        Note - we could chain to the SKOSXL module to load rules for vocabularies - at the moment these are specified in the settings via SKOSPATHS=('ft','featuretypes') and loaded by the SKOSXL module.
    """
    sep = '/'
    if SITEURL[-1:] == '/' :
        sep = ''
        
    try:
        defaultroot = sep.join((SITEURL,"def"))
    except:
        defaultroot = sep.join((SITEURL[0],"def")) 
        
    (reg,created) = UriRegister.objects.get_or_create(label='gazetteer', defaults = { 'url' : '/'.join((defaultroot,'gazetteer')) , 'can_be_resolved' : True} )
    
    label = 'Gazetteer Master Index'
    _clean_rules(label)
    (apirule,created) = RewriteRule.objects.get_or_create(label=label , defaults = {
        'description' : 'Rules for Gazetteer master index items',
                    'parent' : None ,
                    'register' : reg ,
                    'service_location' : SITEURL,
                    'service_params' : None ,
                    'pattern' : 'index/(?P<id>\d+)$' ,
                    'use_lda' : True ,
                    'view_param' : '_view' ,
                    'view_pattern' : None } )
    for ext in RDFLIB_CODES.keys() :
        mt = MediaType.objects.get(file_extension=ext)
        fmt = RDFLIB_CODES[ext]
        (accept,created) = AcceptMapping.objects.get_or_create(rewrite_rule=apirule,media_type=mt, defaults = {
            'redirect_to' : "".join(('${server}','/rdf_io/to_rdf/location/id/$1?_format=', fmt)) } )            

    label = 'Gazetteer Master Index WFS binding'
    _clean_rules(label)
    (apirule,created) = RewriteRule.objects.get_or_create(label=label , defaults = {
        'description' : 'WFS call using ID for Gazetteer master index items',
                    'parent' : apirule ,
                    'register' : None ,
                    'service_location' : SITEURL,
                    'service_params' : None ,
                    'pattern' : None ,
                    'use_lda' : True ,
                    'view_param' : '_view' ,
                    'view_pattern' : 'msapi:wfs'} ) 

    for ext in GEOSERVER_CODES.keys() :
        mt = MediaType.objects.get(file_extension=ext)
        fmt = GEOSERVER_CODES[ext]
        (accept,created) = AcceptMapping.objects.get_or_create(rewrite_rule=apirule,media_type=mt,
            defaults = {
            'redirect_to' : "".join(('${server}','/geoserver/geonode/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=geonode:gaz3&CQL_FILTER=id%3D$1&outputFormat=', fmt)) } )                  
    
    label= 'Gazetteer Sources'
    _clean_rules(label)
    (apirule,created) = RewriteRule.objects.get_or_create(label=label , defaults = {
        'description' : 'Rules for Gazetteer sources - spatial data objects registered in Linked Data view',
                    'parent' : None ,
                    'register' : reg ,
                    'service_location' : "".join((RDFSERVER,"/dna")) ,
                    'service_params' : None ,
                    'pattern' : 'sources/(?P<source>[^\?]+)' ,
                    'use_lda' : True ,
                    'view_param' : '_view' ,
                    'view_pattern' : None } )
    
    # sources are registered in the Linked Data layer - so LDA API can be mapped as defaults
    for ext in ('ttl','json','rdf','xml','html') :
        mt = MediaType.objects.get(file_extension=ext)
        # avoid bug in ELDA HTML - using file extensions but ignoring the fact format overrides it
        if ext == 'html' :
            fmt = ''
        else:
            fmt = ''.join(('&_format=',ext))
        (accept,created) = AcceptMapping.objects.get_or_create(rewrite_rule=apirule,media_type=mt, defaults = {
            'redirect_to' : "".join(('${server}/skos/resource?uri=${uri}',fmt)) } )
    
    label = 'Gazetteer source data'
    viewlist = [ {'name': 'alternates', 'apipath': 'lid/resourcelist?baseuri=${uri}&item=None' }, 
        {'name': 'lid', 'apipath': '${server}/skos/resource?uri=${uri}' }, 
    ]
    for view in viewlist:
        id = ' : '.join((label,"view",view['name']))
        (api_vrule,created) = RewriteRule.objects.get_or_create(
            label=id,
            defaults = {
            'description' : ' : '.join((label,view['name'])) ,
            'parent' : apirule ,
            'register' : None ,
            'service_location' : None ,
            'service_params' : None ,
            'pattern' : None ,
            'use_lda' : True ,
            'view_param' : '_view' ,
            'view_pattern' : view['name'] } )
        for ext in ('ttl','json','rdf','xml','html') :
            mt = MediaType.objects.get(file_extension=ext)
            if ext == 'html' :
                fmt = ''
            else:
                fmt = ''.join(('&_format=',ext))
            (accept,created) = AcceptMapping.objects.get_or_create(rewrite_rule=api_vrule,media_type=mt, defaults = {
            'redirect_to' : "".join(('${server}/', view['apipath'],fmt)) } )
            
def load_rdf_mappings():
    """
        load RDF mappings for Gazetteer Objects - locations and data sources
    """
    #(object_type,created) = ObjectType.objects.get_or_create(uri="void:Dataset", defaults = { "label" : "VoiD Dataset" })
    (object_type,created) = ObjectType.objects.get_or_create(uri="msapi:SourceDataset", defaults = { "label" : "MapStory Layer" })

    # quote the target URI namespace as its a constant, not pulled from the model
    pm = new_mapping(object_type, "GazSource", "Gazetteer Source", "source", ''.join(('"',SITEURL,'def/gazetteer/sources/"')), True )
    # specific mapping
    am = AttributeMapping(scope=pm, attr="filter", predicate="msapi:sourceFilter", is_resource=False).save()

        #(object_type,created) = ObjectType.objects.get_or_create(uri="void:Dataset", defaults = { "label" : "VoiD Dataset" })
    (object_type,created) = ObjectType.objects.get_or_create(uri="msapi:SourceDataset", defaults = { "label" : "MapStory Layer" })

    # quote the target URI namespace as its a constant, not pulled from the model
    pm = new_mapping(object_type, "Location", "Gazetteer entry", "id", ''.join(('"',SITEURL,'def/gazetteer/index/"')), False )
    # specific mapping
    am = AttributeMapping(scope=pm, attr="locationType.term", predicate="msapi:locationTypeCode", is_resource=False).save()
    am = AttributeMapping(scope=pm, attr="locationType.uri", predicate="msapi:locationType", is_resource=True).save()
    am = AttributeMapping(scope=pm, attr="latitude", predicate="geo:lat", is_resource=False).save()
    am = AttributeMapping(scope=pm, attr="longitude", predicate="geo:long", is_resource=False).save()
    am = AttributeMapping(scope=pm, attr="locationname.name@language", predicate="msapi:namesource", is_resource=False).save()
    em = EmbeddedMapping(scope=pm, attr="locationname[namespace=]" , predicate="msapi:namesource", struct="""msapi:name name ; msapi:language language ; msapi:namespace namespace ;  msapi:startDate startDate ; msapi:endDate endDate ; msapi:source nameUsed.source ; msapi:attr nameUsed.config.codefieldconfig.field ; rdfs:seeAlso <%s/def/gazetteer/sources/{nameUsed.source}?_view=name&name={name}>""" % SITEURL ).save()
    em = EmbeddedMapping(scope=pm, attr="locationname[namespace=None]" , predicate="msapi:namesource", struct="""msapi:name name ; msapi:language language ; msapi:namespace namespace ;  msapi:startDate startDate ; msapi:endDate endDate ; msapi:source nameUsed.source ; msapi:attr nameUsed.config.namefieldconfig.field ; rdfs:seeAlso <%s/def/gazetteer/sources/{nameUsed.source}?_view=name&name={name}>""" % SITEURL ).save()
    em = EmbeddedMapping(scope=pm, attr="id" , predicate="rdfs:seeAlso", struct="<{$URI}?_view=alternates>" ).save()
    
def new_mapping(object_type,content_type_label, title, idfield, tgt, autopush):
    content_type = ContentType.objects.get(app_label="gazetteer",model=content_type_label.lower())
 
    ObjectMapping.objects.filter(name=title).delete()
    (pm,created) =   ObjectMapping.objects.get_or_create(name=title, defaults =
        { "auto_push" : autopush , 
          "id_attr" : idfield,
          "target_uri_expr" : tgt,
          "content_type" : content_type
        })
    if not created :
        AttributeMapping.objects.filter(scope=pm).delete()
        EmbeddedMapping.objects.filter(scope=pm).delete()   
        
    pm.obj_type.add(object_type)
    pm.save()    

    return pm   