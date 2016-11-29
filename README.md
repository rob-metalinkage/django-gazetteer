# django-gazetteer

Gazetteer functionality implemented in Django.

A gazetteer is an index of places and locations, and the labels (names) used.

django-gazetteer extend typical simple gazetteers by:
* indexing content hidden in multiple data sets - such as uploaded GIS data not normally searchable by name
* supporting multi-lingual names
* supporting temporal metadata about when names where used
* creating links from names to the many places such data can be found (the "harvested" sources used to build the index)

Gazetteer supports harvesting multiple alternative names and codes for "features" from source data sets. It comes with default handlers for:
* a [Geonode](http://geonode.org/) context using local shapefile data storage
* the [Mapstory](http://mapstory.org/) application loaded to a postgis data store 
* *and can be extended to provide equivalent functionality to other data sources - including direct access to django objects*

Uses [django-skosxl](https://github.com/rob-metalinkage/django-skosxl) to handle field and value-mappings from input data.
If configured it uses [django-rdf-io](https://github.com/rob-metalinkage/django-rdf-io) to register such links to an RDF environment - using VoiD Linkset descriptions
It also uses [uriredirect](https://github.com/rob-metalinkage/uriredirect) to create simple shortcuts to locate gazetteer entries and multiple (potentially distributed) service endpoints to get data about a place name.

## Status: 
Proof-of-concept - currently being developed against Geonode 2.4 and Mapstory (using later geonode and django 1.8)

# Design Goals

1. Gazetteer collates alternative place names for a single feature from multiple sources. 
1. Designed to allow post-hoc reconciliation of equivalent features, but to be able to respect any unique identifying codes in any namespace - i.e. two features form different sources that use the same external identifier are assumed equivalent.
1. Multi-lingual and temporal name validity support.
1. Support null as unknowns for language, status and temporal validity range
1. Linked Data ready URI identifiers for gazetteer entries
1. By remembering which resource each name was found, the gazetteer provides a hub function in a Linked Data view of such resources. 
1. Extensible to handle alternative enviroments
1. Content is held django models so that users can interact to reconcile and extend data in UI workflows as required.
1. Synchronisation of data with one or more spatial stores - i.e. a OLAP model - gazetteer django is the transactional database - dump views to warehouses and datamarts for specific use cases.

# Components
Django-gazetteer uses a "semantics" framework to handle:

* management of terminology cross references in a transparent way
* using semantic reasoning to build rich sets of links from gazetteer entries to resources in the local environment in a configurable way
* Creating a Linked Data layer so such links can be discovered and followed easily


# installation

Working on ansible scripts to automate this - in the meantime..

get a working copy with 
```
git clone https://github.com/rob-metalinkage/django-gazetteer
pip install -e (where you put it)
```

in your 'master' django project (i.e. the one being used as the root project by your webserver):

* add 'gazetteer' to the INSTALLED_APPS  in settings.py (lots of different ways to do this - including importing a local settings file that does this - see [https://github.com/UNSW-CFRC/geonode_ext_install](https://github.com/UNSW-CFRC/geonode_ext_install)
* add     url(r"^gaz/", include('gazetteer.urls')) to urls.py
* configure settings for RDF_IO (target RDF store for links

# Initial content
The initialisation API (which should be password protected!) will set up:

1. Configuration for RDF_IO module - mappings to RDF for link building logic
1. Intial Feature Types vocabulary
1. A set of re-usable configurations for "well-known" source data - such as geonames.org

Ansible scripts [will be] provided to load "semantics" into the triple store - i.e. models need to "reason" over configured gazetteer mappings to build links dynamically to discover related data.

# Usage

## 
The basic usage pattern is

1. Geocode your data (or provide data with unique identifiers for features you would like others to use)
1. Register any namespaces (in the rdf_io/admin/namespaces) that you want to refer to with prefixes - e.g. w3w:
1. Cross reference any feature type and language codes in the data to the defaults you want to use in your gazetteer
1. Configure input source mappings
1. Harvest locations
1. Find location
1. Follow links

The [API](docs/InterimAPI.md) supports methods for these steps - however it is intended to be augmented by application integration - such as search facilities - and then use Linked Data (i.e. follow intuitive links) to find related resources. At this stage the default HTML view is simply a list of possible places a placename can be linked to. Applications can present data according to specific needs and choose what types of links to display.

## Configuration
Configuration of how a data source is loaded to the Gazetteer is done in django. */admin/gazetteer*

Configurations require the following data:

* at least one field that uses an unambiguous place name identifier (not a label) - such as acquired by geocoding with Geonames, OSM or any other source that provides a stable persistent identifier. The more other people have used this identifier the better the gazetteer will automate cross-referencing data!
* zero or more source fields (in the data to be indexed) containing natural language labels
* defaults to use (language, feature types etc)
* name of the source layer to be indexed (the name used as an identifier by the target environment - such as a geonode layer name)

### Standard configurations
some data can be rich and complex - such as an external gazetteer format such as Geonames. Re-usable configurations can be provided by adding files to the installation:

*gazetteer/fixtures/<source>_<name>_config.py* files will be loaded from /gazetteer/manage/loadconfigs

where <source> is a supported harvestable enviroment (geonode, mapstory) 

## API
The API is documented at [docs/InterimAPI](docs/InterimAPI.md)





