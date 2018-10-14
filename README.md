# spaceoppgave

`building_api.py`
Running this file itself with no args provides a very small functionality demo.
 
This model assumes:
- one building limits polygon
- N height plataeus, valid only if they are contiguous and cover 100% of building limits 
- validates integrity by checksumming resultant hybridized polygon features' areas against original building limit polygon area
- outputs these features as formatted JSON via `write_out(filename)`

`test_building_api.py`
Some tests compatible with pytest or unittest. running just `pytest -v` in directory will trigger them.
