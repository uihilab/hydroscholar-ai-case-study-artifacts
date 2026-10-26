import logging
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Polygon

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    # Define bounding box coordinates (lon, lat)
    min_lon, max_lon = -124.5, -116.0
    min_lat, max_lat = 42.0, 49.0

    logger.info(
        f"Creating manual bounding box polygon with "
        f"lon [{min_lon}, {max_lon}] and lat [{min_lat}, {max_lat}]"
    )

    # Define the polygon (closed ring)
    bbox_coords = [
        (min_lon, min_lat),
        (max_lon, min_lat),
        (max_lon, max_lat),
        (min_lon, max_lat),
        (min_lon, min_lat)
    ]
    basin_poly = Polygon(bbox_coords)

    # Create GeoDataFrame
    basin_gdf = gpd.GeoDataFrame(
        {"geometry": [basin_poly]},
        crs="EPSG:4326"
    )
    logger.info("GeoDataFrame created with CRS EPSG:4326")

    # Ensure output directory exists
    output_path = Path("data/columbia_basin.geojson")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Ensured directory exists: {output_path.parent}")

    # Save to GeoJSON
    try:
        basin_gdf.to_file(output_path, driver="GeoJSON")
        logger.info(f"Saved basin boundary to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save GeoJSON: {e}")

if __name__ == "__main__":
    main()