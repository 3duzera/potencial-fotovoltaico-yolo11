"""End-to-end pipeline: image -> roof polygons -> panel layout -> annual generation.

Examples:
    # with the trained model
    python -m solar_rooftops.pipeline examples/telhados_itu.jpg --weights weights/best.pt

    # without the model, reading ground-truth polygons (YOLO label format)
    python -m solar_rooftops.pipeline examples/telhados_itu.jpg --labels examples/telhados_itu.txt
"""
import argparse
import csv
from pathlib import Path

import cv2
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from shapely.geometry import Polygon  # noqa: E402

from .config import DEFAULT_PANEL, SiteParams  # noqa: E402
from .energy import annual_generation_kwh  # noqa: E402
from .panels import RoofLayout, best_layout  # noqa: E402
from .segmentation import polygons_from_labels, segment_roofs  # noqa: E402


def run(image: Path, roofs_px: list[Polygon], site: SiteParams) -> list[tuple[int, RoofLayout | None]]:
    return [(i, best_layout(roof, site=site)) for i, roof in enumerate(roofs_px, start=1)]


def plot(image: Path, results: list[tuple[int, RoofLayout | None]], site: SiteParams, out: Path) -> None:
    img = cv2.cvtColor(cv2.imread(str(image)), cv2.COLOR_BGR2RGB)
    res = site.resolution_m_per_px
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(img)
    for idx, layout in results:
        if layout is None:
            continue
        for geom, style in ((layout.roof_m, dict(color="#ff9f1c", lw=1.5)), (layout.usable_m, dict(color="#ffffff", lw=0.8, ls="--"))):
            x, y = geom.exterior.xy
            ax.plot([v / res for v in x], [v / res for v in y], **style)
        for panel in layout.panels:
            x, y = panel.exterior.xy
            ax.fill([v / res for v in x], [v / res for v in y], color="#1f6feb", alpha=0.75, lw=0)
        c = layout.roof_m.centroid
        ax.text(c.x / res, c.y / res, str(idx), color="white", fontsize=9, ha="center", weight="bold")
    ax.axis("off")
    fig.savefig(out, bbox_inches="tight", pad_inches=0, dpi=110)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("image", type=Path)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--weights", type=Path, help="YOLO11-seg weights (.pt)")
    source.add_argument("--labels", type=Path, help="YOLO polygon label file (.txt)")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--resolution", type=float, default=SiteParams.resolution_m_per_px, help="meters per pixel")
    parser.add_argument("--out", type=Path, default=Path("output"))
    args = parser.parse_args()

    site = SiteParams(resolution_m_per_px=args.resolution)
    if args.weights:
        roofs = segment_roofs(args.image, args.weights, conf=args.conf)
    else:
        h, w = cv2.imread(str(args.image)).shape[:2]
        roofs = polygons_from_labels(args.labels, w, h)

    results = run(args.image, roofs, site)
    args.out.mkdir(parents=True, exist_ok=True)

    rows, total_panels, total_kwh = [], 0, 0.0
    for idx, layout in results:
        if layout is None:
            rows.append([idx, "", 0, 0, "", 0])
            continue
        kwh = annual_generation_kwh(layout.n_panels, DEFAULT_PANEL, site)
        rows.append([idx, f"{layout.roof_area_m2:.1f}", f"{layout.usable_m.area:.1f}", layout.n_panels, layout.angle, f"{kwh:.0f}"])
        total_panels += layout.n_panels
        total_kwh += kwh

    with open(args.out / "telhados.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["telhado", "area_m2", "area_util_m2", "paineis", "angulo_graus", "geracao_kwh_ano"])
        writer.writerows(rows)
    plot(args.image, results, site, args.out / "layout.png")

    print(f"{len(roofs)} telhados | {total_panels} painéis | {total_kwh:,.0f} kWh/ano")
    print(f"Resultados em {args.out}/telhados.csv e {args.out}/layout.png")


if __name__ == "__main__":
    main()
