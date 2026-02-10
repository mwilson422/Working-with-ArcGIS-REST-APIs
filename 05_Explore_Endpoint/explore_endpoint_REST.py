import requests
import json
import time
from pprint import pprint

def explore_arcgis_endpoint(service_url):
    """
    Explore an ArcGIS REST endpoint to see metadata and sample data.
    
    Args:
        service_url: Full URL to the service layer (without /query)
                    e.g., "https://server.com/.../MapServer/2"
    """
    
    # Remove /query if present -- Only need if SELECTing data
    service_url = service_url.rstrip('/').replace('/query', '')
    
    print("=" * 70)
    print("🔍 ARCGIS REST ENDPOINT EXPLORER")
    print("=" * 70)
    print(f"\nService URL: {service_url}\n")
    
    # === 0. CHECK IF API IS ALIVE ===
    print("🏥 CHECKING API STATUS...")
    print("-" * 70)
    
    try:
        response = requests.get(service_url, params={'f': 'json'}, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API is responding")
        else:
            print(f"⚠️  API returned status code: {response.status_code}")
        
        # Show important headers
        print(f"\nImportant Headers:")
        headers_to_check = ['Content-Type', 'Server', 'X-Powered-By', 
                           'X-RateLimit-Remaining', 'X-RateLimit-Limit']
        for header in headers_to_check:
            if header in response.headers: #metadata fields sent by server stored in dictionary
                print(f"  {header}: {response.headers[header]}")
        
        # Check for rate limits
        if 'X-RateLimit-Remaining' in response.headers:
            remaining = response.headers['X-RateLimit-Remaining']
            limit = response.headers.get('X-RateLimit-Limit', 'N/A')
            print(f"\n📊 Rate Limit: {remaining} / {limit} requests remaining")
        else:
            print(f"\n📊 Rate Limit: Not specified (likely unlimited or not enforced)")
        
        print()
        
        # Be a good API citizen - brief pause
        time.sleep(0.3)
        
    except requests.exceptions.RequestException as e: # Catch all for server errors
        print(f"❌ Error connecting to API: {e}")
        return
    
    # === 1. GET METADATA ===
    print("📋 FETCHING METADATA...")
    print("-" * 70)
    
    try:
        metadata_response = requests.get(service_url, params={'f': 'json'}, timeout=10)
        metadata_response.raise_for_status()
        metadata = metadata_response.json()
        
        # Good citizen pause
        time.sleep(0.3)
        
        # Basic info
        print(f"Layer ID: {metadata.get('id', 'N/A')}") # basic syntax: dictionary.get(key, default_value)) to return value
        print(f"Layer Name: {metadata.get('name', 'N/A')}")
        print(f"Layer Type: {metadata.get('type', 'N/A')}")
        print(f"Geometry Type: {metadata.get('geometryType', 'N/A')}")
        print(f"Description: {metadata.get('description', 'N/A')}")
        
        # Record limits
        print(f"\nMax Record Count: {metadata.get('maxRecordCount', 'N/A')}")
        
        # Capabilities
        capabilities = metadata.get('advancedQueryCapabilities', {})
        print(f"\nSupports Pagination: {capabilities.get('supportsPagination', False)}")
        print(f"Supports Statistics: {capabilities.get('supportsStatistics', False)}")
        print(f"Supports Distinct: {capabilities.get('supportsDistinct', False)}")
        
        # === 2. FIELD INFORMATION ===
        print("\n" + "=" * 70)
        print("📊 FIELDS (COLUMNS)")
        print("=" * 70)
        
        fields = metadata.get('fields', [])
        print(f"\nTotal Fields: {len(fields)}\n")
        
        print(f"{'Field Name':<30} {'Type':<20} {'Alias':<30}") 
        print("-" * 80)
        
        for field in fields:
            name = field.get('name', 'N/A')
            field_type = field.get('type', 'N/A')
            alias = field.get('alias', name)
            print(f"{name:<30} {field_type:<20} {alias:<30}")
        
        # === 3. GET SAMPLE DATA (like df.head()) ===
        print("\n" + "=" * 70)
        print("🔬 SAMPLE DATA (First 5 Records)")
        print("=" * 70)
        
        query_url = f"{service_url}/query" # Now we need the /query becasue we are querying the data
        sample_params = {
            'where': '1=1',           # Get all records
            'outFields': '*',         # All fields
            'returnGeometry': 'false', # Don't need geometry for preview
            'resultRecordCount': 5,   # Just get 5 records
            'f': 'json'
        }
        
        sample_response = requests.get(query_url, params=sample_params, timeout=10)
        sample_response.raise_for_status()
        sample_data = sample_response.json()
        
        # Good citizen pause
        time.sleep(0.3)
        
        features = sample_data.get('features', [])
        
        if features:
            print(f"\nShowing {len(features)} sample record(s):\n")
            
            for i, feature in enumerate(features, 1):
                print(f"--- Record {i} ---")
                attrs = feature.get('attributes', {})
                for key, value in attrs.items():
                    # Truncate long values
                    str_value = str(value)
                    if len(str_value) > 50:
                        str_value = str_value[:47] + "..."
                    print(f"  {key}: {str_value}")
                print()
        else:
            print("No sample data available")
        

        # === 4. GET TOTAL RECORD COUNT ===
        print("=" * 70)
        print("📈 RECORD COUNT")
        print("=" * 70)
        
        try:
            count_params = {
                'where': '1=1',
                'returnCountOnly': 'true',
                'f': 'json'
            }
            
            count_response = requests.get(query_url, params=count_params, timeout=10)
            count_data = count_response.json()
            total_count = count_data.get('count', 'N/A')
            
            # Good citizen pause
            time.sleep(0.3)
            
            print(f"\nTotal Records: {total_count:,}")
            
            if isinstance(total_count, int) and total_count > metadata.get('maxRecordCount', 1000):
                print(f"⚠️  Warning: Total records exceed max record count.")
                print(f"   You will need pagination to retrieve all {total_count:,} records.")
        
        except Exception as e:
            print(f"Could not get record count: {e}")   


        # === 5. GET UNIQUE VALUES FOR KEY FIELDS ===
        print("=" * 70)
        print("🏷️  UNIQUE VALUES (for text/categorical fields)")
        print("=" * 70)
        
        # Look for likely categorical fields
        text_fields = [f['name'] for f in fields 
                      if 'String' in f.get('type', '') 
                      and f.get('name') not in ['OBJECTID', 'GlobalID', 'Shape']]
        
        if text_fields[:3]:  # Check first 3 text fields
            print("\nGetting unique values for key fields...\n")
            
            for field_name in text_fields[:3]:  # Limit to first 3
                try:
                    distinct_params = {
                        'where': '1=1',
                        'returnGeometry': 'false',
                        'returnDistinctValues': 'true',
                        'outFields': field_name,
                        'f': 'json'
                    }
                    
                    distinct_response = requests.get(query_url, params=distinct_params, timeout=10)
                    distinct_data = distinct_response.json()
                    
                    # Good citizen pause
                    time.sleep(0.3)
                    
                    unique_values = [f['attributes'][field_name] 
                                   for f in distinct_data.get('features', [])]
                    
                    print(f"{field_name}:")
                    print(f"  Unique values: {len(unique_values)}")
                    if len(unique_values) <= 20:
                        print(f"  Values: {unique_values}")
                    else:
                        print(f"  Sample values: {unique_values[:10]} ... (+ {len(unique_values)-10} more)")
                    print()
                    
                except Exception as e:
                    print(f"{field_name}: Could not retrieve ({e})\n")
        

        # === 6. TEST FILTERING ===
        print("\n" + "=" * 70)
        print("🧪 TEST FILTERING CAPABILITIES")
        print("=" * 70)
        
        # Test basic WHERE clause
        print("\nTesting basic WHERE clause...")
        test_params = {
            'where': '1=1',
            'returnCountOnly': 'true',
            'f': 'json'
        }
        
        try:
            filter_response = requests.get(query_url, params=test_params, timeout=10)
            
            # Good citizen pause
            time.sleep(0.3)
            
            if filter_response.status_code == 200:
                print("✅ Basic filtering works (WHERE 1=1)")
            else:
                print(f"❌ Filtering failed: Status {filter_response.status_code}")
        except Exception as e:
            print(f"❌ Filtering test error: {e}")
        
        # Test field filtering if we have text fields
        if text_fields:
            test_field = text_fields[0]
            print(f"\nTesting field-specific filtering ({test_field})...")
            
            # Get a sample value
            try:
                sample_params = {
                    'where': '1=1',
                    'outFields': test_field,
                    'resultRecordCount': 1,
                    'returnGeometry': 'false',
                    'f': 'json'
                }
                sample_resp = requests.get(query_url, params=sample_params, timeout=10)
                sample_val = sample_resp.json()['features'][0]['attributes'][test_field]
                
                # Good citizen pause
                time.sleep(0.3)
                
                # Test filtering by that value
                test_where = f"{test_field} = '{sample_val}'"
                filter_params = {
                    'where': test_where,
                    'returnCountOnly': 'true',
                    'f': 'json'
                }
                
                filter_resp = requests.get(query_url, params=filter_params, timeout=10)
                
                # Good citizen pause
                time.sleep(0.3)
                
                if filter_resp.status_code == 200:
                    count = filter_resp.json().get('count', 0)
                    print(f"✅ Field filtering works: WHERE {test_field} = '{sample_val}' returned {count} record(s)")
                else:
                    print(f"❌ Field filtering failed: Status {filter_resp.status_code}")
                    
            except Exception as e:
                print(f"⚠️  Could not test field filtering: {e}")
        
        # Check rate limits again after all requests
        print("\n" + "=" * 70)
        print("📊 FINAL RATE LIMIT CHECK")
        print("=" * 70)
        
        if 'X-RateLimit-Remaining' in filter_response.headers:
            remaining = filter_response.headers['X-RateLimit-Remaining']
            limit = filter_response.headers.get('X-RateLimit-Limit', 'N/A')
            print(f"\nRate Limit after exploration: {remaining} / {limit} requests remaining")
        else:
            print(f"\nNo rate limit detected for this API")
        
        print("\n" + "=" * 70)
        print("✅ Exploration complete!")
        print("=" * 70)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching metadata: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


def quick_preview(service_url, where_clause="1=1", num_records=10):
    """
    Quick preview of data matching a WHERE clause.
    
    Args:
        service_url: URL to service layer
        where_clause: SQL WHERE clause
        num_records: Number of records to show
    """
    service_url = service_url.rstrip('/').replace('/query', '')
    query_url = f"{service_url}/query"
    
    print(f"\n🔍 Quick Preview: {where_clause}")
    print("-" * 70)
    
    params = {
        'where': where_clause,
        'outFields': '*',
        'returnGeometry': 'false',
        'resultRecordCount': num_records,
        'f': 'json'
    }
    
    try:
        response = requests.get(query_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Good citizen pause
        time.sleep(0.3)
        
        features = data.get('features', [])
        print(f"Found {len(features)} record(s):\n")
        
        for i, feature in enumerate(features, 1):
            print(f"Record {i}:")
            pprint(feature.get('attributes', {}), width=100, compact=True)
            print()
            
    except Exception as e:
        print(f"❌ Error: {e}")


# === MAIN EXECUTION ===
if __name__ == "__main__":
    # Example: NSW Planning Zoning Layer
    
    print('Explore an ArcGIS REST endpoint to see metadata and sample data.')
    print('service_url: Full URL to the service layer (without /query) e.g., "https://server.com/.../MapServer/2"')

    service_url = input('Enter url: ')
    
    # Full exploration
    explore_arcgis_endpoint(service_url)
    
    # Quick preview of specific data
    # quick_preview(service_url, "LGA_NAME LIKE '%Bay%'", num_records=3)
