"""Photovoltaic generation estimate."""
from .config import DEFAULT_PANEL, DEFAULT_SITE, PanelSpec, SiteParams


def annual_generation_kwh(n_panels: int, panel: PanelSpec = DEFAULT_PANEL, site: SiteParams = DEFAULT_SITE) -> float:
    """E = N x P_module x H_daily x PR x 365  (kWh/year)."""
    daily = n_panels * panel.power_kw * site.irradiation_kwh_m2_day * site.performance_ratio
    return daily * 365
