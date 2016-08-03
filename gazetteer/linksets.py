#from django.db import transaction
from django.db.models import F
import json
from gazetteer.models import GazSource,LocationTypeField,CodeFieldConfig,NameFieldConfig,LinkSet,LocationName,Location

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

from .settings import TARGET_NAMESPACE_FT 


def genLinkSets():
    """
        scan all location names and generate LinkSets 
    """
    
    ns_xref_count = {}
    ns_list = {}
    lastloc = None
    names = LocationName.objects.filter(namespace__isnull=False).order_by('location')
    for name in names :
        if name.location != lastloc :
            for ns in ns_list :
                if not ns_xref_count.get(ns) :
                    ns_xref_count [ns] = {}
                for ns2 in ns_list :
                    if ns == ns2 :
                        continue
                    if not ns_xref_count [ns].get(ns2) :
                        ns_xref_count [ns][ns2] = 1
                    else:
                        ns_xref_count [ns][ns2] = ns_xref_count [ns][ns2] + 1
            ns_list = {}
            lastloc = name.location
        ns_list[name.namespace] = True
        
    # now scan the x_refs counts and build LinkSets
    LinkSet.objects.all().delete()
    for ns in ns_xref_count :
        for ns2 in ns_xref_count[ns] :
            LinkSet.objects.create(ns1=ns,ns2=ns2,label="".join(('Gazetteer location cross-references between ', ns , ' and ' ,ns2)), count_sources=0,count_links = ns_xref_count[ns][ns2])
            
