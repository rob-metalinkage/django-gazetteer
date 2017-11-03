# django-gazetteer Harvest Configuration Guidelines

Describes the modes and options for gazetteer "harvest" process.

The gazetteer harvest does two things:
1  Records names (toponyms), alternative identifiying codes and time ranges for names found in harvested layers
1  Records links to the source data for each name and code found

However...

there is not a 1:1 relationship between records and names, or records and the underlying "location" that has many possible names

So, we could have a layer with a million roads, all in the U.S.A  - but we dont really want to build a link from every road to the location "U.S.A"

Some links should be handled at the layer metadata level - in general wherever some geographical dimension exists with nested features - i.e. unless the dataset is specifically about states, countries etc and provides alternate names for these things, then the hierarchical geographical dimension is not appropriate for gazetteer harvesting.  

Recognition of these higher-level geographies should be handled by:
*  recording the attribute containing identifying codes (eg "AZ")
*  the namespace of the codes - consistent with the namespace used in the gazetteer for these entities
*  ensuring that the matching geographies are available as a "reference layer" with a configured gazetteer harvest to capture the names (toponyms)

This is functionality to implement as a consequence:
* support importer tagging attributes as "containing geography identifiers" (modulo Ux choice of best wording) and recording the codelist (namespace). This may be supported by having reference layers record a regex to match code form, and hints for column names. 
* make sure any form of preconfigured "initiatives" can set this automatically for known data template formats
* record such relationships in the gazetteer location 
* build layer metadata in RDF to support layer-level discovery of code usage
* build and describe links to such layers as a "related data" option - so if we click on a hiking store in Arizona we could potentially search for layers about similar topics, where we can search for data related to Arizona 

Ux for these "containing relationships" will be hard to get right - as the granularity of data may vary greatly and the degree of relevance and usefulness of such links vary.



 


