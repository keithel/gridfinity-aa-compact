"""Geometry specification for the 2x2 Gridfinity AA Compact Battery Holder."""

from dataclasses import dataclass
import math

DIMENSIONS: dict[str, float] = {
    "grid_pitch_mm": 42.00,
    "outer_span_mm": 83.50,
    "outer_half_span_mm": 41.75,
    "outer_corner_radius_mm": 3.75,
    "foot_span_mm": 41.50,
    "foot_height_mm": 4.75,
    "foot_bottom_chamfer_mm": 0.80,
    "foot_vertical_step_mm": 1.80,
    "foot_upper_chamfer_mm": 2.15,
    "inner_lip_span_mm": 78.30,
    "inner_lip_corner_radius_mm": 1.15,
    "lip_radial_width_mm": 2.60,
    "lip_bottom_bevel_mm": 1.90,
    "lip_vertical_mm": 1.80,
    "lip_top_bevel_mm": 0.70,
    "lip_height_mm": 4.40,
    "bottom_floor_z_mm": 4.00,
    "stacking_seat_z_mm": 56.00,
    "bottom_bin_top_z_mm": 60.40,
    "top_bin_base_z_mm": 56.00,
    "top_bin_feet_top_z_mm": 60.75,
    "top_floor_z_mm": 60.00,
    "top_bin_height_mm": 28.00,
    "top_bin_top_z_mm": 84.00,
    "max_aa_diameter_mm": 14.38,
    "max_aa_height_mm": 50.50,
    "aa_bore_diameter_mm": 15.00,
    "grabber_max_diameter_mm": 11.95,
    "grabber_length_mm": 105.00,
    "grabber_magnet_protrusion_mm": 0.15,
    "grabber_bore_diameter_mm": 12.80,
    "grabber_funnel_chamfer_mm": 1.00,
    "pitch_x_mm": 15.80,
    "pitch_y_mm": 13.68,
    "drawer_height_mm": 121.00,
    "finger_groove_width_mm": 40.00,
    "finger_groove_depth_mm": 2.50,
    "finger_groove_z_min_mm": 72.00,
    "finger_groove_z_max_mm": 80.00,
}


@dataclass(frozen=True)
class SlotSpec:
    """Coordinate and diameter specification for a single honeycomb pocket."""

    x_mm: float
    y_mm: float
    diameter_mm: float
    kind: str  # "AA" or "GRABBER"


def get_honeycomb_slots() -> list[SlotSpec]:
    """Return the 23 slots in the 5-4-5-4-5 honeycomb pattern (22 AA + 1 Grabber)."""
    px = DIMENSIONS["pitch_x_mm"]
    py = DIMENSIONS["pitch_y_mm"]
    aa_d = DIMENSIONS["aa_bore_diameter_mm"]
    grabber_d = DIMENSIONS["grabber_bore_diameter_mm"]

    slots: list[SlotSpec] = []
    for row_idx in (-2, -1, 0, 1, 2):
        y = round(row_idx * py, 4)
        if row_idx % 2 == 0:
            x_positions = [-2 * px, -px, 0.0, px, 2 * px]
        else:
            x_positions = [-1.5 * px, -0.5 * px, 0.5 * px, 1.5 * px]

        for col_idx, x_raw in enumerate(x_positions):
            x = round(x_raw, 4)
            if row_idx == -2 and col_idx == len(x_positions) - 1:
                slots.append(SlotSpec(x_mm=x, y_mm=y, diameter_mm=grabber_d, kind="GRABBER"))
            else:
                slots.append(SlotSpec(x_mm=x, y_mm=y, diameter_mm=aa_d, kind="AA"))
    return slots


def is_circle_inside_rounded_rect(
    x_mm: float,
    y_mm: float,
    radius_mm: float,
    half_span_mm: float,
    corner_radius_mm: float,
) -> bool:
    """Return True if a circle of `radius_mm` at `(x_mm, y_mm)` is strictly inside a rounded square."""
    ax = abs(x_mm)
    ay = abs(y_mm)
    if ax + radius_mm >= half_span_mm or ay + radius_mm >= half_span_mm:
        return False
    arc_center = half_span_mm - corner_radius_mm
    if ax > arc_center and ay > arc_center:
        dist_to_arc_center = math.hypot(ax - arc_center, ay - arc_center)
        if dist_to_arc_center + radius_mm >= corner_radius_mm:
            return False
    return True
