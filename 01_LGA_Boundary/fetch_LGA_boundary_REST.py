import requests # third party library that must be installed
import json # built-in library

# This script is for getting a .geoJSON of an LGA boundary from the Spatial Services Spatial collaboration Portal API
# NSW Administrative Boundaries Theme - Local Government Area



# === User Settings ===

# Make sure that BASE_URL has the '/query' endpoint
BASE_URL = 'https://portal.spatial.nsw.gov.au/server/rest/services/NSW_Administrative_Boundaries_Theme/FeatureServer/8/query'

# Set WHERE for query - In this case it will be lganame 
# For this dataset the LGA name is all caps
WHERE_CLAUSE = "lganame = 'MID-WESTERN REGIONAL'"

# Output file name goes here
OUTFILE_NAME = 'MidWesternRegional_LGA.geojson'





# === Fetch Data ===

# Becasue I know this script is only going to get one feature I do not need to worry agbout paginating data.
print(f"Fetching data from ArcGIS REST API...")
print(f"Filter: {WHERE_CLAUSE}")

# Define the rest of the parameters (maybe could make these part of User settings)
params = {
        "where": WHERE_CLAUSE, # The Where parameter is user defined above
        "outFields": "*", # This will select all columns
        "f": "geojson", # This give the file format
    }

# Use Python requests.get() to retrieve information from the server, 
# if successful will return the response object '200' which is the HTTP code to indicate success

# API returns a string of GeoJSON - This is a string, not a Python object!
response = requests.get(BASE_URL, params=params)

# .raise_for_status() will return an HTTPerror if there was an error during the process
response.raise_for_status() 

# To parse the JSON string into a Python Dictionary
data = response.json()
# Need to do this to convert the JSON-formatted string  into a usable, native object within Python
# This is now a Python Dictionary and can be treated as such



# === Save to GeoJSON ===

with open(OUTFILE_NAME, 'w', encoding = 'utf-8') as f:
    json.dump(data, f, indent = 2)

print(f"💾 Saved to: {OUTFILE_NAME}")