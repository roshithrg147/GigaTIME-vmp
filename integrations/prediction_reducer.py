"""
GigaTIME returns predictions as a list of numpy arrays, each shaped [23, H, W],
where each of the 23 channels corresponds to one protein/marker.

Channel ordering is based on the official GigaTIME model card:
  prov-gigatime/GigaTIME on Hugging Face
"""
from typing import List, Dict, Any
import numpy as np
from scipy.stats import entropy as scipy_entropy

CHANNEL_NAMES: List[str] = [
    "PD-L1", "CD8", "CD20", "CD138", "CD68", "CD163",
    "HER2", "ER", "PR", "Ki67", "CD4", "CD3",
    "FOXP3", "CD56", "CD31", "SMA", "FAP", "ColIV",
    "EpCAM", "SOX10", "CK14",
    "bg1", "bg2",  # non-protein background channels
]

# Clinically relevant channels surfaced directly in the report
PRIORITY_CHANNELS = ["PD-L1", "CD8", "CD20", "CD138", "CD68", "FOXP3", "Ki67", "CD3"]

HIGH_DENSITY_THRESHOLD = 0.5


def reduce_predictions(predictions: List[np.ndarray]) -> Dict[str, Any]:
    """
    Aggregate a list of per-tile [23, H, W] float32 arrays into a compact
    biomarker summary dict that can be stored in JobStore and consumed by
    the summarize_spatial_architecture Gemini prompt.

    Args:
        predictions: List of numpy arrays, shape [23, H, W] each.

    Returns:
        Structured dict with biomarker_summary and spatial_metrics.
    """
    if not predictions:
        return _empty_summary()

    # Stack tiles: [N_tiles, 23, H, W]
    stacked = np.stack(predictions, axis=0).astype(np.float32)

    biomarker_summary: Dict[str, Any] = {}
    for i, name in enumerate(CHANNEL_NAMES):
        if name.startswith("bg"):
            continue  # skip background channels
        channel_data = stacked[:, i, :, :]  # [N_tiles, H, W]
        mean_density = float(channel_data.mean())
        max_density = float(channel_data.max())
        high_tile_fraction = float((channel_data > HIGH_DENSITY_THRESHOLD).mean())
        biomarker_summary[name] = {
            "mean_density": round(mean_density, 4),
            "max_density": round(max_density, 4),
            "high_tile_fraction": round(high_tile_fraction, 4),
        }

    spatial_metrics = _compute_spatial_metrics(stacked)
    immune_phenotype = _classify_immune_phenotype(biomarker_summary)

    return {
        "tile_count": len(predictions),
        "channel_count": len(CHANNEL_NAMES) - 2,  # exclude bg channels
        "biomarker_summary": biomarker_summary,
        "spatial_metrics": {
            **spatial_metrics,
            "immune_phenotype": immune_phenotype,
        },
        "priority_biomarkers": {
            k: biomarker_summary[k]
            for k in PRIORITY_CHANNELS
            if k in biomarker_summary
        },
    }


def _compute_spatial_metrics(stacked: np.ndarray) -> Dict[str, float]:
    """Compute entropy and spatial heterogeneity across tiles."""
    # Mean activation per tile across all protein channels (exclude bg)
    protein_stack = stacked[:, :21, :, :]  # [N, 21, H, W]
    mean_per_tile = protein_stack.mean(axis=(1, 2, 3))  # [N]

    # Shannon entropy over tile-level mean activations
    hist, _ = np.histogram(mean_per_tile, bins=20, range=(0, 1), density=True)
    hist = hist + 1e-10  # avoid log(0)
    spatial_entropy = float(scipy_entropy(hist))

    return {
        "spatial_entropy": round(spatial_entropy, 4),
        "mean_protein_activation": round(float(mean_per_tile.mean()), 4),
        "tile_heterogeneity": round(float(mean_per_tile.std()), 4),
    }


def _classify_immune_phenotype(biomarker_summary: Dict[str, Any]) -> str:
    """
    Classify the tumor immune phenotype based on CD8 and CD3 spatial density.

    Phenotypes:
      - immune-inflamed:  high CD8 + high CD3 density
      - immune-excluded:  low CD8 but moderate CD3
      - immune-desert:    low CD8 + low CD3
    """
    cd8 = biomarker_summary.get("CD8", {}).get("mean_density", 0.0)
    cd3 = biomarker_summary.get("CD3", {}).get("mean_density", 0.0)

    if cd8 > 0.4 and cd3 > 0.3:
        return "immune-inflamed"
    elif cd3 > 0.2:
        return "immune-excluded"
    else:
        return "immune-desert"


def _empty_summary() -> Dict[str, Any]:
    return {
        "tile_count": 0,
        "channel_count": 0,
        "biomarker_summary": {},
        "spatial_metrics": {"immune_phenotype": "unknown"},
        "priority_biomarkers": {},
    }
