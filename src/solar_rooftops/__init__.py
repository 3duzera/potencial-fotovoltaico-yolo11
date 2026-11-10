"""Rooftop photovoltaic potential from satellite imagery with YOLO11 instance segmentation."""
from .config import DEFAULT_PANEL, DEFAULT_SITE, PanelSpec, SiteParams
from .energy import annual_generation_kwh
from .panels import RoofLayout, best_layout, pack_panels

__all__ = [
    "DEFAULT_PANEL", "DEFAULT_SITE", "PanelSpec", "SiteParams",
    "annual_generation_kwh", "RoofLayout", "best_layout", "pack_panels",
]
