from importlib import import_module

def loadconfigs(deploycontext='mapstory') :
    for cfg in ['tm_world', 'nga', 'nameevents' ] :
        try:
            loadconfig( "_".join( (deploycontext, cfg, 'config')))
        except Exception as e:
            print e

def loadconfig(cfgname):
    print cfgname
    #cm = __import__("".join(('gazetteer.fixtures.',cfgname)))
    cm = import_module("".join(('gazetteer.fixtures.',cfgname)), 'gazetteer.fixtures')
    print cm
    cm.load_base_ft()
    cm.load_ft_mappings()
    cm.load_config()
    