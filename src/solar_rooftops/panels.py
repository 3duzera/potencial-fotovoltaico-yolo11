"""Fit photovoltaic modules inside the usable area of a segmented roof."""
from dataclasses import dataclass

from shapely import affinity
from shapely.geometry import Polygon, box
from shapely.strtree import STRtree

from .config import DEFAULT_ANGLES, DEFAULT_PANEL, DEFAULT_SITE, PanelSpec, SiteParams


@dataclass
class RoofLayout:
    roof_m: Polygon          # full roof footprint, in meters
    usable_m: Polygon        # roof minus the edge setback, in meters
    panels: list[Polygon]    # placed modules, in meters
    angle: int               # module rotation that fitted the most panels

    @property
    def n_panels(self) -> int:
        return len(self.panels)

    @property
    def roof_area_m2(self) -> float:
        return self.roof_m.area


def to_meters(polygon_px: Polygon, resolution: float) -> Polygon:
    return affinity.scale(polygon_px, xfact=resolution, yfact=resolution, origin=(0, 0))


def usable_area(roof_m: Polygon, setback_m: float) -> Polygon:
    """Shrink the roof by ``setback_m`` on every side (negative buffer)."""
    return roof_m.buffer(-setback_m)


def pack_panels(area: Polygon, panel: PanelSpec, angle: float) -> list[Polygon]:
    """Greedy grid packing of rotated modules inside ``area``.

    Walks the bounding box in steps of one (rotated) module; at each cell it also tries
    small offsets (10% of the module) so modules can slide into irregular corners.
    """
    if area.is_empty:
        return []
    minx, miny, maxx, maxy = area.bounds
    module = affinity.rotate(box(0, 0, panel.width_m, panel.height_m), angle, origin="center")
    mx0, my0, mx1, my1 = module.bounds
    module = affinity.translate(module, -mx0, -my0)  # anchor at (0, 0)
    step_x, step_y = mx1 - mx0, my1 - my0
    offsets = [(0, 0), (0.1 * step_x, 0), (0, 0.1 * step_y), (0.1 * step_x, 0.1 * step_y)]

    placed: list[Polygon] = []
    x = minx
    while x + step_x <= maxx:
        y = miny
        while y + step_y <= maxy:
            for dx, dy in offsets:
                candidate = affinity.translate(module, xoff=x + dx, yoff=y + dy)
                if area.contains(candidate) and not _overlaps(candidate, placed):
                    placed.append(candidate)
                    break
            y += step_y
        x += step_x
    return placed


def _overlaps(candidate: Polygon, placed: list[Polygon]) -> bool:
    if not placed:
        return False
    tree = STRtree(placed)
    return any(candidate.intersection(placed[i]).area > 1e-6 for i in tree.query(candidate))


def best_layout(
    roof_px: Polygon,
    panel: PanelSpec = DEFAULT_PANEL,
    site: SiteParams = DEFAULT_SITE,
    angles: tuple[int, ...] = DEFAULT_ANGLES,
) -> RoofLayout | None:
    """Try every rotation and keep the one that fits the most modules."""
    roof_m = to_meters(roof_px, site.resolution_m_per_px)
    usable = usable_area(roof_m, site.setback_m)
    if usable.is_empty or not usable.is_valid:
        return None
    if usable.geom_type == "MultiPolygon":  # a narrow roof may split in two after the setback
        usable = max(usable.geoms, key=lambda g: g.area)

    layouts = [RoofLayout(roof_m, usable, pack_panels(usable, panel, a), a) for a in angles]
    return max(layouts, key=lambda layout: layout.n_panels)
