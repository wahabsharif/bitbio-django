from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any


SUPERSCRIPT_MAP = {
    "0": "⁰",
    "1": "¹",
    "2": "²",
    "3": "³",
    "4": "⁴",
    "5": "⁵",
    "6": "⁶",
    "7": "⁷",
    "8": "⁸",
    "9": "⁹",
}


def parse_decimal_input(value: str | None) -> float:
    if value is None:
        return float("nan")
    s = str(value).strip()
    if s == "":
        return float("nan")

    # If single comma and no dot, treat comma as decimal separator
    if "," in s and "." not in s:
        if s.count(",") == 1:
            try:
                return float(s.replace(",", "."))
            except ValueError:
                return float("nan")

    # Otherwise remove thousands separators and parse
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return float("nan")


def format_volume(value: float, unit: str) -> str:
    if unit == "uL":
        return f"{round(value):d}"
    if unit == "mL":
        return f"{value:.2f}"
    return str(value)


def format_exponential(num: float) -> str:
    if num == 0:
        return "0"
    base, exp_str = f"{num:.2e}".split("e")
    exp = exp_str.replace("+", "")
    superscript = "".join(SUPERSCRIPT_MAP.get(d, "") for d in exp)
    return f"{base} x 10{superscript}"


@dataclass
class ValidationResult:
    missing_fields: List[str]
    negative_value_fields: List[str]
    percentage_over_limit_fields: List[str]

    @property
    def has_errors(self) -> bool:
        return bool(
            self.missing_fields
            or self.negative_value_fields
            or self.percentage_over_limit_fields
        )


def validate_required_fields(payload: Dict[str, Any]) -> ValidationResult:
    required = [
        ("seeding_density", "Seeding Density"),
        ("num_wells", "Number of Wells"),
        ("surface_area", "Surface Area"),
        ("media_volume", "Media Volume"),
        ("count1", "Cell Count 1"),
        ("viability1", "Viability 1"),
        ("buffer", "Buffer Percentage"),
        ("suspension_volume", "Suspension Volume"),
    ]

    missing: List[str] = []
    negative: List[str] = []
    over_pct: List[str] = []

    for field_id, label in required:
        raw = (payload.get(field_id, "") or "").strip()
        if raw == "":
            missing.append(label)
            continue

        if field_id == "seeding_density":
            num = parse_decimal_input(raw)
        else:
            try:
                num = float(raw)
            except ValueError:
                num = float("nan")

        if num != num:  # NaN check
            missing.append(label)
            continue

        if num < 0:
            negative.append(label)

        if (
            field_id in {"viability1", "viability2", "viability3", "buffer"}
            and num > 100
        ):
            over_pct.append(label)

    return ValidationResult(missing, negative, over_pct)


def compute_variability(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    if mean == 0:
        return 0.0
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return (variance**0.5) / mean


def perform_calculation(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Parse inputs
    seeding = parse_decimal_input(payload.get("seeding_density")) or 0.0
    wells = int(parse_decimal_input(str(payload.get("num_wells", "0"))) or 0)
    area = parse_decimal_input(payload.get("surface_area")) or 0.0
    media_vol = parse_decimal_input(payload.get("media_volume")) or 0.0
    counts = [
        parse_decimal_input(payload.get("count1")),
        parse_decimal_input(payload.get("count2")),
        parse_decimal_input(payload.get("count3")),
    ]
    viabilities = [
        parse_decimal_input(payload.get("viability1")),
        parse_decimal_input(payload.get("viability2")),
        parse_decimal_input(payload.get("viability3")),
    ]
    buffer_perc = parse_decimal_input(payload.get("buffer")) or 0.0
    suspension_vol = parse_decimal_input(payload.get("suspension_volume")) or 1.0

    valid_counts = [c for c in counts if isinstance(c, (int, float)) and c and c > 0]
    valid_viabs = [
        v for v in viabilities if isinstance(v, (int, float)) and v and v > 0
    ]

    if not valid_counts or not valid_viabs or wells <= 0 or area <= 0:
        return {"error": "Insufficient valid inputs for calculation"}

    avg_count = sum(valid_counts) / len(valid_counts)
    avg_viab = sum(valid_viabs) / len(valid_viabs)

    # Calculation logic mirrored from JS
    cell_density = (avg_count * 1_000_000 * (avg_viab / 100.0)) / max(
        suspension_vol, 1e-9
    )
    cells_per_well = seeding * area
    required_cells = cells_per_well * wells
    required_cells *= 1.0 + buffer_perc / 100.0

    vol_to_seed = required_cells / max(cell_density, 1e-9)
    total_media_needed = media_vol * wells
    total_media_with_buffer = total_media_needed * (1.0 + buffer_perc / 100.0)
    vol_dilute = total_media_with_buffer - vol_to_seed
    vol_plate_per_well = total_media_with_buffer / max(wells, 1)

    # Warnings
    warnings: List[str] = []
    total_available_cells = cell_density * suspension_vol
    if required_cells > total_available_cells:
        warnings.append(
            "Please note that the number of live cells available is insufficient for your experimental design. Please review your setup and consider adjustments, such as reducing the number of wells used in the experiment."
        )
    if buffer_perc == 0:
        warnings.append(
            "⚠️ It is highly recommended to include a buffer to ensure enough cells and media."
        )
    if vol_to_seed < 0.1:
        warnings.append(
            f"The required cell suspension volume is very small ({format_volume(vol_to_seed, 'mL')} mL). Consider using fewer wells or increasing the suspension volume for more accurate pipetting."
        )

    # Variability checks (info-level, can be used by client if desired)
    counts_cv = compute_variability(valid_counts)
    viab_cv = compute_variability(valid_viabs)

    result = {
        # Raw numbers
        "wells": wells,
        "cell_density": cell_density,
        "cells_per_well": cells_per_well,
        "required_cells": required_cells,
        "vol_to_seed_ml": vol_to_seed,
        "vol_dilute_ml": max(0.0, vol_dilute),
        "vol_plate_per_well_ul": vol_plate_per_well * 1000.0,
        # Formatted strings
        "volume_to_dilute": format_volume(max(0.0, vol_dilute), "mL"),
        "volume_to_seed": format_volume(vol_to_seed, "mL"),
        "volume_plate_per_well": format_volume(vol_plate_per_well * 1000.0, "uL"),
        "cell_density_formatted": format_exponential(cell_density),
        "required_cells_total_formatted": format_exponential(required_cells),
        "cells_per_well_formatted": f"{int(round(cells_per_well)):,}",
        # Narrative
        "narrative": {
            "narrativeWellCount": wells,
            "narrativeVolumeSeed": format_volume(vol_to_seed, "mL"),
            "narrativeVolumeDilute": format_volume(max(0.0, vol_dilute), "mL"),
            "narrativeVolumePerWell": format_volume(vol_plate_per_well * 1000.0, "uL"),
            "narrativeCellDensity": format_exponential(cell_density),
            "narrativeCellsPerWell": f"{int(round(cells_per_well)):,}",
        },
        # Warnings / diagnostics
        "warnings": warnings,
        "counts_cv": counts_cv,
        "viability_cv": viab_cv,
    }
    return result
