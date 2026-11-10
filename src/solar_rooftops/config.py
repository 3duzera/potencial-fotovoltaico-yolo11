"""Default parameters used in the study (Itu-SP, 2025)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PanelSpec:
    """Photovoltaic module dimensions (m) and rated power (kWp)."""
    width_m: float = 2.465
    height_m: float = 1.134
    power_kw: float = 0.560  # 560 Wp monocrystalline module


@dataclass(frozen=True)
class SiteParams:
    """Imagery and site parameters."""
    resolution_m_per_px: float = 0.1     # ground sample distance of the orthophotos
    setback_m: float = 0.5               # safety margin removed from the roof edge
    irradiation_kwh_m2_day: float = 5.094  # mean daily irradiation on a tilted plane, Itu-SP
    performance_ratio: float = 0.8       # system losses (inverter, cabling, temperature, dirt)


DEFAULT_PANEL = PanelSpec()
DEFAULT_SITE = SiteParams()
DEFAULT_ANGLES = (0, 45, 90, 135)
