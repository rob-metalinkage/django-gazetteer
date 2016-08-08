# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# do this when > 1.6!!!
# from django.db import migrations, models

from gazetteer.models import GazSource,GazSourceConfig,LocationTypeField,CodeFieldConfig,NameFieldConfig
from skosxl.models import Concept, Scheme, MapRelation
from gazetteer.settings import TARGET_NAMESPACE_FT    



def load_base_ft():
    (sch,created) = Scheme.objects.get_or_create(uri=TARGET_NAMESPACE_FT[:-1], defaults = { 'pref_label' :"Gaz Feature types" })
    try:
        (ft,created) = Concept.objects.get_or_create(term="ADMIN", defaults = { 'pref_label' :"Populated Place", 'definition':"Populated place"} , scheme = sch)
    except:
        pass

# now set up cross references from NGA feature types namespace

# now set up harvest config
def load_ft_mappings() :
    pass

def load_config() :
    try:
        GazSourceConfig.objects.filter(name="TM_WorldBoundaries").delete()
    except:
        pass
    config=GazSourceConfig.objects.create(lat_field="lat", name="TM_WorldBoundaries", long_field="lon")
    NameFieldConfig.objects.create(config=config,language="en", as_default=True, languageNamespace="", field="name", languageField="")
    LocationTypeField.objects.create(field='"ADMIN"',namespace="http://mapstory.org/def/featuretypes/gazetteer/", config=config)
    CodeFieldConfig.objects.create(config=config,field="iso3",namespace="http://mapstory.org/id/countries/iso3")
    CodeFieldConfig.objects.create(config=config,field="iso2",namespace="http://mapstory.org/id/countries/iso2")
    CodeFieldConfig.objects.create(config=config,field="un",namespace="http://mapstory.org/id/countries/un")
    CodeFieldConfig.objects.create(config=config,field="fips",namespace="http://mapstory.org/id/countries/fips")

    (s,created) = GazSource.objects.get_or_create(source="tm_world_borders", config=config, source_type="mapstory")
    print (s,created)

"""
class Migration(migrations.Migration):
    initial = True

    dependencies = [
        #('yourappname', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_ft_mappings),
        migrations.RunPython(load_config),
    ]
"""        
