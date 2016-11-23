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
    Namespace.objects.get_or_create( uri='http://www.w3.org/1999/02/22-rdf-syntax-ns#', defaults = { 'prefix' : 'rdf' , 'notes': 'RDF' } )
    Namespace.objects.get_or_create( uri='http://www.w3.org/2000/01/rdf-schema#', defaults = { 'prefix' : 'rdfs' , 'notes': 'RDFS' } )
    Namespace.objects.get_or_create( uri='http://www.w3.org/2004/02/skos/core#', defaults = { 'prefix' : 'skos' , 'notes': 'SKOS' } )
    Namespace.objects.get_or_create( uri='http://www.w3.org/2008/05/skos-xl#', defaults = { 'prefix' : 'skosxl' , 'notes': 'SKOSXL' } )
    Namespace.objects.get_or_create( uri='http://xmlns.com/foaf/0.1/', defaults = { 'prefix' : 'foaf' , 'notes': 'FOAF' } )
    Namespace.objects.get_or_create( uri='http://purl.org/dc/terms/', defaults = { 'prefix' : 'dct' , 'notes': 'Dublin Core Terms' } )
    Namespace.objects.get_or_create( uri='http://www.w3.org/ns/dcat#', defaults = { 'prefix' : 'dcat' , 'notes': 'DCAT' } )
    Namespace.objects.get_or_create( uri='http://www.w3.org/2001/XMLSchema#', defaults = { 'prefix' : 'xsd' , 'notes': 'XSD' } )

    Namespace.objects.get_or_create( uri='http://id.sirf.net/def/schema/lid/', defaults = { 'prefix' : 'lid' , 'notes': 'LID - allows characterisation of resources such as VoiD:technicalFeatures against Linked Data API view names' } )
    
    Namespace.objects.get_or_create( uri='http://rdfs.org/ns/void#', defaults = { 'prefix' : 'void' , 'notes': 'VoiD - vocabulary of interlinked datasets' } )
    Namespace.objects.get_or_create( uri='http://www.w3.org/2003/01/geo/wgs84_pos#', defaults = { 'prefix' : 'geo' , 'notes': 'geo WGS84 positioning' } )

    
    Namespace.objects.get_or_create( uri='https://gazetteer.mapstory.org/def/ontology/mapstory_api/', defaults = { 'prefix' : 'msapi' , 'notes': 'Mapstory API definitions - VoiD descriptions to generate links to resources' } )
    Namespace.objects.get_or_create( uri='https://gazetteer.mapstory.org/def/ontology/geonode_api/', defaults = { 'prefix' : 'gnapi' , 'notes': 'Geonode API definitions - VoiD descriptions to generate links to resources' } )
    
    Namespace.objects.get_or_create( uri='https://gazetteer.mapstory.org/def/gazetteer/sources/', defaults = { 'prefix' : 'gazsrc' , 'notes': 'Gazetteer sources - uploaded layers from which locations are mapped' } )
    Namespace.objects.get_or_create( uri='https://gazetteer.mapstory.org/def/gazetteer/index/', defaults = { 'prefix' : 'gaz' , 'notes': 'Master gazetteer dataset - the index of all place names' } )
    Namespace.objects.get_or_create( uri='https://gazetteer.mapstory.org/def/ft/', defaults = { 'prefix' : 'gftsrc' , 'notes': 'source feature type codes' } )
    Namespace.objects.get_or_create( uri='https://gazetteer.mapstory.org/def/featuretypes/', defaults = { 'prefix' : 'gft' , 'notes': 'Gazetteer Feature Types'} )
    
    print "loading base namespaces"
    
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