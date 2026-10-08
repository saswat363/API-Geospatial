<div align="center">

# 🛰️ Geospatial File Measurement API

### A production-quality FastAPI backend for processing geospatial files and computing accurate spatial measurements.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![GeoPandas](https://img.shields.io/badge/GeoPandas-1.2%2B-139C5A?style=for-the-badge)](https://geopandas.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-14%20Passing-brightgreen?style=for-the-badge&logo=pytest)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

</div>

---

## 📌 Overview

The **Geospatial File Measurement API** is a backend service built with **FastAPI** that accepts geospatial files in **KML** or **ZIP (Shapefile)** format, extracts every geographic feature, and computes accurate spatial measurements — area in square metres (m²) for polygons and length in metres (m) for lines.

The key engineering challenge this project solves is **CRS (Coordinate Reference System) handling**: geographic data is often stored in EPSG:4326 (latitude/longitude in degrees), where directly computing area or length gives meaningless results. This API automatically detects the source CRS, determines the correct UTM projection zone from the dataset's centroid, transforms the geometries, and then performs precise metric-unit measurements.

This project was built as a technical assignment for the **Aereo** internship application — demonstrating skills in:
- FastAPI backend architecture
- REST API design
- Geospatial data processing (GeoPandas, Shapely, PyProj)
- CRS transformation and UTM zone selection
- Security-aware file handling
- Automated testing with pytest
- Docker containerization

---

## ✨ Features

| Feature | Details |
|---|---|
| 📁 **KML Upload** | Accepts `.kml` files with mixed geometry types |
| 🗜️ **ZIP Shapefile Upload** | Accepts `.zip` archives containing valid Shapefiles |
| 🔍 **Feature Extraction** | Reads all features, geometry types, and attributes |
| 📐 **Polygon Area** | Accurate area in **m²** via UTM projection |
| 📏 **LineString Length** | Accurate length in **m** via UTM projection |
| 🔄 **Auto CRS Transformation** | Detects geographic CRS → selects UTM zone → transforms |
| 🌍 **Global UTM Support** | Works for any dataset worldwide (not hard-coded to any location) |
| 🛡️ **Security** | ZIP path traversal prevention, 50 MB limit, UUID filenames |
| ❌ **Graceful Error Handling** | Clean JSON errors, no stack traces exposed |
| 📝 **Swagger UI** | Auto-generated interactive API docs at `/docs` |
| ✅ **14 pytest Tests** | 0 skipped, 0 warnings — full scenario coverage |
| 🐳 **Docker Ready** | `docker compose up --build` and you're running |

---

## 🧰 Tech Stack

| Library | Version | Purpose |
|---|---|---|
| **Python** | 3.11+ | Core language |
| **FastAPI** | 0.100+ | API framework — async, Pydantic-native, auto-docs |
| **Uvicorn** | 0.23+ | ASGI server |
| **GeoPandas** | 1.2+ | Reading KML and Shapefile formats, CRS operations |
| **Shapely** | 2.0+ | Geometry operations (area, length, type detection) |
| **PyProj** | 3.6+ | CRS definitions and coordinate transformations |
| **Fiona** | 1.9+ | Low-level geospatial file I/O driver |
| **Pydantic** | 2.0+ | Request/response validation and serialization |
| **python-multipart** | 0.0.6+ | Multipart file upload parsing |
| **pytest** | 7.4+ | Testing framework |
| **httpx** | 0.25+ | Async HTTP client for tests |

---

## 📁 Project Structure

```text
geospatial-measurement-api/
│
├── app/
│   ├── __init__.py
│   ├── main.py                    # App entry point — registers routers
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── files.py               # HTTP endpoints (POST /upload, GET /info, GET /measurements)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── file_processor.py      # Orchestration: save → parse → cache → return
│   │   ├── crs_handler.py         # CRS detection + UTM zone selection
│   │   └── measurement.py         # Pure geometry measurement logic
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── file_schema.py         # Pydantic response models
│   │
│   └── utils/
│       ├── __init__.py
│       └── validators.py          # File extension + ZIP safety validation
│
├── uploads/                       # Uploaded files stored here (UUID-named)
│   └── .gitkeep
│
├── tests/
│   ├── __init__.py
│   └── test_api.py                # 14 pytest tests — all scenarios covered
│
├── sample_data/
│   └── README.md                  # Instructions for sample test files
│
├── requirements.txt
├── .gitignore
├── README.md
├── Dockerfile
└── docker-compose.yml
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.11+
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/saswat363/API-Geospatial.git
cd API-Geospatial
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Windows (PowerShell):
venv\Scripts\activate

# Windows (Git Bash):
source venv/Scripts/activate

# Linux / macOS:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Server

```bash
uvicorn app.main:app --reload
```

The server starts at: **http://localhost:8000**

> To use a different port (e.g., if 8000 is blocked):
> ```bash
> uvicorn app.main:app --reload --port 8080
> ```

---

## 📖 Swagger / OpenAPI Docs

Interactive API documentation is auto-generated by FastAPI:

```
http://localhost:8000/docs
```

ReDoc alternative:
```
http://localhost:8000/redoc
```

---

## 📡 API Endpoints

### `POST /api/files/`
Upload a geospatial file (`.kml` or `.zip` Shapefile).

**Request:** `multipart/form-data` with field `file`

**Response:** `HTTP 201 Created`
```json
{
  "id": "b61e30a4-96e2-4434-b43d-0c5322ed903c",
  "filename": "survey.kml",
  "feature_count": 3,
  "crs": "EPSG:4326",
  "status": "COMPLETED"
}
```

**curl example:**
```bash
curl -X POST "http://localhost:8000/api/files/" \
  -H "accept: application/json" \
  -F "file=@survey.kml"
