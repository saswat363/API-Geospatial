from fastapi import APIRouter, File, UploadFile, status
from app.schemas.file_schema import FileInfo, FileMeasurementsResponse
from app.services.file_processor import handle_file_upload, get_file_info, get_file_measurements

router = APIRouter(prefix="/api/files", tags=["files"])

@router.post("/", response_model=FileInfo, status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a geospatial file (.kml or .zip containing a shapefile).
    """
    return await handle_file_upload(file)

@router.get("/{id}/", response_model=FileInfo)
async def read_file_info(id: str):
    """
    Get file metadata.
    """
    return get_file_info(id)

@router.get("/{id}/measurements/", response_model=FileMeasurementsResponse)
async def read_file_measurements(id: str):
    """
    Get geometry measurements for all features in the file.
    """
    return get_file_measurements(id)
