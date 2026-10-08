import os
import uuid
import zipfile
import tempfile
import geopandas as gpd
import fiona
import pandas as pd
from fastapi import UploadFile, HTTPException
from shapely.geometry import mapping
from app.schemas.file_schema import FileInfo, FeatureMeasurement
from app.utils.validators import validate_file_extension, validate_zip_contents
from app.services.crs_handler import determine_measurement_crs, transform_for_measurement
from app.services.measurement import calculate_measurement

# In-memory storage for the assignment
files_metadata = {}
file_features_cache = {}

# Ensure fiona supports KML
try:
    fiona.drvsupport.supported_drivers['KML'] = 'rw'
    fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'
except AttributeError:
    pass

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
MAX_FILE_SIZE = 50 * 1024 * 1024 # 50 MB

async def save_upload_file(upload_file: UploadFile, file_id: str) -> str:
    # Read first to check size
    contents = await upload_file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB.")
        
    ext = os.path.splitext(upload_file.filename)[1].lower()
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    
    with open(file_path, "wb") as f:
        f.write(contents)
        
    return file_path

def process_geospatial_file(file_path: str, ext: str) -> gpd.GeoDataFrame:
    try:
        if ext == '.kml':
            gdf = gpd.read_file(file_path, driver='KML')
            return gdf
        elif ext == '.zip':
            validate_zip_contents(file_path)
            # Create a temporary directory to extract
            with tempfile.TemporaryDirectory() as tmp_dir:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(tmp_dir)
                
                # Find the .shp file
                shp_file = None
                for root, dirs, files in os.walk(tmp_dir):
                    for file in files:
                        if file.lower().endswith('.shp'):
                            shp_file = os.path.join(root, file)
                            break
                    if shp_file:
                        break
                
                if not shp_file:
                    raise HTTPException(status_code=400, detail="ZIP does not contain a .shp file.")
                    
                gdf = gpd.read_file(shp_file)
                return gdf
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid or corrupted geospatial file: {str(e)}")

async def handle_file_upload(upload_file: UploadFile) -> FileInfo:
    """Orchestrates: extension validation → disk save → geospatial parse → in-memory cache → return metadata."""
    filename = upload_file.filename
    validate_file_extension(filename)
    
    file_id = str(uuid.uuid4())
    file_path = await save_upload_file(upload_file, file_id)
    
    ext = os.path.splitext(filename)[1].lower()
    gdf = process_geospatial_file(file_path, ext)
    
    crs_str = gdf.crs.to_string() if gdf.crs else None
    
    file_info = FileInfo(
        id=file_id,
        filename=filename,
        feature_count=len(gdf),
        crs=crs_str,
        status="COMPLETED"
    )
    
    # Store metadata
    files_metadata[file_id] = file_info
    
    # Pre-process and cache features for the measurements endpoint
    file_features_cache[file_id] = {
        "gdf": gdf,
        "crs_str": crs_str,
        "filename": filename
    }
    
    return file_info

def get_file_info(file_id: str) -> FileInfo:
    """Return cached FileInfo metadata for the given UUID, or raise 404."""
    if file_id not in files_metadata:
        raise HTTPException(status_code=404, detail="File ID does not exist.")
    return files_metadata[file_id]

def get_file_measurements(file_id: str):
    """Return per-feature measurements for the given UUID. Applies CRS transformation before computing area/length."""
    if file_id not in file_features_cache:
        raise HTTPException(status_code=404, detail="File ID does not exist.")
        
    cache_data = file_features_cache[file_id]
    gdf = cache_data["gdf"]
    original_crs = cache_data["crs_str"]
    filename = cache_data["filename"]
    
    if original_crs is None:
        # If CRS is missing, we return status explaining that
        measurement_crs = None
        transformed_gdf = gdf
    else:
        measurement_crs = determine_measurement_crs(gdf)
        transformed_gdf = transform_for_measurement(gdf, measurement_crs) if measurement_crs else gdf
        
    features = []
    
    # Reset index to have sequential feature IDs
    gdf = gdf.reset_index(drop=True)
    transformed_gdf = transformed_gdf.reset_index(drop=True)
    
    for idx, row in gdf.iterrows():
        # original geometry for GeoJSON output
        orig_geom = row.geometry
        geom_type = orig_geom.geom_type if orig_geom else None
        
        # safely convert to geojson dict
        geom_dict = mapping(orig_geom) if orig_geom and not orig_geom.is_empty else None
        
        # properties (attributes excluding geometry)
        properties = {col: row[col] for col in gdf.columns if col != 'geometry' and not isinstance(row[col], (gpd.GeoSeries, gpd.GeoDataFrame))}
        # pd.isna raises ValueError on list/dict values, so guard with try/except
        def _safe_nan(v):
            try:
                return None if pd.isna(v) else v
            except (ValueError, TypeError):
                return v
        properties = {k: _safe_nan(v) for k, v in properties.items()}
        
        if original_crs is None:
            measurement = None
            unit = None
            status = "MISSING_CRS"
        else:
            trans_geom = transformed_gdf.loc[idx, 'geometry']
            meas_res = calculate_measurement(trans_geom)
            measurement = meas_res["measurement"]
            unit = meas_res["measurement_unit"]
            status = meas_res["status"]
            
        feat = FeatureMeasurement(
            feature_id=idx,
            geometry_type=geom_type,
            geometry=geom_dict,
            properties=properties,
            measurement=measurement,
            measurement_unit=unit,
            status=status
        )
        features.append(feat)
        
    return {
        "file_id": file_id,
        "filename": filename,
        "crs": original_crs,
        "measurement_crs": measurement_crs,
        "features": features
    }
