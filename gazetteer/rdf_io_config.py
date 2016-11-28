#
# Configures RDF_IO mappings to make gazetteer source links available as Linked Data resources
#

from gazetteer.models import GazSource,GazSourceConfig,LocationTypeField,CodeFieldConfig,NameFieldConfig
from rdf_io.models import ObjectMapping, ObjectType
from gazetteer.settings import TARGET_NAMESPACE_FT,SITEURL    

from rdf_io.models import Namespace, ObjectType,ObjectMapping,AttributeMapping,EmbeddedMapping 
from django.contrib.contenttypes.models import ContentType
from skosxl.models import Scheme

BASE_URI="https://gazetteer.mapstory.org/def/gazetteer/sources"

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
  
    # TODO - these are for generated resources and should be synced to SITEURL
    _loadNamespace( uri='https://gazetteer.mapstory.org/def/gazetteer/sources/', prefix='gazsrc' , defaults = {  'notes' :  'Gazetteer sources - uploaded layers from which locations are mapped' } )
    _loadNamespace( uri='https://gazetteer.mapstory.org/def/gazetteer/index/', prefix='gaz' , defaults = {  'notes' :  'Master gazetteer dataset - the index of all place names' } )
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
    
def load_urirules() :
    """
        Load uriredirect rules for these object types.
    """
    pass

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
    em = EmbeddedMapping(scope=pm, attr="locationname[namespace=]" , predicate="msapi:namesource", struct="""msapi:name name ; msapi:language language ; msapi:namespace namespace ;  msapi:startDate startDate ; msapi:endDate endDate ; msapi:source nameUsed.source ; msapi:attr nameUsed.config.codefieldconfig.field ; rdfs:seeAlso <%sdef/gazetteer/sources/{nameUsed.source}?_view=name&name={name}>""" ).save()
    em = EmbeddedMapping(scope=pm, attr="locationname[namespace=None]" , predicate="msapi:namesource", struct="""msapi:name name ; msapi:language language ; msapi:namespace namespace ;  msapi:startDate startDate ; msapi:endDate endDate ; msapi:source nameUsed.source ; msapi:attr nameUsed.config.namefieldconfig.field ; rdfs:seeAlso <%sdef/gazetteer/sources/{nameUsed.source}?_view=name&name={name}>""" % SITEURL ).save()
    em = EmbeddedMapping(scope=pm, attr="id" , predicate="rdfs:seeAlso", struct="<{$URI}?_view=alternates>" ).save()
    
def new_mapping(object_type,content_type_label, title, idfield, tgt, autopush):
    content_type = ContentType.objects.get(app_label="gazetteer",model=content_type_label.lower())
 
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