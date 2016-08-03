from gazetteer.models import GazSource,GazSourceConfig,LocationTypeField,CodeFieldConfig,NameFieldConfig
from skosxl.models import Concept, Scheme, MapRelation
from gazetteer.settings import TARGET_NAMESPACE_FT    

(sch,created) = Scheme.objects.get_or_create(uri=TARGET_NAMESPACE_FT[:-1], pref_label="Gaz Feature types")
try:
    (ft,created) = Concept.objects.get_or_create(term="PPL", pref_label="Populated Place", definition = "def", scheme = sch)
except:
    pass

# now set up cross references from NGA feature types namespace
sch2 = Scheme.objects.create(uri="http://www.geonames.org/ontology#", pref_label="NGA gaz codes")
ft2 = Concept.objects.create(term="PPLA", pref_label="Populated Place", definition = "def", scheme = sch2)
mr = MapRelation.objects.create(match_type=  1, origin_concept=ft2 , uri="".join((TARGET_NAMESPACE_FT,"PPL")))

# now set up harvest config
try:
    GazSourceConfig.objects.delete(name="Geonames country file dump")
except:
    pass

try:    
    config=GazSourceConfig.objects.create(lat_field="lat", name="Geonames country file dump", long_field="long")

    LocationTypeField.objects.create(field='dsg',namespace="http://mapstory.org/def/ft/nga/", config=config)
    
    NameFieldConfig.objects.create(config=config,language="", as_default=True, languageNamespace="http://geonames.nga.mil/def/lang/", field="full_name_", languageField="LC",name_type = 'Endonym')
    NameFieldConfig.objects.create(config=config,language="", as_default=False, languageNamespace="http://geonames.nga.mil/def/lang/", field="full_nam_1", languageField="LC",name_type = 'Exonym')
    
    CodeFieldConfig.objects.create(config=config,field="ufi",namespace="http://geonames.nga.mil/id/")
    
    (s,created) = GazSource.objects.get_or_create(source="tu_sample", config=config, source_type="mapstory")
    print (s,created)
except Exception as e:
    print "skipping ", e
    