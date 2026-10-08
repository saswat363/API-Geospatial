import os
import io
import zipfile
import tempfile
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Basic endpoint tests
# ---------------------------------------------------------------------------

def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307


def test_upload_invalid_extension():
    files = {'file': ('test.txt', b"dummy content", 'text/plain')}
    response = client.post("/api/files/", files=files)
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_missing_file():
    response = client.post("/api/files/")
    assert response.status_code == 422  # Unprocessable Entity (missing field)


def test_get_invalid_file_id():
    response = client.get("/api/files/invalid-id/")
    assert response.status_code == 404


def test_get_invalid_file_measurements():
    response = client.get("/api/files/invalid-id/measurements/")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# KML upload — covers Polygon, LineString and Point in a single file
# ---------------------------------------------------------------------------

KML_CONTENT = """<?xml version="1.0" encoding="utf-8" ?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document id="root_doc">
<Folder><name>test</name>
  <Placemark>
    <name>poly</name>
    <Polygon><outerBoundaryIs><LinearRing>
      <coordinates>77.5,12.9 77.5,13.0 77.6,13.0 77.6,12.9 77.5,12.9</coordinates>
    </LinearRing></outerBoundaryIs></Polygon>
  </Placemark>
  <Placemark>
    <name>line</name>
    <LineString><coordinates>77.5,12.9 77.6,13.0</coordinates></LineString>
  </Placemark>
  <Placemark>
    <name>point</name>
    <Point><coordinates>77.55,12.95</coordinates></Point>
  </Placemark>
</Folder>
</Document></kml>
"""


def test_kml_upload_and_feature_count():
    """KML with 3 features should upload and report feature_count=3."""
    kml_bytes = KML_CONTENT.encode("utf-8")
    files = {'file': ('survey.kml', kml_bytes, 'application/vnd.google-earth.kml+xml')}
    response = client.post("/api/files/", files=files)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["filename"] == "survey.kml"
    assert data["feature_count"] == 3
    assert data["status"] == "COMPLETED"
    assert data["crs"] is not None


def test_kml_measurements_polygon_area():
    """Polygon in EPSG:4326 must be transformed to UTM and return area in m²."""
    kml_bytes = KML_CONTENT.encode("utf-8")
    files = {'file': ('survey.kml', kml_bytes, 'application/vnd.google-earth.kml+xml')}
    resp = client.post("/api/files/", files=files)
    file_id = resp.json()["id"]

    resp = client.get(f"/api/files/{file_id}/measurements/")
    assert resp.status_code == 200
    data = resp.json()

    # measurement CRS must be a UTM zone (EPSG:326xx or 327xx)
    assert data["measurement_crs"].startswith("EPSG:326") or \
           data["measurement_crs"].startswith("EPSG:327"), \
           f"Expected UTM, got {data['measurement_crs']}"

    poly = next(f for f in data["features"] if f["geometry_type"] == "Polygon")
    assert poly["status"] == "SUCCESS"
    assert poly["measurement_unit"] == "m\u00b2"
    assert poly["measurement"] > 0, "Polygon area must be > 0"


def test_kml_measurements_linestring_length():
    """LineString in EPSG:4326 must return length in metres after UTM projection."""
    kml_bytes = KML_CONTENT.encode("utf-8")
    files = {'file': ('survey.kml', kml_bytes, 'application/vnd.google-earth.kml+xml')}
    resp = client.post("/api/files/", files=files)
    file_id = resp.json()["id"]

    resp = client.get(f"/api/files/{file_id}/measurements/")
    line = next(f for f in resp.json()["features"] if f["geometry_type"] == "LineString")
    assert line["status"] == "SUCCESS"
    assert line["measurement_unit"] == "m"
    assert line["measurement"] > 0, "LineString length must be > 0"


def test_kml_measurements_point_no_measurement():
    """Point features must return measurement=None and status=NO_MEASUREMENT."""
    kml_bytes = KML_CONTENT.encode("utf-8")
    files = {'file': ('survey.kml', kml_bytes, 'application/vnd.google-earth.kml+xml')}
    resp = client.post("/api/files/", files=files)
    file_id = resp.json()["id"]

    resp = client.get(f"/api/files/{file_id}/measurements/")
    point = next(f for f in resp.json()["features"] if f["geometry_type"] == "Point")
    assert point["measurement"] is None
    assert point["measurement_unit"] is None
    assert point["status"] == "NO_MEASUREMENT"


