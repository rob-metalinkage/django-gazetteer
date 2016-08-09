from django.shortcuts import render
from django.db import transaction
from django.db.models import F
from itertools import islice
from django.http import HttpResponse, Http404
from geonode.utils import json_response
import json
from gazetteer.models import Location, LocationName, to_date, DATE_STRATEGY_EARLIEST,DATE_STRATEGY_LATEST,DATE_STRATEGY_ALWAYS,DATE_STRATEGY_IFNULL
from skosxl.models import Notation, Concept

from django.views.decorators.csrf import csrf_exempt

from .settings import TARGET_NAMESPACE_FT 


FINDPARAMS = { 'name': 'locationname__name__iexact' ,
    'namestart' : 'locationname__name__istartswith' ,
    'lang' : 'locationname__language',
    'code' : 'locationname__name' ,
    'namespace' : 'locationname__namespace' ,
    }
    
# just throw us into a debugger in the environment.
def debug(req) :
    import pdb; pdb.set_trace()


def genlinksets(req) :
    from gazetteer.linksets import genLinkSets
    return HttpResponse(genLinkSets())    

def loadconfigs(req) :
    return HttpResponse(gazetteer.fixtures.loadconfigs())    
@csrf_exempt


def findloc(req):
    """
        Get a location and its associtaed nested properties based on an id.
    """
    max=100
    page = 1
    try:
        max = int(req.GET.get('max'))
        if max <1 or max > 1000 :
            return HttpResponse('Max values out of range (1-1000)',status=500)
    except:
        if req.GET.get('max'):
            return  HttpResponse('Invalid integer for max',status=500)
    try:
        page = int(req.GET.get('page'))
        if page < 1  :
            return  HttpResponse('Page values out of range 1-',status=500)
    except:
        if req.GET.get('page'):
            return  HttpResponse('Invalid integer for page',status=500) 
            
    if req.GET.get('pdb') :
        import pdb; pdb.set_trace()
    filters = {}
    for param in FINDPARAMS.keys() :
        value = req.GET.get(param)
        if value:
            try:
                filters[ FINDPARAMS[param ] ] = value.decode('unicode_escape')
            except:
                filters[ FINDPARAMS[param ] ] = value
    if len(filters) == 0 :
        return HttpResponse('No valid query parameters found %s' % str( FINDPARAMS.keys()) ,status=500)
    try:
        l = Location.objects.filter(**filters)
    except Exception as e:
        return HttpResponse(e,status=500)
 
#    pdb.set_trace()
    return json_response(_encodeLocList(l,max,page))
    
def getloc(req, locid):
    """
        Get a location and its associtaed nested properties based on an id.
    """
    try:
        l = Location.objects.get(pk=locid)
    except Location.DoesNotExist:
        raise Http404
#    pdb.set_trace()  
    return json_response(_encodeLoc(locid,l))

def _encodeLocList(loclist,max=100,page=1):    
    foundlist = []
    count = 0
    for (count,location) in enumerate(islice(loclist,(page-1)*max, page*max),start=1):
        foundlist.append(_encodeLoc(location.id,location))
    return { 'page':page , 'count':count, 'itemsPerPage':max, 'results':foundlist }
    
def _encodeLoc(locid,l):    
    names = LocationName.objects.filter(location=locid)
    return {'type':l.locationType.term,'locid':locid, 'latitude':l.latitude, 'longitude':l.longitude, 'defaultName':l.defaultName, 'names':_encodeNames(names)}
   
def _encodeNames(names):
    namelist = [] 
    for n in names:
        namelist.append( _encodeName(n) )
    return namelist

def _encodeName(n):
    nprops = {'name':n.name }
    if n.language :
        nprops['language'] = n.language
    if n.namespace :
        nprops['namespace'] = n.namespace
    if n.startDate :
        nprops['startDate'] = n.startDate
    if n.endDate :
        nprops['endDate'] = n.endDate
    return nprops

@csrf_exempt
def matchloc(req, *args, **kwargs):
    """
    Find a matching location based on a gazetteer entry with multiple possible names and codes
    call match with flag not to create if missing
    """
    return _matchloc(req, insert=False )

@csrf_exempt
def updateloc(req, *args, **kwargs):
    """
    Find a matching location based on a gazetteer entry with multiple possible names and codes
    call match with flag to create if missing and at least one unambiguous featurecode is present
    """
    return _matchloc(req, insert=True )
    
