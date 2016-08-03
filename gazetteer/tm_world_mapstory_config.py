from gazetteer.models import GazSource,GazSourceConfig,LocationTypeField,CodeFieldConfig,NameFieldConfig
from skosxl.models import Concept, Scheme, MapRelation
from gazetteer.settings import TARGET_NAMESPACE_FT    

print "frog"
(sch,created) = Scheme.objects.get_or_create(uri=TARGET_NAMESPACE_FT[:-1], pref_label="Gaz Feature types")
try:
    (ft,created) = Concept.objects.get_or_create(term="ADMIN", pref_label="Administrative Boundary", definition = "def", scheme = sch)
except:
    pass
try:
    config=GazSourceConfig.objects.create(lat_field="lat", name="TM_WorldBoundaries", long_field="lon")
    NameFieldConfig.objects.create(config=config,language="en", as_default=True, languageNamespace="", field="name", languageField="")
    LocationTypeField.objects.create(field='"ADMIN"',namespace="http://mapstory.org/def/featuretypes/gazetteer/", config=config)
    CodeFieldConfig.objects.create(config=config,field="iso3",namespace="http://mapstory.org/id/countries/iso3")
    CodeFieldConfig.objects.create(config=config,field="iso2",namespace="http://mapstory.org/id/countries/iso2")
    CodeFieldConfig.objects.create(config=config,field="un",namespace="http://mapstory.org/id/countries/un")
    CodeFieldConfig.objects.create(config=config,field="fips",namespace="http://mapstory.org/id/countries/fips")

    (s,created) = GazSource.objects.get_or_create(source="tm_world_borders", config=config, source_type="mapstory")
    print (s,created)
except Exception as e:
    print "skipping ", e