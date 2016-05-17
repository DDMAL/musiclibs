This folder contains static files to test against for the front and backend.

manifest.json: A valid example manifest for testing importing and searching.

collection_top.json: A valid collection containing only a nested collection.

collection_bottom.json: A valid collection containing a nested manifest.

search_result.json: Expected response for GET'ing '/?q=Maria&format=json' when only manifest.json is indexed.

search_empty.json: Expected response for empty search at URL "/?q=test&format=json"

recent_manifests.json: Output of /manifests/recent/ when manifest.json is imported
