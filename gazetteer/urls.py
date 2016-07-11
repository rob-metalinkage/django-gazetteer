from django.conf.urls import patterns, url
from gazetteer.views import getloc,recordname,matchloc,updateloc,debug
from gazetteer.harvest import harvestsource,harvestlayer

urlpatterns = patterns(
    '',
    url(r'location/(?P<locid>\d+)$', getloc, name='getloc'),
    url(r'location/(?P<locid>\d+)/recordname$', recordname, name='recordname'),
    url(r'location/matchloc$', matchloc, name='matchloc'),
    url(r'location/updateloc$', updateloc, name='updateloc'),
    url(r'debug$', debug, name='debug'),
    url(r'harvest/(?P<layerid>\d+)$',harvestsource,name='harvestsource'),
    url(r'harvest/(?P<sourcetype>[\w\d_]+)/(?P<layer_name>.+)$',harvestlayer,name='harvestlayer'),

    #    url(r'^location/matchloc$', include(patterns('',
#        url(r'^(?P<name>\+)$', 'recordname', name='recordname'),
#    ))),
)
