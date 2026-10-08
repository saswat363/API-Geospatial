import os
import zipfile
from fastapi import HTTPException

def validate_file_extension(filename: str):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ['.kml', '.zip']:
        raise HTTPException(status_code=400, detail="Unsupported file type. Only .kml and .zip files are allowed.")

def validate_zip_contents(zip_path: str):
    """
    Ensure zip file contains at least a .shp file.
    Also protects against path traversal by checking zip file contents.
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            has_shp = False
            for name in zip_ref.namelist():
                # Prevent path traversal
                if '..' in name or name.startswith('/') or name.startswith('\\'):
                    raise HTTPException(status_code=400, detail="Dangerous file path in ZIP.")
                if name.lower().endswith('.shp'):
                    has_shp = True
            if not has_shp:
                raise HTTPException(status_code=400, detail="ZIP does not contain a .shp file.")
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid or corrupted ZIP file.")
