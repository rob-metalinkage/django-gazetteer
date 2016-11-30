from django.db import models
from skosxl.models import Concept
from .settings import TARGET_NAMESPACE_FT 
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
import datetime

SITEURL=settings.SITEURL
try:
    TARGET_NAMESPACE_FT=settings.TARGET_NAMESPACE_FT
except:
    pass
    
# choices 
DATE_STRATEGY_EARLIEST = 1 # choose earliest of provided and stored date
DATE_STRATEGY_LATEST = 2 # choose latest of provided and stored date
DATE_STRATEGY_ALWAYS = 3 # choose provided date and overwrite any stored date
DATE_STRATEGY_IFNULL = 4 # choose provided date if no stored date available

DATE_STRATEGY_CHOICES = (
    (DATE_STRATEGY_EARLIEST, 'Earliest'),
    (DATE_STRATEGY_LATEST, 'Latest'),
    (DATE_STRATEGY_ALWAYS, 'Always use'),
    (DATE_STRATEGY_IFNULL, 'Use if missing'),
)

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

    def url(self):
        return "".join((SITEURL,'def/gazetteer/sources/',source))
        
    def __unicode__(self):
        return ( self.source_type + ' : ' + self.source )
# location type will be a SKOS Concept - this gives us direct access to the code - and indirect to any labels via Labels.objects.filter(concept = self.concept)
class Location(models.Model):
    defaultName = models.CharField(max_length=200)
    locationType = models.ForeignKey(Concept, limit_choices_to={'scheme__uri' : TARGET_NAMESPACE_FT[0:-1]})
    latitude = models.FloatField()
    longitude = models.FloatField()
#    latMin = models.FloatField(blank=True,null=True)
#    latMax = models.FloatField(blank=True,null=True)
#    longMin = models.FloatField(blank=True,null=True)
#    longMax = models.FloatField(blank=True,null=True)
    def __unicode__(self):
        return ( self.defaultName  )

class LocationName(models.Model):
    location = models.ForeignKey(Location)
    name = models.CharField(max_length=200)
    language = models.CharField(max_length=2,help_text=_(u'language code e.g. <em>en</em>'), blank=True, null=True)
 
    namespace = models.URLField(blank=True,null=True)
    startDate = models.IntegerField(blank=True,null=True)
    endDate = models.IntegerField(blank=True,null=True)
    nameUsed = models.ManyToManyField(GazSource,blank=True,null=True)
    
     
        
        
    def __unicode__(self):
        if self.language :
            return ( u'@'.join((self.name,self.language) ) )
        elif self.namespace :
            return (self.name + '(' + self.namespace + ')')
        else :
            return (self.name)

def to_date(date):
    ''' 
        convert a date string to whatever the model supports 
    '''
    if not date:
        return None
    elif type(date) == int :
        return date
    elif type(date) == float :
        return int(date)
    elif type(date) == datetime.date:
        return date.year
    elif type(date) in (str, unicode) :
        try:
            return int(date)
        except:
            pass
    return 666
            
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

 
 

class LocationTypeField(models.Model):
    """
        mapping for a source field to a namespace qualified code for location type
    """
    config = models.ForeignKey(GazSourceConfig,unique=True)
    field = models.CharField(max_length=20, help_text="Name of field containing a location type code in data source - using OGR conventions. A constant literal value may be provided in quotes")
    namespace = models.URLField(blank=True,null=True, default=TARGET_NAMESPACE_FT, help_text="leave blank only if the field contains a fully qualified URI")

  
        
class NameFieldConfig(models.Model):
    """
        mapping for a source field to a temporally bounded toponym 
    """
    config = models.ForeignKey(GazSourceConfig)
    field = models.CharField(max_length=20,help_text="Name of field containing a name in data source - using OGR conventions")
    delimiter = models.CharField(max_length=5,help_text=_(u'delimiter if multiple names in a field e.g. <em>,</em>'),blank=True,null=True)
    language = models.CharField(max_length=20, null=True,blank=True, help_text="language code, if a constant")
    languageField = models.CharField(max_length=20,blank=True,help_text="Name of field containing a language identifier for this name - using OGR conventions") 
    languageNamespace = models.CharField(max_length=200,null=True,blank=True, help_text="Namespace of provided language field, if set provide SKOS translation to standard language code using this namespace" )
    startDate = models.CharField(max_length=30,null=True,blank=True, help_text="Start date field or expression")
    startDateNull = models.CharField(max_length=30,null=True,blank=True, help_text="Null value to ignore")
    startDateStrategy = models.PositiveSmallIntegerField( _(u'start_date processing strategy'),
                                                    choices=DATE_STRATEGY_CHOICES, 
                                                    default=DATE_STRATEGY_EARLIEST)
    endDate = models.CharField(max_length=30,null=True,blank=True, help_text="Start date field or expression")
    endDateNull = models.CharField(max_length=30,null=True,blank=True, help_text="Null value to ignore")
    endDateStrategy = models.PositiveSmallIntegerField( _(u'end_date processing strategy'),
                                                    choices=DATE_STRATEGY_CHOICES, 
                                                    default=DATE_STRATEGY_LATEST)
    nameType = models.CharField(max_length=200,null=True,blank=True, help_text="Name type")
    as_default = models.BooleanField(help_text="use this as default label if provided")

  
class CodeFieldConfig(models.Model):
    """
        mapping for a source field to a namespace qualified code
    """
    config = models.ForeignKey(GazSourceConfig)
    field = models.CharField(max_length=20, help_text="Name of field containing a code in data source - using OGR conventions")
    namespace = models.URLField(blank=True,null=True)
  
class LinkSet(models.Model):
    """
        container to hold annotated summaries of links between different feature identifiers, by namespace
    """
    label = models.TextField(max_length = 100,blank=True,null=True,help_text="Label")
    ns1 = models.CharField(max_length=500,help_text="Source namespace")
    ns2 = models.CharField(max_length=500,help_text="Target namespace")
    description = models.TextField(max_length = 1000,blank=True,null=True,help_text="Description")
    count_sources = models.IntegerField(verbose_name="number of distinct data sources containing this cross reference")
    count_links = models.IntegerField(verbose_name="number of distinct cross references")
    
    def __unicode__(self):
        return ( "".join( (self.ns1, ' -> ' , self.ns2 , ' (', str(self.count_links), ')'  ) ) )
            