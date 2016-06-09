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
        
class NameLink(models.Model):
    """
        records a link between a registered name and a map layer (by ID)
    """
    locname = models.ForeignKey(Location)
    layerid = models.IntegerField()
    
    def __unicode__(self):
        return ( locname + ' in ' + layerid )