def _matchloc(req,insert):
    if req.method != 'POST' :
        return HttpResponse('Access method not supported', status=405)
        # will need to do more work ot make GET work - build locobj...
    if req.GET.get('pdb') :
        import pdb; pdb.set_trace()
    try:
        if req.method == 'POST':
            locobj = json.loads(req.body)
            return json_response(matchlocation(locobj,sourcelayer=None,insert=insert))
        elif req.method == 'GET':
            if not req.GET.get('namespace') and req.GET.get('name').startswith('http') :
                names = [{ 'name':req.GET.get('name'), 'namespace': req.GET.get('name')[0:req.GET.get('name').rfind('/')+1] }]
            elif req.GET.get('namespace') and req.GET.get('name') :
                names = [{ 'namespace':req.GET.get('namespace'), 'name': req.GET.get('name') }]
            elif req.GET.get('namespace') :
                return HttpResponse('namespace but no corresponding name specified', status=400)
            elif req.GET['language'] and req.GET.get('name') :
                names = [{ 'language':req.GET['language'], 'name': req.GET.get('name') }]
            else :
                return  HttpResponse('must specify name and language or namespace', status=400)
        
            typecode = req.GET['locationType']
        else :
            return HttpResponse('method not supported', status=404) 
    except Exception as e:
        # import pdb; pdb.set_trace()   
        return HttpResponse(e, status=400)
    
# return empty list    
    return HttpResponse('[]', status=200)
    
    
def matchlocation(locobj,sourcelayer, insert):
    names = locobj['names']
    typecode = locobj['locationType']    
    # we'll build up lists of location ids for different matching strategies. The client will then have to decide how aggressive to be with accepting answers and dealing with inconsistencies.
    match_ids = { 'code':[] , 'name_lang':[], 'name':[] } 
    
    # list of codes found
    codes = []
    
    for nameobj in names: 
        if not nameobj.has_key('name') :
            # malformed 
            raise ValueError('Missing element (name) in gazetteer object')
        elif not nameobj.get('name') :
            # skip a null entry - thats OK
            continue
        try:
            name_uni = nameobj['name'].decode('unicode_escape')
        except:
            name_uni = nameobj['name']
            
        if nameobj.get('namespace'):
            codes.append( nameobj )
            namelist = LocationName.objects.filter( name=name_uni, namespace=nameobj['namespace'] )
            # should be just one here - but we'll get a list of all found and check this later
            for n in  namelist :
                match_ids['code'].append(n.location.id)
        elif nameobj.get('language'):
            namelist = LocationName.objects.filter( name=name_uni, language=nameobj['language'], location__locationType__term=typecode )    
            if namelist :
                for n in  namelist :
                    match_ids['name_lang'].append(n.location.id)
        else :
            namelist = LocationName.objects.filter( name=name_uni, location__locationType__term=typecode) 
            if namelist :
                for n in  namelist :
                    match_ids['name'].append(n.location.id) 

  
    # now get details of locations from the ids, deduplicating as we go 
    matches = {}
    # we may make this controllable later

    strategy = 'bestonly' 
    
    for matchtype in ["code", "name_lang", "name"] :
        if match_ids.get( matchtype ) :
            for locid in  match_ids[matchtype] :
                if not matches.get(locid) :
                    matches[locid] = {"matchtype":matchtype,"locobj":Location.objects.get(id=locid)}
            if strategy == 'bestonly' and matches :
                break
    
    # now perform basic validation:
    count_codes = 0
    codematch = [] 
    namelangmatch = []
    namematch=[]
    definitiveloc = None
    for loc in matches.keys() :
        # count number of code matches - more than one will indicate some error
        if matches[loc]['matchtype'] == 'code' :
            count_codes += 1
            codematch.append(_encodeLoc(loc,matches[loc]['locobj']))
            definitiveloc = loc
        elif matches[loc]['matchtype'] == 'name_lang' :  
            namelangmatch.append(_encodeLoc(loc,matches[loc]['locobj']))
        elif matches[loc]['matchtype'] == 'name' :  
            namematch.append(_encodeLoc(loc,matches[loc]['locobj']))
        # else :
            # check 
    
    if count_codes > 1 :
        raise ValueError('duplicate records found for feature identifiers  : '+ codematch) 
    elif count_codes == 0 and insert and codes :
        # there were codes provided but no match was made - so we can search for and insert this as a new location if missing
        loc = _insertloc(locobj)
        if loc :
            definitiveloc = loc.id
    
    if insert and definitiveloc:
        for nameobj in names:
            if nameobj.get('name') :
                if not nameobj.get('namespace'):
                    try:
                        nameobj['name'] = nameobj['name'].decode('unicode_escape')
                    except:
                        pass # wasnt escaped unicode after all
                _recordname(nameobj,definitiveloc,sourcelayer)
            


    return {'code':codematch, 'name_lang':namelangmatch, 'name':namematch } 



