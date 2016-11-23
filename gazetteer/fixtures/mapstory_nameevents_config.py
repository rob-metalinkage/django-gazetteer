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
    pass
    
def load_config() :
    try:
        GazSourceConfig.objects.filter(name="Mapstory naming events special format").delete()
    except:
        pass
    config=GazSourceConfig.objects.create(lat_field="lat", name="Mapstory naming events special format", long_field="long")

    LocationTypeField.objects.create(field='"PPL"',namespace=TARGET_NAMESPACE_FT, config=config)
    
    NameFieldConfig.objects.create(config=config,language="", as_default=False, languageNamespace="", field="name_after", languageField="",delimiter=',', startDate='start_date', endDate='end_date', nameType = 'Endonym')
   
    CodeFieldConfig.objects.create(config=config,field="gnis_id",namespace="http://geonames.nga.mil/id/")
    CodeFieldConfig.objects.create(config=config,field="geonamesid",namespace="http://sws.geonames.org/")
    
    (s,created) = GazSource.objects.get_or_create(source="istanbulevents", config=config, source_type="mapstory")

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
