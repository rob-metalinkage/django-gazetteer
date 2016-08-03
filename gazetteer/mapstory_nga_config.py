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
        (ft,created) = Concept.objects.get_or_create(term="PPL", defaults = { 'pref_label' :"Populated Place", 'definition':"Populated place"} , scheme = sch)
    except:
        pass

# now set up cross references from NGA feature types namespace

# now set up harvest config
def load_ft_mappings() :
    (sch2,created) = Scheme.objects.get_or_create(uri="http://mapstory.org/def/ft/nga",  defaults = { 'pref_label' : "NGA gaz codes"} )
    (ft2,created) = Concept.objects.get_or_create(term="PPLA",  scheme = sch2 , defaults = { 'pref_label' :"Populated Place", 'definition':"Populated place"} )
    (ft3,created) = Concept.objects.get_or_create(term="PPLA3", scheme = sch2 , defaults = { 'pref_label' :"Populated Place", 'definition':"Populated place"} )
    (mr,created) = MapRelation.objects.get_or_create(match_type=1, origin_concept=ft2 , uri="".join((TARGET_NAMESPACE_FT,"PPL")))
    (mr,created) = MapRelation.objects.get_or_create(match_type=1, origin_concept=ft3 , uri="".join((TARGET_NAMESPACE_FT,"PPL")))

def load_config(test_sample) :
    try:
        GazSourceConfig.objects.filter(name="NGA GNS gazetteer").delete()
    except:
        pass
    config=GazSourceConfig.objects.create(lat_field="lat", name="NGA GNS gazetteer", long_field="long")

    LocationTypeField.objects.create(field='dsg',namespace="http://mapstory.org/def/ft/nga/", config=config)
    
    NameFieldConfig.objects.create(config=config,language="", as_default=True, languageNamespace="http://geonames.nga.mil/def/lang/", field="full_name_", languageField="LC",nameType = 'Endonym')
    NameFieldConfig.objects.create(config=config,language="", as_default=False, languageNamespace="http://geonames.nga.mil/def/lang/", field="full_nam_1", languageField="LC",nameType = 'Exonym')
    
    CodeFieldConfig.objects.create(config=config,field="ufi",namespace="http://geonames.nga.mil/id/")
    
    (s,created) = GazSource.objects.get_or_create(source=test_sample, config=config, source_type="mapstory")
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