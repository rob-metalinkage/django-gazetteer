from gazetteer.models import GazSource,GazSourceConfig,LocationTypeField,CodeFieldConfig,NameFieldConfig
from skosxl.models import Concept, Scheme, MapRelation
from gazetteer.settings import TARGET_NAMESPACE_FT    

sch = Scheme.objects.create(uri=TARGET_NAMESPACE_FT[:-1], pref_label="Gaz Feature types")
ft = Concept.objects.create(term="ADMIN", pref_label="Administrative Boundary", definition = "def", scheme = sch)
 
config=GazSourceConfig.objects.create(lat_field="LAT", name="TM_WorldBoundaries", long_field="LON")
NameFieldConfig.objects.create(config=config,language="en", as_default=True, languageNamespace="", field="NAME", languageField="")
LocationTypeField.objects.create(field='"ADMIN"',namespace="http://mapstory.org/def/featuretypes/gazetteer/", config=config)
CodeFieldConfig.objects.create(config=config,field="ISO3",namespace="http://mapstory.org/id/countries/iso3")
CodeFieldConfig.objects.create(config=config,field="ISO2",namespace="http://mapstory.org/id/countries/iso2")
CodeFieldConfig.objects.create(config=config,field="UN",namespace="http://mapstory.org/id/countries/un")
CodeFieldConfig.objects.create(config=config,field="FIPS",namespace="http://mapstory.org/id/countries/fips")

GazSource.objects.create(source="tm_world_borders_2005", config=config, source_type="geonode")