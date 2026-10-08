import geopandas as gpd
import math

def get_utm_crs(lon: float, lat: float) -> str:
    """
    Determine the UTM EPSG code for a given longitude and latitude.
    """
    utm_band = str((math.floor((lon + 180) / 6) % 60) + 1)
    if len(utm_band) == 1:
        utm_band = '0' + utm_band
    
    if lat >= 0:
        epsg_code = f"326{utm_band}" # Northern hemisphere
    else:
        epsg_code = f"327{utm_band}" # Southern hemisphere
        
    return f"EPSG:{epsg_code}"

def determine_measurement_crs(gdf: gpd.GeoDataFrame) -> str | None:
    """
    Determine a suitable projected CRS for measurements.
    If the CRS is already projected, return it.
    If the CRS is geographic, calculate a suitable UTM zone based on the centroid.
    If the CRS is missing, we cannot reliably transform, so return None.
    """
    if gdf.crs is None:
        return None
        
    if gdf.crs.is_projected:
        return gdf.crs.to_string()
        
    # If geographic, calculate the centroid of the entire dataset to determine UTM zone
    valid_geoms = gdf[gdf.is_valid & ~gdf.is_empty]
    if valid_geoms.empty:
        return "EPSG:3857" # Fallback if all geometries are empty/invalid
        
    centroid = valid_geoms.union_all().centroid
    if centroid.is_empty:
        return "EPSG:3857" # Fallback
        
    lon, lat = centroid.x, centroid.y
    return get_utm_crs(lon, lat)

def transform_for_measurement(gdf: gpd.GeoDataFrame, target_crs: str) -> gpd.GeoDataFrame:
    """
    Transform a GeoDataFrame to a target CRS.
    """
    if gdf.crs is None or target_crs is None:
        return gdf
    
    return gdf.to_crs(target_crs)
