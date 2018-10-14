# spaceoppgave

*requires `geopandas` and `shapely`*

`building_api.py`:
Running this file itself with no args provides a very small functionality demo. Must have the two demo data sources in directory (`heights.json` and `limits.json`)
 
This model:
- assumes there is only one building-limits polygon
- assumes N height plataeus, valid only if they are contiguous and cover 100% of building limits 
- validates integrity by checksumming resultant hybridized polygon features' areas against original building limit polygon area
- uses this validation as a means to save a running history of last-known-good-featuresets and therefore a conflict resolution system when either feature is being changed 
- outputs these features as formatted JSON via `write_out(filename)`

`test_building_api.py`:
Some tests compatible with pytest or unittest. running just `pytest -v` in directory will trigger them.
