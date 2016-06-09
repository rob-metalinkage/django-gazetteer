# django-gazetteer

Gazetteer functionality implemented in Django

Gazetteer supports harvesting multiple alternative names and codes for "features" from source data sets
	- comes with default handlers for a geonode context loaded to a postgis data store
	- can be extended to provide equivalent functionality to other data sources.

Uses django-skosxl to handle field and value-mappings from input data.
If configured it uses django-rdf-io to register such links to an RDF environment - using VoiD Linkset descriptions


# Design Goals

1 Gazetteer collates alternative place names for a single feature from multiple sources. 
1 Designed to allow post-hoc reconciliation of equivalent features, but to be able to respect any unique identifying codes in any namespace - i.e. two features form different sources that use the same external identifier are assumed equivalent.
1 Multi-lingual and temporal name validity support.
1 Support null as unknowns for language, status and temporal validity range
1 By remembering which resource each name was found, the gazetteer provides a hub function in a Linked Data view of such resources. 
1 Extensible to handle alternative enviroments
1 Content is django models so that users can interact to reconcile and extend data in UI workflows as required.

## installation

get a working copy with 
git clone https://github.com/rob-metalinkage/django-gazetteer
pip install -e (where you put it)

in your master django project:
* add 'gazetteer' to the INSTALLED_APPS  in settings.py
* add     url(r"^gaz/", include('gazetteer.urls')) to urls.py

## Usage
TODO

### Mapping syntax

 
## Status: 
in development - being ported from an embedded app to a standalone module

todo:


## API
