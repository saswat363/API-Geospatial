from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class FileInfo(BaseModel):
    id: str
    filename: str
    feature_count: int
    crs: Optional[str]
    status: str

class FeatureMeasurement(BaseModel):
    feature_id: int
    geometry_type: Optional[str]
    geometry: Optional[Dict[str, Any]]
    properties: Dict[str, Any]
    measurement: Optional[float]
    measurement_unit: Optional[str]
    status: str

class FileMeasurementsResponse(BaseModel):
    file_id: str
    filename: str
    crs: Optional[str]
    measurement_crs: Optional[str]
    features: List[FeatureMeasurement]
