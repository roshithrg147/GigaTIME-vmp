import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

import numpy as np

logger = logging.getLogger(__name__)

TILE_SIZE = 256
MAX_TILES = 64  # Cap for MVP; increase when production-ready


def load_and_tile_slide(
    image_path: str,
    tile_size: int = TILE_SIZE,
    max_tiles: int = MAX_TILES,
    overlap: int = 0,
) -> List[np.ndarray]:
    """
    Load a slide (SVS, TIFF, PNG, JPEG) and extract tiles using
    healthcareai_toolkit's ImageReader.

    Returns a list of uint8 numpy arrays of shape [tile_size, tile_size, 3].
    Falls back to a synthetic tile grid if the image cannot be opened,
    which supports mock/test mode without real slides.
    """
    try:
        from healthcareai_toolkit.data.image_reader import ImageReader
        from healthcareai_toolkit.data.image_preprocessor import ImagePreprocessor
        from healthcareai_toolkit.data.file_types import get_filetype

        reader = ImageReader(engine="sitk")
        mime_type = get_filetype(image_path)
        image_array = reader.read_to_image_array(image_path, mime_type)

        preprocessor = ImagePreprocessor(pad_to_square=False, resize_size=None)
        image_array = preprocessor.preprocess_image(
            image_array, normalize=str(image_array.dtype) != "uint8"
        )
        image_array = np.clip(image_array, 0, 255).astype(np.uint8)

        tiles = _extract_tiles(image_array, tile_size, overlap, max_tiles)
        logger.info(
            "Extracted %d tiles from %s via healthcareai_toolkit",
            len(tiles), image_path
        )
        return tiles

    except Exception as exc:
        logger.warning(
            "Could not load slide via healthcareai_toolkit (%s). "
            "Falling back to synthetic tiles for mock mode.",
            exc
        )
        return _generate_synthetic_tiles(tile_size, count=4)


def _extract_tiles(
    image: np.ndarray,
    tile_size: int,
    overlap: int,
    max_tiles: int,
) -> List[np.ndarray]:
    """Slice a numpy image array into non-overlapping tiles."""
    h, w = image.shape[:2]
    step = tile_size - overlap
    tiles = []

    for y in range(0, h - tile_size + 1, step):
        for x in range(0, w - tile_size + 1, step):
            tile = image[y:y + tile_size, x:x + tile_size]
            if tile.shape[0] == tile_size and tile.shape[1] == tile_size:
                if tile.ndim == 2:
                    tile = np.stack([tile] * 3, axis=-1)
                elif tile.shape[-1] > 3:
                    tile = tile[:, :, :3]
                tiles.append(tile)
            if len(tiles) >= max_tiles:
                return tiles

    return tiles if tiles else _generate_synthetic_tiles(tile_size, count=4)


def _generate_synthetic_tiles(tile_size: int, count: int) -> List[np.ndarray]:
    """Return noise tiles for unit testing and mock mode."""
    rng = np.random.default_rng(seed=42)
    return [
        rng.integers(0, 255, (tile_size, tile_size, 3), dtype=np.uint8)
        for _ in range(count)
    ]
