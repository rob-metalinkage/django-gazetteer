from gazetteer.models import GazSource,GazSourceConfig,LocationTypeField,CodeFieldConfig,NameFieldConfig
from skosxl.models import Concept, Scheme, MapRelation
from gazetteer.settings import TARGET_NAMESPACE_FT    

sch = Scheme.objects.create(uri=TARGET_NAMESPACE_FT[:-1], pref_label="Gaz Feature types")
ft = Concept.objects.create(term="ADMIN", pref_label="Administrative Boundary", definition = "def", scheme = sch)
 
config=GazSourceConfig.create(lat_field="lat", name="TM_WorldBoundaries", long_field="lon")
NameFieldConfig.create(config=config,language="en", as_default=True, languageNamespace="", field="name", languageField="")
LocationTypeField.create(field='"ADMIN"',namespace="http://mapstory.org/def/featuretypes/gazetteer/", config=config)
CodeFieldConfig.create(config=config,field="iso3",namespace="http://mapstory.org/id/countries/iso3")
CodeFieldConfig.create(config=config,field="iso2",namespace="http://mapstory.org/id/countries/iso2")
CodeFieldConfig.create(config=config,field="un",namespace="http://mapstory.org/id/countries/un")
CodeFieldConfig.create(config=config,field="fips",namespace="http://mapstory.org/id/countries/fips")

GazSourceConfig.create(source="tm_world_borders_2005", config=config, source_type="geonode")