## Overview
This script will fetch ArcGIS REST data with a spatial filter as opposed to a filter by attribute. 

#### Different Input Formats Supported
- ✅ GeoJSON (.geojson)
- ✅ Shapefile (.shp)
- ✅ GeoPackage (.gpkg)
- ✅ Any format GeoPandas can read

## What the Script Does

1. Loads your boundary polygon (from GeoJSON, Shapefile, or GeoPackage)
2. Reprojects to WGS84 (EPSG:4326) - required by ArcGIS REST
3. Converts to ArcGIS JSON format - the format the API expects
4. Queries the service with the polygon as a spatial filter
5. Handles pagination automatically if there are many lots
6. Saves results as GeoJSON

### User inputs:
1. Service URL
2. Boundary file
3. Spatial relationship
4. Output file name


```python
# Your inputs
service_url = "https://server.com/.../Cadastre/Lots/MapServer/0/query" # API url
boundary_file = "bayside_boundary.geojson"  # The LGA polygon


results = get_features_by_polygon(
    service_url=service_url,
    polygon_file=boundary_file,
    spatial_relation='intersects', # Spatial relationship (see below)
    output_file='bayside_lots.geojson' # Output file name
)
```

#### Spatial Relationships
```python
spatial_relation='intersects'  # Returns features that share any space with the boundary polygon (most common)
spatial_relation='within'      # Only returns features where the feature is completely inside the boundary (inverse of contains, A contains B = B within A)
spatial_relation='contains'    # Only returns features that are completely inside the boundary polygon
spatial_relation='touches'     # Returns features that share a boundary but don't overlap 
spatial_relation='overlaps'    # Returns features that partially overlap (some inside, some outside)
spatial_relation='crosses'     # Returns lines that cross through the polygon (when working with linear features)

```