```

---

### `GET /api/files/{id}/`
Retrieve metadata for a previously uploaded file.

**Response:** `HTTP 200 OK`
```json
{
  "id": "b61e30a4-96e2-4434-b43d-0c5322ed903c",
  "filename": "survey.kml",
  "feature_count": 3,
  "crs": "EPSG:4326",
  "status": "COMPLETED"
}
```

**curl example:**
```bash
curl "http://localhost:8000/api/files/b61e30a4-96e2-4434-b43d-0c5322ed903c/"
```

---

### `GET /api/files/{id}/measurements/`
Retrieve per-feature spatial measurements.

**Response:** `HTTP 200 OK`
```json
{
  "file_id": "b61e30a4-96e2-4434-b43d-0c5322ed903c",
  "filename": "survey.kml",
  "crs": "EPSG:4326",
  "measurement_crs": "EPSG:32643",
  "features": [
    {
      "feature_id": 0,
      "geometry_type": "Polygon",
      "geometry": { "type": "Polygon", "coordinates": [[...]] },
      "properties": { "name": "Area A" },
      "measurement": 125034.52,
      "measurement_unit": "m²",
      "status": "SUCCESS"
    },
    {
      "feature_id": 1,
      "geometry_type": "LineString",
      "geometry": { "type": "LineString", "coordinates": [[...]] },
      "properties": { "name": "Road A" },
      "measurement": 1532.41,
      "measurement_unit": "m",
      "status": "SUCCESS"
    },
    {
      "feature_id": 2,
      "geometry_type": "Point",
      "geometry": { "type": "Point", "coordinates": [77.55, 12.95] },
      "properties": { "name": "Location A" },
      "measurement": null,
      "measurement_unit": null,
      "status": "NO_MEASUREMENT"
    }
  ]
}
```

**curl example:**
```bash
curl "http://localhost:8000/api/files/b61e30a4-96e2-4434-b43d-0c5322ed903c/measurements/"
```

---

## 🗺️ CRS Handling Strategy

This is the most critical engineering aspect of the project.

### Why EPSG:4326 cannot be used directly for measurements

EPSG:4326 (WGS84) stores coordinates as **latitude/longitude in degrees**. When you call `geometry.area` or `geometry.length` on degree-based coordinates, the result is in **square degrees** or **degrees**, which is not meaningful for real-world measurements.

**Example of the wrong approach (NEVER done in this API):**
```python
# WRONG — produces result in degrees, not metres
area_in_degrees = geometry.area  # e.g. 0.0001° — meaningless
```

### The correct approach used in this API

```
Source File (EPSG:4326)
        ↓
Detect CRS — is it geographic or projected?
        ↓ (geographic)
Compute dataset centroid (lon, lat)
        ↓
Determine UTM Zone from longitude:
  zone = floor((lon + 180) / 6) % 60 + 1
        ↓
Select hemisphere:
  lat ≥ 0 → Northern: EPSG:326XX
  lat < 0 → Southern: EPSG:327XX
        ↓
Transform geometries: gdf.to_crs("EPSG:326XX")
        ↓
Measure on projected geometry:
  Polygon  → geometry.area   (m²)
  Line     → geometry.length (m)
