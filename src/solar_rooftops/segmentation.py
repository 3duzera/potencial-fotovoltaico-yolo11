"""Roof segmentation: run the YOLO11-seg model or read YOLO-format polygon labels."""
from pathlib import Path

from shapely.geometry import Polygon
from shapely.validation import make_valid

Point = tuple[float, float]


def _to_polygon(points: list[Point]) -> Polygon | None:
    if len(points) < 3:
        return None
    polygon = Polygon(points)
    if not polygon.is_valid:
        polygon = make_valid(polygon)
        # make_valid may return a collection; keep the largest polygonal part
        parts = [g for g in getattr(polygon, "geoms", [polygon]) if g.geom_type == "Polygon"]
        if not parts:
            return None
        polygon = max(parts, key=lambda g: g.area)
    return polygon if polygon.area > 0 else None


def parse_yolo_label(line: str, img_width: int, img_height: int) -> list[Point]:
    """Convert one YOLO segmentation line (``cls x1 y1 x2 y2 ...``, normalized) to pixel points."""
    values = list(map(float, line.split()))
    coords = values[1:]  # first value is the class id
    return [(coords[i] * img_width, coords[i + 1] * img_height) for i in range(0, len(coords), 2)]


def polygons_from_labels(label_path: str | Path, img_width: int = 1024, img_height: int = 1024) -> list[Polygon]:
    """Read every roof polygon (pixel coordinates) from a YOLO label file."""
    polygons = []
    for line in Path(label_path).read_text().splitlines():
        if line.strip():
            polygon = _to_polygon(parse_yolo_label(line, img_width, img_height))
            if polygon is not None:
                polygons.append(polygon)
    return polygons


def segment_roofs(image_path: str | Path, weights: str | Path, conf: float = 0.25, imgsz: int = 1024) -> list[Polygon]:
    """Segment roofs in an image with the trained YOLO11-seg weights (pixel coordinates)."""
    from ultralytics import YOLO  # imported lazily: only needed for inference

    result = YOLO(str(weights)).predict(source=str(image_path), conf=conf, imgsz=imgsz, verbose=False)[0]
    if result.masks is None:
        return []
    polygons = [_to_polygon([tuple(p) for p in contour]) for contour in result.masks.xy]
    return [p for p in polygons if p is not None]