def _insertloc(locobj):
    """
        insert a new location object, and record each name provided for it
    """
    # import ipdb; ipdb.set_trace()
    # TODO add constraint that the concept in the in the target scheme
    locationType=Concept.objects.get(term=locobj['locationType'], scheme__uri = TARGET_NAMESPACE_FT[:-1])
    if not locationType :
        
        raise ValueError ('Invalid location type ' + locobj['locationType'])   
    
    defaultName = locobj.get('defaultName') or locobj['names'][0].get('name') 
    return Location.objects.create(defaultName=defaultName, locationType=locationType, latitude=locobj['latitude'] , longitude=locobj['longitude'] )
 
    
def recordname(req, locid):
    if req.method == 'POST':
        nameobj = json.loads(req.body)
        status = 'got json'
    elif req.method == 'GET':
        if not req.GET.get('namespace') and req.GET.get('name'):
            nameobj = { 'name':req.GET.get('name'), 'namespace': req.GET.get('name')}
        elif req.GET['language'] and req.GET.get('name') :
            nameobj = { 'language':req.GET['language'], 'name': req.GET.get('name') }
        else :
            HttpResponse('must specify name and language or namespace', status=400)
    else :
        HttpResponse('method not supported', status=404) 
#    pdb.set_trace()
    try:
        status = _recordname(nameobj,locid,None)
    except Exception as e:
        return HttpResponse(e, status=400)
            
    return HttpResponse(status, status=200)
    
def _recordname(nameobj,locid,sourcelayer) :
    loc = Location.objects.get(id=locid)
    status = 'got loc'
    # import pdb; pdb.set_trace()
    obj = None

    if not nameobj.get('name') :
        return 'invalid name object - no name element defined'
    elif nameobj.get('namespace') :
        # we need to check if an incompatible name has been defined already
        names = LocationName.objects.filter( location = loc, namespace=nameobj['namespace'])
        if names :
           for nn in names :
                if nn.name != unicode(nameobj['name']) :
                    raise ValueError('conflicting names {0} {1} found for namespace {2}'.format((nameobj['name'],  nn.name ,nameobj['namespace'] )))
    elif not nameobj.get('language') :
        names = LocationName.objects.filter( location = loc, name=nameobj['name'] )
        #if found then had a name already fall through to update dates if necessary
        if names :
            (obj,created) = (names[0], False)
    else : # look for one with language not set
        names = LocationName.objects.filter( location = loc, name=nameobj['name'] , language=None)
        if names :
            (obj,created) = (names[0], False)
            obj.language = nameobj.get('language')
            
    # have found one with missing language if necessary.
    if not obj :
        (obj, created) = LocationName.objects.get_or_create( location = loc, name=nameobj['name'], language=nameobj.get('language'),namespace=nameobj.get('namespace'), defaults = {} )
    
    status = 'location created ' + str(created)

    if not created and ( nameobj.get('startDate') or nameobj.get('endDate') ) :    # update dates 
        try:
            date = nameobj.get('startDate')
 
            if date:
                recdate = getattr(obj,'startDate')
                strategy = nameobj['startDateStrategy']
                date = to_date(date)
                if not recdate or strategy == DATE_STRATEGY_ALWAYS:
                    obj.startDate = date
                elif strategy == DATE_STRATEGY_EARLIEST :
                    if date_less_than ( date, recdate) :
                        obj.startDate = date
                elif strategy == DATE_STRATEGY_LATEST :
                    if not date_less_than ( date, recdate) :
                        obj.startDate = date    

            date = nameobj.get('endDate')
            if date:
                recdate = getattr(obj,'endDate')
                strategy = nameobj['endDateStrategy']
                date = to_date(date)
                if not recdate or strategy == DATE_STRATEGY_ALWAYS:
                    obj.endDate = date
                elif strategy == DATE_STRATEGY_EARLIEST :
                    if date_less_than ( date, recdate) :
                        obj.endDate = date
                elif strategy == DATE_STRATEGY_LATEST :
                    if not date_less_than ( date, recdate) :
                        obj.endDate = date 
        except Exception as e:
            status = status + ' (with error determining date values) '
            
    if sourcelayer :
        obj.nameUsed.add(sourcelayer)
        obj.save()
    if not created:
        # obj.extra_field = 'some_val'
        status =  'updating counts for ' + F( obj.name) 
    return status


    
def date_less_than( d1, d2 ) :
    """
        compare two dates - may be complex fuzzy dates (like c. 500BC)
    """
    
    return d1 < d2 