```

**Example for a dataset centred near Bengaluru (lon=77.5, lat=12.9):**
```
UTM Zone = floor((77.5 + 180) / 6) % 60 + 1 = 43
Hemisphere = Northern (lat > 0)
Measurement CRS = EPSG:32643
```

> The API is not hard-coded to any location. It works globally for any dataset.

### Edge Cases Handled

| Scenario | Behaviour |
|---|---|
| CRS is already projected | Use the existing projected CRS directly |
| CRS is missing entirely | Return `status: "MISSING_CRS"` per feature |
| All geometries are empty/invalid | Fall back to EPSG:3857 |
| Dataset spans multiple UTM zones | Uses centroid — documents this as a limitation |

---

## 📐 Measurement Rules

| Geometry Type | Measurement | Unit | Status |
|---|---|---|---|
| `Polygon` | Area | m² | `SUCCESS` |
| `MultiPolygon` | Total area | m² | `SUCCESS` |
| `LineString` | Length | m | `SUCCESS` |
| `MultiLineString` | Total length | m | `SUCCESS` |
| `Point` | None | — | `NO_MEASUREMENT` |
| `MultiPoint` | None | — | `NO_MEASUREMENT` |
| `GeometryCollection` | None | — | `UNSUPPORTED_GEOMETRY` |
| Empty geometry | None | — | `NO_MEASUREMENT` |

A single feature returning `NO_MEASUREMENT` or `UNSUPPORTED_GEOMETRY` **does not fail the request** — all other features are still processed successfully.

---

## 🛡️ Security

| Threat | Mitigation |
|---|---|
| Invalid file types | Extension whitelist (`.kml`, `.zip` only) |
| Oversized files | 50 MB hard limit — returns HTTP 413 |
| ZIP path traversal | Pre-extraction scan for `../`, `/`, `\` prefixes |
| Malicious filenames | UUID-based storage — uploaded filename is never used for disk paths |
| Corrupt geospatial files | Try/except wrapping all GeoPandas read calls → HTTP 400 |
| Server stack trace exposure | All exceptions caught and returned as clean JSON |

---

## ❌ Error Reference

| HTTP Code | Trigger |
|---|---|
| `400` | Invalid file extension |
| `400` | Corrupt or unreadable geospatial file |
| `400` | ZIP contains no `.shp` file |
| `400` | Dangerous path found inside ZIP |
| `400` | Invalid or corrupted ZIP archive |
| `404` | File ID does not exist |
| `413` | File exceeds 50 MB |
| `422` | Missing required `file` field in request |

All errors return:
```json
{ "detail": "Human-readable error message here." }
```

---

## 🧪 Testing

Run the full test suite:

```bash
pytest tests/test_api.py -v
```

Expected output:
```
tests/test_api.py::test_root_redirect                      PASSED
tests/test_api.py::test_upload_invalid_extension           PASSED
tests/test_api.py::test_upload_missing_file                PASSED
tests/test_api.py::test_get_invalid_file_id                PASSED
tests/test_api.py::test_get_invalid_file_measurements      PASSED
tests/test_api.py::test_kml_upload_and_feature_count       PASSED
tests/test_api.py::test_kml_measurements_polygon_area      PASSED
tests/test_api.py::test_kml_measurements_linestring_length PASSED
tests/test_api.py::test_kml_measurements_point_no_measurement PASSED
tests/test_api.py::test_epsg4326_transforms_to_utm         PASSED
tests/test_api.py::test_valid_zip_upload                   PASSED
tests/test_api.py::test_valid_zip_polygon_measurement      PASSED
tests/test_api.py::test_zip_without_shapefile              PASSED
tests/test_api.py::test_zip_path_traversal_rejected        PASSED

14 passed in 0.89s
```

### Test Coverage Summary

| Scenario | Covered |
|---|---|
| Root redirect | ✅ |
| Invalid file extension (400) | ✅ |
| Missing file body (422) | ✅ |
| Invalid file ID → 404 | ✅ |
| Invalid measurements ID → 404 | ✅ |
| KML upload with 3 geometry types | ✅ |
| Polygon area > 0 in m² | ✅ |
| LineString length > 0 in m | ✅ |
| Point → NO_MEASUREMENT | ✅ |
| EPSG:4326 → UTM transformation verified | ✅ |
| ZIP Shapefile upload | ✅ |
| ZIP Polygon area calculation | ✅ |
| ZIP without .shp (400) | ✅ |
| ZIP path traversal attack (400) | ✅ |

---

## 🐳 Docker

### Build and Run

```bash
docker compose up --build
```

The API will be available at **http://localhost:8000**

### Manual Docker Commands

```bash
# Build image
docker build -t geospatial-api .

# Run container
docker run -p 8000:8000 -v $(pwd)/uploads:/app/uploads geospatial-api
```

### docker-compose.yml

```yaml
version: "3.8"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
```

The `uploads/` directory is mounted as a volume so uploaded files persist across container restarts.

---

## 🏗️ Architecture & Request Flow

```
Client Request
      │
      ▼
  FastAPI App (main.py)
      │  include_router
      ▼
  routes/files.py          ← HTTP concerns: method, status code, response model
      │  delegates to
      ▼
  services/file_processor.py   ← Orchestration: validate → save → parse → cache
      │  calls
      ├──► utils/validators.py       ← Extension check, ZIP safety scan
      ├──► services/crs_handler.py   ← CRS detection, UTM zone selection
      └──► services/measurement.py   ← Pure geometry area/length computation
      │
      ▼
  schemas/file_schema.py   ← Pydantic serialization to JSON response
