from django.db import models
from skosxl.models import Concept
from .settings import TARGET_NAMESPACE_FT 

# Create your models here.

# superceded LocationType with generic SKOS object.
# this allows mappings between alternative feature type vocabulkaries
#
#class LocationType (models.Model):
#    """
#        Feature types to allow disambiguation of different entities with similar names
#    """
#    code = models.CharField(max_length=10, unique=True)
#    label = models.CharField(max_length=200)
#    definition = models.CharField(max_length=2000)   
#    citation = models.URLField(null=True)
#    def __unicode__(self):
#        return ( self.code + ' = ' + self.label )

# location type will be a SKOS Concept - this gives us direct access to the code - and indirect to any labels via Labels.objects.filter(concept = self.concept)
class Location(models.Model):
    defaultName = models.CharField(max_length=200)
    locationType = models.ForeignKey(Concept, limit_choices_to={'scheme__uri' : TARGET_NAMESPACE_FT[0:-1]})
    latitude = models.FloatField()
    longitude = models.FloatField()
    latMin = models.FloatField(blank=True,null=True)
    latMax = models.FloatField(blank=True,null=True)
    longMin = models.FloatField(blank=True,null=True)
    longMax = models.FloatField(blank=True,null=True)
    def __unicode__(self):
        return ( self.defaultName  )

class LocationName(models.Model):
    location = models.ForeignKey(Location)
    name = models.CharField(max_length=200)
    language = models.CharField(max_length=2,help_text='language code e.g. <em>en</em>', blank=True, null=True)
    namespace = models.URLField(blank=True,null=True)
    nameValidStart = models.DateField(blank=True,null=True)
    nameValidEnd = models.DateField(blank=True,null=True)   
    def __unicode__(self):
        if self.language :
            return ( self.name + '@' + self.language )
        elif self.namespace :
            return (self.name + '(' + self.namespace + ')')
        else :
            return (self.name)
            
class RelType (models.Model):
    code = models.CharField(max_length=20)
    description = models.CharField(max_length=200)

    def __unicode__(self):
        return ( self.code  )

class LocationRelation(models.Model):
    source = models.ForeignKey(Location,related_name='source')
    target = models.ForeignKey(Location,related_name='target')
    rel = models.ForeignKey(RelType)
        
    def __unicode__(self):
        return ( location1 + ' ' + relation + ' ' + location2 )

 
     
    
class GazSourceConfig(models.Model):
    """
        setup parameters to harvest a source data set into a gazetteer format
    """
    name = models.CharField(max_length=100, help_text = "name of config")
    filter = models.TextField(max_length = 1000,blank=True,null=True,help_text="default filter to select features from source data") 
            
    lat_field = models.CharField(max_length=20,blank=True,null=True,help_text="Name of field containing latitude in data source - using OGR conventions")
    long_field = models.CharField(max_length=20,blank=True,null=True,help_text="Name of field containing longitude in data source - using OGR conventions")
    geom_field = models.CharField(max_length=20,blank=True,null=True,help_text="Name of field containing a geometry in data source - using OGR conventions")
   
    def __unicode__(self):
        return ( self.name )
   
        
class GazSource(models.Model):
    """ 
        binding of a specific data source to a potentially re-usable configuration
    """
    source = models.CharField(max_length=100, help_text = "name of source data set or django model type")
    source_type = models.CharField(max_length=20,default="mapstory")
    config = models.ForeignKey(GazSourceConfig)
    filter = models.TextField(max_length = 1000,blank=True,null=True,help_text="optional filter to further refine selection of features defined in config") 

    def __unicode__(self):
        return ( self.source_type + ' : ' + self.source )
    
class NameLink(models.Model):
    """
        records a link between a registered name and a map layer (by ID)
    """
    locname = models.ForeignKey(Location)
    layerid = models.IntegerField()
    
    def __unicode__(self):
        return ( locname + ' in ' + layerid )

class LocationTypeField(models.Model):
    """
        mapping for a source field to a namespace qualified code for location type
    """
    config = models.ForeignKey(GazSourceConfig,unique=True)
    field = models.CharField(max_length=20, help_text="Name of field containing a location type code in data source - using OGR conventions. A constant literal value may be provided in quotes")
    namespace = models.URLField(blank=True,null=True, help_text="leave blank only if the field contains a fully qualified URI")

  
        
class NameFieldConfig(models.Model):
    """
        mapping for a source field to a temporally bounded toponym 
    """
    config = models.ForeignKey(GazSourceConfig)
    field = models.CharField(max_length=20,help_text="Name of field containing a name in data source - using OGR conventions")
    language = models.CharField(max_length=20, null=True,blank=True, help_text="language code, if a constant")
    languageField = models.CharField(max_length=20,help_text="Name of field containing a language identifier for this name - using OGR conventions") 
    languageNamespace = models.CharField(max_length=200,null=True,blank=True, help_text="Namespace of provided language field, if set provide SKOS translation to standard language code using this namespace" )
    name_type = models.CharField(max_length=200,null=True,blank=True, help_text="name type")
    as_default = models.BooleanField(help_text="use this as default label if provided")

  
class CodeFieldConfig(models.Model):
    """
        mapping for a source field to a namespace qualified code
    """
    config = models.ForeignKey(GazSourceConfig)
    field = models.CharField(max_length=20, help_text="Name of field containing a code in data source - using OGR conventions")
    namespace = models.URLField(blank=True,null=True)
  