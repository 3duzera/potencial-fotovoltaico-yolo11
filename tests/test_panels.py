from shapely.geometry import box

from solar_rooftops import PanelSpec, SiteParams, annual_generation_kwh, best_layout, pack_panels

PANEL = PanelSpec(width_m=2.0, height_m=1.0, power_kw=0.5)


def test_rectangle_fits_exact_grid():
    panels = pack_panels(box(0, 0, 10, 5), PANEL, angle=0)
    assert len(panels) == 25  # 5 columns x 5 rows


def test_panels_stay_inside_and_do_not_overlap():
    area = box(0, 0, 7.3, 4.1)
    panels = pack_panels(area, PANEL, angle=0)
    assert all(area.contains(p) for p in panels)
    for i, a in enumerate(panels):
        for b in panels[i + 1:]:
            assert a.intersection(b).area < 1e-6


def test_best_layout_applies_setback_and_picks_best_angle():
    site = SiteParams(resolution_m_per_px=0.1, setback_m=0.5)
    roof_px = box(0, 0, 45, 110)  # 4.5 m x 11 m roof -> 3.5 m x 10 m usable
    layout = best_layout(roof_px, PANEL, site, angles=(0, 90))
    assert abs(layout.usable_m.area - 35.0) < 1e-6
    assert layout.angle == 90  # 0 deg fits 1 x 10 = 10 modules; 90 deg fits 3 x 5 = 15
    assert layout.n_panels == 15


def test_roof_smaller_than_setback_returns_none():
    assert best_layout(box(0, 0, 5, 5), PANEL, SiteParams()) is None


def test_annual_generation_formula():
    site = SiteParams(irradiation_kwh_m2_day=5.0, performance_ratio=0.8)
    assert annual_generation_kwh(10, PANEL, site) == 10 * 0.5 * 5.0 * 0.8 * 365
