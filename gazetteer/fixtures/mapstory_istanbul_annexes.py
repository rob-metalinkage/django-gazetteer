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
        (ft,created) = Concept.objects.get_or_create(term="ADMIN", defaults = { 'pref_label' :"Administrative unit", 'definition':"An administrative unit"} , scheme = sch)
    except:
        pass

# now set up harvest config
def load_ft_mappings() :
    pass

def load_config() :
    try:
        GazSourceConfig.objects.filter(name="City Administrave Area Annexations").delete()
    except:
        pass
    config=GazSourceConfig.objects.create(geom_field="wkb_geometry", name="City Administrave Area Annexations")
    NameFieldConfig.objects.create(config=config,language="en", as_default=True, languageNamespace="", field="name", languageField="")
    LocationTypeField.objects.create(field='"ADMIN"',namespace=TARGET_NAMESPACE_FT, config=config)
    CodeFieldConfig.objects.create(config=config,field="iso3",namespace="http://mapstory.org/id/countries/iso3")
    
    (s,created) = GazSource.objects.get_or_create(source="istanbul", config=config, source_type="mapstory")
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
