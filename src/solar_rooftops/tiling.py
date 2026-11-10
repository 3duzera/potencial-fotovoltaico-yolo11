"""Split large orthophotos (.tif) into a grid of smaller tiles for annotation and inference."""
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None  # orthophotos are larger than PIL's default safety limit


def split_image(input_path: str | Path, output_dir: str | Path, grid: tuple[int, int] = (10, 10)) -> list[Path]:
    """Cut an image into ``rows x cols`` equal tiles saved as JPEG.

    Tiles are named ``<stem>_crop_<row>_<col>.jpg``, matching the dataset naming.
    """
    input_path, output_dir = Path(input_path), Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    image = Image.open(input_path).convert("RGB")
    rows, cols = grid
    tile_w, tile_h = image.width // cols, image.height // rows

    tiles = []
    for row in range(rows):
        for col in range(cols):
            left, upper = col * tile_w, row * tile_h
            tile = image.crop((left, upper, left + tile_w, upper + tile_h))
            out = output_dir / f"{input_path.stem}_crop_{row}_{col}.jpg"
            tile.save(out, "JPEG")
            tiles.append(out)
    return tiles