```

---

## 💡 Design Decisions

| Decision | Reason |
|---|---|
| **FastAPI over Django/Flask** | Native async, automatic Swagger/OpenAPI, Pydantic v2 integration out of the box |
| **GeoPandas for file reading** | Handles KML, Shapefile, GeoJSON and more through a unified DataFrame interface |
| **Shapely for geometry ops** | Industry standard for 2D geometry; `.area` and `.length` are exact on projected coordinates |
| **UTM via centroid** | Most datasets are regional — centroid-based UTM gives the best accuracy without requiring user input |
| **In-memory metadata store** | Sufficient for this assignment scope; clearly documented with production alternative |
| **UUID filenames** | Prevents path injection and filename collisions regardless of what the user uploads |
| **No frontend** | This is a backend API — kept clean and purpose-built |
| **`tempfile.TemporaryDirectory()`** | Guarantees temp extraction directories are cleaned up even if an exception occurs |

---

## 🚧 Known Limitations

1. **Multi-zone datasets**: Datasets spanning more than one UTM zone (e.g., continental-scale data) will have measurement inaccuracies at the zone boundaries. The centroid heuristic is a reasonable approximation for city/regional scale data.

2. **In-memory storage**: All metadata and GeoDataFrames are stored in Python dicts. Restarting the server clears all previously uploaded file records.

3. **No authentication**: The API has no auth layer — anyone with network access can upload files. Intended for local/evaluation use only.

4. **Large files**: Files up to 50 MB are accepted synchronously. Very large Shapefiles with millions of features may cause response latency.

---

## 🔭 Future Scope

### 💾 Persistent Storage
- Replace the in-memory dict with **PostgreSQL + PostGIS** for durable file metadata and spatial query support
- Store uploaded files in **AWS S3 / Azure Blob / Google Cloud Storage** instead of local disk

### ⚡ Performance & Scalability
- Offload heavy geospatial processing to a **Celery + Redis** background task queue
- Return a job ID immediately and let the client poll for completion — avoids HTTP timeouts on large files
- Add **streaming upload** support for files beyond 50 MB using chunked transfer encoding
- Cache measurement results in **Redis** so repeated requests for the same file are instant

### 🔐 Security & Auth
- Add **JWT / OAuth2 authentication** to protect the upload endpoint
- Implement **rate limiting** (e.g., via SlowAPI) to prevent abuse
- Add **API key management** for enterprise clients
- Scan uploaded content with an antivirus/malware service before processing

### 🌍 Enhanced Geospatial Support
- Support additional file formats: **GeoJSON**, **GeoTIFF**, **FlatGeobuf**, **GPKG**
- Support **3D geometries** (Z coordinates) with volume calculations
- Implement **reprojection-aware area** for datasets crossing UTM zone boundaries using equal-area projections (e.g., Albers, Mollweide)
- Add **bounding box extraction** per feature
- Support **coordinate simplification** (Douglas-Peucker) for large polygon responses

### 📊 Analytics & Reporting
- Dashboard endpoint returning aggregate statistics (total area, total length) per upload
- Export measurements as **CSV / GeoJSON / Excel**
- Spatial query endpoints: "find all features within bounding box"
- Historical analytics per file (trends over multiple uploads of the same region)

### 🏗️ Infrastructure
- **Kubernetes** deployment manifests (Helm chart)
- **CI/CD pipeline** via GitHub Actions — auto-run pytest on every push
- **Health check** endpoint for load balancer integration
- **Prometheus metrics** for request count, latency, and error rate monitoring
- **Structured logging** (JSON logs) for log aggregation (ELK / Datadog)

### 👁️ Visualization (Optional)
- Optional lightweight map preview endpoint returning **GeoJSON** for frontend rendering with Leaflet or MapLibre
- Thumbnail map PNG generation using **Matplotlib + Contextily** for static previews

---

## 🎓 Learning Outcomes

Building this project involved gaining hands-on experience with:

- Designing a clean, modular **FastAPI** backend
- Understanding **REST API conventions** (status codes, resource naming, error contracts)
- Handling **multipart file uploads** securely
- Processing real geospatial formats: **KML** and **Shapefile**
- Understanding **CRS concepts** — why geographic and projected systems differ
- Implementing **UTM zone selection** mathematically from coordinates
- Using **GeoPandas** for spatial data pipelines
- Writing pure **Shapely** geometry computations
- Building **self-contained pytest tests** that create their own test data
- Containerizing a Python app with **Docker**
- Writing professional **technical documentation**

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">

Built with Python, FastAPI, and GeoPandas · For the Aereo Internship Assignment

</div>
