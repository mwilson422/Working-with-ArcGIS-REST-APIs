# Project Workflow
1. Fetch LGA Boundary from Spatial Services Spatial Collaboration Portal
    - Python script that takes a LGA name as input and returns the LGA boundary as a GeoJSON
2. Get Evironmental Planning Instrument - Land Zoning Data from SEED (Sharing and Enabling Environmental Data in NSW)
    - Dataset will be larger than for one LGA polygon and so need to have pagination abilities in the script to get this data.
    - Select data based on LGA name and returns data in GeoJSON
3. LEP layers in GeoJSON do not neccessarily have styling associated with them and Land Zoning uses specific styling for different zones so investigate different ways of handling that.
    - The following are provided by SEED:
        - ESRI Layer file (stores symbology)
        - ESRI Style file (can be used to apply symbology to the layer)
        - XLSX with RGB and HEX codes for different zones
        - The REST Services Directory provides Drawing Info in the metadata
4. Get Lot Boundaries from Spatial Services Spatial Collaboration Portal
    - This layer does not have a field that makes it easy to only get data for an LGA so I want to be able to use the GeoJSON acquired earlier of the LGA boundary polygon as a spatial filter.
5. Create a script that will investigate the REST API enpoints.
    - Checks that API is alive
    - Get the metadata
    - Get some sample data
    - Get total record count
    - Get unique values 
    - Test filtering
    