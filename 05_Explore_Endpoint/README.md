# API Endpoint Explorer

## Overview
The purpose of this script is to gather information about the data accessed via ArcGIS REST API. 

The output will show:
1. ✅ **API health check** - API status code and if API is repsponding
2. ✅ **Metadata** - layer name, type, limits
3. ✅ **All field names and types** - so you know what columns exist
4. ✅ **Sample data** - like `df.head()`, shows first 5 records
5. ✅ **Total record count** - how much data exists
6. ✅ **Unique values** - for categorical fields (so you know exact spelling!)
7. ✅ **Filtering tests** - tests for filtering capabilities
8. ✅ **Rate limit check** - checks the final rate limit and remaining requests

## When to Use This
✅ Use this tool when:
- Starting work with a new API
- Debugging failed queries
- Planning a large data extraction
- Documenting an API for others
- Learning what data is available


### Common API Codes
Status codes tell us how the server handled our request:

- 200 OK: Request successful, data returned.
- 201 Created: New resource created.
- 204 No Content: Success but no data returned.
- 400 Bad Request: Invalid request.
- 401 Unauthorized: Missing or invalid API key.
- 500 Internal Server Error: Server encountered an error.