def test_epsg4326_transforms_to_utm():
    """EPSG:4326 source must always produce a UTM measurement_crs, never itself."""
    kml_bytes = KML_CONTENT.encode("utf-8")
    files = {'file': ('survey.kml', kml_bytes, 'application/vnd.google-earth.kml+xml')}
    resp = client.post("/api/files/", files=files)
    file_id = resp.json()["id"]

    resp = client.get(f"/api/files/{file_id}/measurements/")
    data = resp.json()
    assert data["crs"] is not None
    assert "4326" in data["crs"]
    # The measurement CRS must NOT be geographic (must be a projected UTM zone)
    assert "4326" not in data["measurement_crs"], \
        "Measurements must NOT be taken in EPSG:4326"


# ---------------------------------------------------------------------------
# ZIP Shapefile tests
# ---------------------------------------------------------------------------

def _make_polygon_zip() -> bytes:
    """Create an in-memory ZIP with a valid single-geometry-type Polygon shapefile."""
    import geopandas as gpd
    from shapely.geometry import Polygon

    poly = Polygon([(77.5, 12.9), (77.5, 13.0), (77.6, 13.0), (77.6, 12.9)])
    gdf = gpd.GeoDataFrame({'name': ['area_a'], 'geometry': [poly]}, crs="EPSG:4326")

    with tempfile.TemporaryDirectory() as tmp:
        shp_path = os.path.join(tmp, "data.shp")
        gdf.to_file(shp_path)

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w') as zf:
            for ext in ['.shp', '.shx', '.dbf', '.prj', '.cpg']:
                fp = os.path.join(tmp, f"data{ext}")
                if os.path.exists(fp):
                    zf.write(fp, arcname=f"data{ext}")
        return buf.getvalue()


def test_valid_zip_upload():
    """Valid ZIP Shapefile must upload and return 201 with correct metadata."""
    try:
        zip_bytes = _make_polygon_zip()
    except Exception as exc:
        pytest.skip(f"Could not create test shapefile: {exc}")

    files = {'file': ('data.zip', zip_bytes, 'application/zip')}
    response = client.post("/api/files/", files=files)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["feature_count"] == 1
    assert data["status"] == "COMPLETED"
    assert "EPSG:4326" in data["crs"].upper()


def test_valid_zip_polygon_measurement():
    """Polygon from ZIP Shapefile must have area > 0 in m²."""
    try:
        zip_bytes = _make_polygon_zip()
    except Exception as exc:
        pytest.skip(f"Could not create test shapefile: {exc}")

    files = {'file': ('data.zip', zip_bytes, 'application/zip')}
    resp = client.post("/api/files/", files=files)
    file_id = resp.json()["id"]

    resp = client.get(f"/api/files/{file_id}/measurements/")
    assert resp.status_code == 200
    feat = resp.json()["features"][0]
    assert feat["geometry_type"] == "Polygon"
    assert feat["measurement"] > 0
    assert feat["measurement_unit"] == "m\u00b2"
    assert feat["status"] == "SUCCESS"


def test_zip_without_shapefile():
    """ZIP with no .shp must return 400."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_path = os.path.join(tmp_dir, "empty.zip")
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("test.txt", "hello")

        with open(zip_path, "rb") as f:
            files = {'file': ('empty.zip', f, 'application/zip')}
            response = client.post("/api/files/", files=files)

    assert response.status_code == 400
    assert "ZIP does not contain a .shp file" in response.json()["detail"]


def test_zip_path_traversal_rejected():
    """ZIP containing a path traversal entry must return 400."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zf:
        zf.writestr("../evil.shp", "fake shapefile content")
    buf.seek(0)
    files = {'file': ('evil.zip', buf.read(), 'application/zip')}
    response = client.post("/api/files/", files=files)
    assert response.status_code == 400
    assert "Dangerous file path" in response.json()["detail"]
