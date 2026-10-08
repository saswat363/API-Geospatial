import os
import requests
import json

BASE_URL = "http://127.0.0.1:8080"

# 1. Create a sample KML file with a Polygon, LineString, and Point
KML_CONTENT = """<?xml version="1.0" encoding="utf-8" ?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document id="root_doc">
<Schema name="sample" id="sample">
	<SimpleField name="name" type="string"></SimpleField>
</Schema>
<Folder><name>sample</name>
  <Placemark>
	<name>poly</name>
	<ExtendedData><SchemaData schemaUrl="#sample">
		<SimpleData name="name">poly</SimpleData>
	</SchemaData></ExtendedData>
      <Polygon><outerBoundaryIs><LinearRing><coordinates>0,0 0,1 1,1 1,0 0,0</coordinates></LinearRing></outerBoundaryIs></Polygon>
  </Placemark>
  <Placemark>
	<name>line</name>
	<ExtendedData><SchemaData schemaUrl="#sample">
		<SimpleData name="name">line</SimpleData>
	</SchemaData></ExtendedData>
      <LineString><coordinates>0,0 1,1</coordinates></LineString>
  </Placemark>
  <Placemark>
	<name>point</name>
	<ExtendedData><SchemaData schemaUrl="#sample">
		<SimpleData name="name">point</SimpleData>
	</SchemaData></ExtendedData>
      <Point><coordinates>0.5,0.5</coordinates></Point>
  </Placemark>
</Folder>
</Document></kml>
"""

KML_FILE = "sample_data/test_data.kml"

def run_tests():
    print("=== LIVE API TESTS ===\n")
    
    # Setup: Create KML
    os.makedirs("sample_data", exist_ok=True)
    with open(KML_FILE, "w") as f:
        f.write(KML_CONTENT)
    print(f"Created sample file: {KML_FILE}")

    # Test 1: Upload the file
    print("\n--- Test 1: Upload File ---")
    with open(KML_FILE, "rb") as f:
        files = {"file": ("test_data.kml", f, "application/vnd.google-earth.kml+xml")}
        response = requests.post(f"{BASE_URL}/api/files/", files=files)
    
    assert response.status_code == 201, f"Upload failed: {response.text}"
    data = response.json()
    print("Upload Response:", json.dumps(data, indent=2))
    
    file_id = data["id"]
    assert data["filename"] == "test_data.kml"
    assert data["feature_count"] == 3
    assert data["status"] == "COMPLETED"
    print("✅ Upload successful!")

    # Test 2: Get File Metadata
    print("\n--- Test 2: Get File Metadata ---")
    response = requests.get(f"{BASE_URL}/api/files/{file_id}/")
    assert response.status_code == 200
    data = response.json()
    print("Metadata Response:", json.dumps(data, indent=2))
    print("✅ Metadata retrieval successful!")

    # Test 3: Get Measurements
    print("\n--- Test 3: Get Measurements ---")
    response = requests.get(f"{BASE_URL}/api/files/{file_id}/measurements/")
    assert response.status_code == 200
    data = response.json()
    
    print(f"Measurements calculated in CRS: {data['measurement_crs']}")
    print(f"Total Features Processed: {len(data['features'])}")
    
    for feature in data["features"]:
        geom_type = feature["geometry_type"]
        meas = feature["measurement"]
        unit = feature["measurement_unit"]
        status = feature["status"]
        
        print(f" - {geom_type}: Measurement = {meas} {unit if unit else ''} | Status = {status}")
        
        if geom_type == "Polygon":
            assert unit == "m²"
            assert status == "SUCCESS"
        elif geom_type == "LineString":
            assert unit == "m"
            assert status == "SUCCESS"
        elif geom_type == "Point":
            assert meas is None
            assert status == "NO_MEASUREMENT"
            
    print("✅ Measurements successful!")

    # Test 4: Invalid File Extension
    print("\n--- Test 4: Invalid Extension ---")
    files = {"file": ("test.txt", b"dummy content", "text/plain")}
    response = requests.post(f"{BASE_URL}/api/files/", files=files)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 400
    print("✅ Invalid file blocked correctly!")

if __name__ == "__main__":
    try:
        run_tests()
        print("\n🎉 ALL TESTS PASSED! API IS FULLY FUNCTIONAL.")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
