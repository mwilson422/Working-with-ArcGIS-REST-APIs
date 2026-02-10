import json
import time
import requests
import geopandas as gpd
from shapely.geometry import shape

def get_features_by_polygon(service_url, polygon_file, spatial_relation='intersects', 
                            output_file='output.geojson', chunk_size=1000):
    """
    Query ArcGIS REST API using a polygon as spatial filter.
    
    Args:
        service_url: URL to the ArcGIS feature service query endpoint
        polygon_file: Path to GeoJSON/Shapefile/GeoPackage with the boundary polygon
        spatial_relation: 'intersects', 'contains', 'within', 'overlaps', etc.
        output_file: Where to save the results
        chunk_size: Records per request (for pagination)
    
    Returns:
        GeoJSON FeatureCollection with all features
    """
    
    print("=" * 70)
    print("🗺️  ARCGIS SPATIAL FILTER QUERY")
    print("=" * 70)
    
    # === 1. LOAD THE BOUNDARY POLYGON ===
    print(f"\n📍 Loading boundary polygon from: {polygon_file}")
    
    try:
        # Read the polygon (works with GeoJSON, Shapefile, GeoPackage)
        boundary_gdf = gpd.read_file(polygon_file)
        
        print(f"   Loaded {len(boundary_gdf)} polygon(s)")
        print(f"   CRS: {boundary_gdf.crs}")
        
        # If multiple polygons, dissolve into one
        if len(boundary_gdf) > 1:
            print("   Dissolving multiple polygons into one boundary...")
            boundary_gdf = boundary_gdf.dissolve()
        
        # Reproject to WGS84 (EPSG:4326) - ArcGIS REST expects this
        if boundary_gdf.crs != 'EPSG:4326':
            print(f"   Reprojecting from {boundary_gdf.crs} to EPSG:4326...")
            boundary_gdf = boundary_gdf.to_crs('EPSG:4326')
        
        # Get the geometry as a Shapely object
        boundary_geom = boundary_gdf.geometry.iloc[0]
        
        # Convert to GeoJSON format (what ArcGIS expects)
        boundary_json = shape(boundary_geom).__geo_interface__
        
        print("   ✅ Boundary polygon ready")
        print(f"   Bounds: {boundary_geom.bounds}")
        
    except Exception as e:
        print(f"   ❌ Error loading boundary polygon: {e}")
        return None
    
    # === 2. BUILD THE SPATIAL QUERY ===
    print("\n🔍 Building spatial query...")
    print(f"   Service: {service_url}")
    print(f"   Spatial relation: {spatial_relation}")
    
    # Convert geometry to ArcGIS JSON format
    geometry_filter = json.dumps(boundary_json)
    
    # Base parameters
    base_params = {
        'geometry': geometry_filter,
        'geometryType': 'esriGeometryPolygon',
        'spatialRel': f'esriSpatialRel{spatial_relation.capitalize()}',
        'inSR': '4326',         # Input spatial reference (WGS84)
        'outFields': '*',       # Get all fields
        'returnGeometry': 'true',
        'f': 'geojson'          # Output format
    }
    
    # === 3. CHECK IF PAGINATION IS NEEDED ===
    print("\n📊 Checking how many features match...")
    
    count_params = base_params.copy()
    count_params.update({
        'returnCountOnly': 'true',
        'f': 'json'
    })
    
    try:
        count_response = requests.get(service_url, params=count_params, timeout=30)
        count_response.raise_for_status()
        total_count = count_response.json().get('count', 0)
        
        print(f"   ✅ Found {total_count:,} features within boundary")
        
        time.sleep(0.3)  # Good citizen pause
        
    except Exception as e:
        print(f"   ⚠️  Could not get count: {e}")
        total_count = None
    
    # === 4. FETCH THE DATA (with pagination if needed) ===
    print("\n📥 Fetching features...")
    
    all_features = []
    offset = 0
    
    # Determine if we need pagination
    needs_pagination = total_count and total_count > chunk_size
    
    if needs_pagination:
        print(f"   Using pagination (chunks of {chunk_size})")
    
    while True:
        # Build request parameters
        params = base_params.copy()
        
        if needs_pagination:
            params.update({
                'resultOffset': offset,
                'resultRecordCount': chunk_size
            })
        
        try:
            # Make the request
            response = requests.get(service_url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            # Extract features
            features = data.get('features', [])
            
            if not features:
                print("   ✅ No more features")
                break
            
            all_features.extend(features)
            print(f"   📦 Fetched {len(features)} features (total: {len(all_features)})")
            
            # If not using pagination, we're done after first request
            if not needs_pagination:
                break
            
            # Check if we got fewer features than requested (last page)
            if len(features) < chunk_size:
                print("   ✅ Reached last page")
                break
            
            offset += chunk_size
            time.sleep(0.5)  # Good citizen pause between requests
            
        except Exception as e:
            print(f"   ❌ Error fetching data: {e}")
            break
    
    # === 5. SAVE THE RESULTS ===
    if all_features:
        print(f"\n💾 Saving {len(all_features)} features to {output_file}")
        
        output_geojson = {
            "type": "FeatureCollection",
            "features": all_features
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_geojson, f, indent=2, ensure_ascii=False)
        
        print("   ✅ Saved successfully")
        
        # Show sample properties
        if all_features:
            print("\n📋 Sample feature properties:")
            sample_props = all_features[0].get('properties', {})
            for key, value in list(sample_props.items())[:5]:
                print(f"   {key}: {value}")
        
        return output_geojson
    else:
        print("\n⚠️  No features found within the boundary")
        return None


def quick_spatial_query(service_url, polygon_file, output_file='output.geojson'):
    """
    Simplified version for quick queries (no pagination).
    
    Args:
        service_url: ArcGIS REST query endpoint
        polygon_file: Path to boundary polygon file
        output_file: Where to save results
    """
    
    print(f"Loading boundary from: {polygon_file}")
    
    # Load and prepare polygon
    boundary_gdf = gpd.read_file(polygon_file)
    
    if len(boundary_gdf) > 1:
        boundary_gdf = boundary_gdf.dissolve()
    
    if boundary_gdf.crs != 'EPSG:4326':
        boundary_gdf = boundary_gdf.to_crs('EPSG:4326')
    
    boundary_geom = boundary_gdf.geometry.iloc[0]
    boundary_json = json.dumps(shape(boundary_geom).__geo_interface__)
    
    # Query parameters
    params = {
        'geometry': boundary_json,
        'geometryType': 'esriGeometryPolygon',
        'spatialRel': 'esriSpatialRelIntersects',
        'inSR': '4326',
        'outFields': '*',
        'returnGeometry': 'true',
        'f': 'geojson'
    }
    
    print("Querying service...")
    response = requests.get(service_url, params=params, timeout=60)
    response.raise_for_status()
    
    geojson = response.json()
    num_features = len(geojson.get('features', []))
    
    print(f"Found {num_features} features")
    
    # Save
    with open(output_file, 'w') as f:
        json.dump(geojson, f, indent=2)
    
    print(f"Saved to: {output_file}")
    
    return geojson


# === USAGE ===
if __name__ == "__main__":
    
    # Example 1: Full version with pagination
    service_url = "https://portal.spatial.nsw.gov.au/server/rest/services/NSW_Land_Parcel_Property_Theme/FeatureServer/8/query"
    boundary_file = "bayside_lga_boundary.geojson"
    
    results = get_features_by_polygon(
        service_url=service_url,
        polygon_file=boundary_file,
        spatial_relation='intersects',  # or 'contains', 'within', etc. 
        output_file='bayside_lots.geojson',
        chunk_size=2000
    )
    
    # Example 2: Quick version (no pagination)
    # quick_spatial_query(
    #     service_url="https://example.com/.../query",
    #     polygon_file="boundary.geojson",
    #     output_file="lots.geojson"
    # )
