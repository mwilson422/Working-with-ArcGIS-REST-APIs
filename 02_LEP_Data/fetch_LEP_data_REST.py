import requests
import json
import time

def fetch_arcgis_features(base_url, where_clause, max_retries=3):
    """
    Fetch all features from ArcGIS REST endpoint with pagination.
    
    Args:
        base_url: ArcGIS REST service URL
        where_clause: SQL WHERE clause for filtering
        max_retries: Number of retry attempts on failure
    
    Returns:
        GeoJSON FeatureCollection with all features
    """
    
    all_features = []
    offset = 0
    page_size = 1000  # Common max for ArcGIS servers
    
    print(f"Fetching data from: {base_url}")
    print(f"Filter: {where_clause}")
    print("-" * 50)
    
    # First, check if server supports pagination
    supports_pagination = check_pagination_support(base_url)
    
    if supports_pagination:
        print("✓ Server supports pagination")
        all_features = fetch_with_pagination(base_url, where_clause, page_size, max_retries)
    else:
        print("⚠ Server doesn't support pagination, trying single request")
        all_features = fetch_single_request(base_url, where_clause, max_retries)
    
    # Create GeoJSON FeatureCollection
    geojson = {
        "type": "FeatureCollection",
        "features": all_features
    }
    
    print("-" * 50)
    print(f"✓ Total features fetched: {len(all_features)}")
    
    return geojson


def check_pagination_support(base_url):
    """Check if the ArcGIS server supports pagination."""
    try:
        # Remove /query if it's in the URL
        service_url = base_url.replace('/query', '')
        
        params = {
            'f': 'json'
        }
        response = requests.get(service_url, params=params, timeout=10)
        response.raise_for_status()
        metadata = response.json()
        
        # Check for pagination capabilities
        return metadata.get('advancedQueryCapabilities', {}).get('supportsPagination', False)
    except:
        return False


def fetch_with_pagination(base_url, where_clause, page_size, max_retries):
    """Fetch features using pagination (resultOffset/resultRecordCount)."""
    all_features = []
    offset = 0
    
    while True:
        params = {
            'where': where_clause,
            'outFields': '*',
            'f': 'geojson',
            'resultOffset': offset,
            'resultRecordCount': page_size,
            'returnGeometry': 'true'
        }
        
        print(f"Fetching records {offset} to {offset + page_size}...", end=" ")
        
        # Retry logic
        for attempt in range(max_retries):
            try:
                response = requests.get(base_url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Retry {attempt + 1}/{max_retries}...", end=" ")
                    time.sleep(2)
                else:
                    print(f"✗ Failed after {max_retries} attempts")
                    raise Exception(f"Failed to fetch data: {str(e)}")
        
        # Extract features
        features = data.get('features', [])
        
        if not features:
            print("✓ No more records")
            break
        
        all_features.extend(features)
        print(f"✓ Got {len(features)} records")
        
        # Check if we got fewer records than requested (last page)
        if len(features) < page_size:
            break
        
        offset += page_size
        time.sleep(0.5)  # Be nice to the server
    
    return all_features


def fetch_single_request(base_url, where_clause, max_retries):
    """Fetch features in a single request (fallback method)."""
    params = {
        'where': where_clause,
        'outFields': '*',
        'f': 'geojson',
        'returnGeometry': 'true'
    }
    
    print("Attempting single request...", end=" ")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(base_url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            features = data.get('features', [])
            print(f"✓ Got {len(features)} records")
            
            # Check if we might have hit the limit
            if len(features) >= 1000:
                print("⚠ Warning: May have hit record limit (1000+). Some data might be missing.")
            
            return features
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Retry {attempt + 1}/{max_retries}...", end=" ")
                time.sleep(2)
            else:
                raise Exception(f"Failed to fetch data: {str(e)}")


def save_geojson(geojson_data, filename):
    """Save GeoJSON to file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(geojson_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved to: {filename}")


# Main execution
if __name__ == "__main__":

    # ========== User Set Parameters ==========
    # ArcGIS REST endpoint url
    url = "https://mapprod3.environment.nsw.gov.au/arcgis/rest/services/Planning/EPI_Primary_Planning_Layers/MapServer/2/query"
    
    # Filter by LGA_NAME
    where = "EPI_NAME = 'Mid-Western Regional Local Environmental Plan 2012'"
    
    try:
        # Fetch all data
        geojson_data = fetch_arcgis_features(url, where)
        
        # Save to file
        output_file = "MidWestern_LandZone.geojson"
        save_geojson(geojson_data, output_file)
        
        # Print summary
        print("\n" + "=" * 50)
        print("Summary:")
        print(f"  Features: {len(geojson_data['features'])}")
        print(f"  Output: {output_file}")
        
        # Print first feature as sample
        if geojson_data['features']:
            print("\nSample feature properties:")
            props = geojson_data['features'][0].get('properties', {})
            for key, value in list(props.items())[:5]:
                print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
