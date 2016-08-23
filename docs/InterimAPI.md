# django-gazetteer Interim API docs

Describes the Gazetteer module Web API. These are interim docs possibly to be replaced by an automated document generation allowing gazetteer API dcescription to be automatically included in a master project. (This will need to wait until till the target platform for driving Use Case, geonode,  moves to latest version of django..

# Search 
`/location/find?{params}`

params are:
* _name_ - match a name exactly (case insensitive)
* _namestart_ - match the start of a name (case insensitive)
* _lang_ - match a name for a specific language code
* _code_ - match a code-form (e.g. an identifier from an external data source)
* _namespace_ - match a code from a specific namespace only
* _max_=M - show first M results
* _page_=N - show page N of results (max defaults to 100)

_name_ may be a literal 
`/gazetteer/location/find?namestart=هولندا`
or the equivalent in 'escaped unicode'
`/gazetteer/location/find?namestart=\u0647\u0648\u0644\u0646\u062f\u0627`

results are in JSON:
```
{
	count: 81,
	itemsPerPage: 100,
	page: 0,
	latitude: 17.078,
	type: "ADMIN",
	results: [
		{
		locid: 520,
		longitude: -61.783,
		defaultName: "Antigua and Barbuda",
		names: [
			{
			namespace: "http://mapstory.org/id/countries/iso3",
			name: "ATG"
			},
			{
			name: "Antigua and Barbuda",
			language: "en"
			}
		]
	]
}
```

# Access a specific location

## Access using internal id
`/location/{id}`

## Access using a unique code
`/location/code?code={code}&namespace={namespaceURI}`
Note if namespaceURI is missing, code may be a full URI

## Get linked data view, include references to sources
`rdf_io/to_rdf/location/id/{id}`


# Configuration

Configurations are loaded using the admin interface

`/admin/gazetteer/gazsourceconfig/`

and bound to particular data sources using

`/admin/gazetteer/gazsource/`

## Load pre-defined configurations

Pre-defined harvest configurations for key resources are provided and may be loaded (idempotently) using
`/manage/loadconfigs`

# Harvest
`/gazetteer/harvest/{source_id}`

arguments:
* _n_=N - number of source records to process

reports the number of features processed and the number of new locations inserted.

# Maintenance

These commands are mainly used as a convenience for developers and system administrators
## Remove a data source references
`/manage/flush/{source_id}`
Removes all references from names found to the designated data source. If a Location has no other data sources referenced then it will removed.
