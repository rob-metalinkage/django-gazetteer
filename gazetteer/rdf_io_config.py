#
# Configures RDF_IO mappings to make gazetteer source links available as Linked Data resources
#

from gazetteer.models import GazSource,GazSourceConfig,LocationTypeField,CodeFieldConfig,NameFieldConfig
from rdf_io.models import ObjectMapping, ObjectType
from gazetteer.settings import TARGET_NAMESPACE_FT    

def init_mapping()
    obj_type = ObjectType.objects.get(uri='
    ObjectMapping.objects.create(obj_type
	"model" : "rdf_io.objectmapping",
		"fields" : {
			"filter" : null,
			"obj_type" : ["skos:ConceptScheme"],
			"name" : "skos:ConceptScheme default",
			"target_uri_expr" : "uri",
			"id_attr" : "uri",
			"content_type" : ["skosxl", "scheme"]
		}