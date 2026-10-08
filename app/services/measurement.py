from shapely.geometry.base import BaseGeometry

def calculate_measurement(geometry: BaseGeometry) -> dict:
    """
    Calculates measurement based on geometry type.
    Must be called on geometries that are already in a projected CRS.
    """
    if geometry is None or geometry.is_empty:
        return {
            "measurement": None,
            "measurement_unit": None,
            "status": "NO_MEASUREMENT"
        }

    geom_type = geometry.geom_type
    
    if geom_type in ['Polygon', 'MultiPolygon']:
        area = geometry.area
        return {
            "measurement": round(area, 2),
            "measurement_unit": "m²",
            "status": "SUCCESS"
        }
    elif geom_type in ['LineString', 'MultiLineString']:
        length = geometry.length
        return {
            "measurement": round(length, 2),
            "measurement_unit": "m",
            "status": "SUCCESS"
        }
    elif geom_type in ['Point', 'MultiPoint']:
        return {
            "measurement": None,
            "measurement_unit": None,
            "status": "NO_MEASUREMENT"
        }
    else:
        # GeometryCollection or others
        return {
            "measurement": None,
            "measurement_unit": None,
            "status": "UNSUPPORTED_GEOMETRY"
        }
