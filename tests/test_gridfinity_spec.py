import math
from src.gridfinity_spec import DIMENSIONS, get_honeycomb_slots, is_circle_inside_rounded_rect
from src.onshape_client import OnshapeClient


def test_honeycomb_slot_counts_and_grabber_position():
    slots = get_honeycomb_slots()
    aa_slots = [s for s in slots if s.kind == "AA"]
    grabber_slots = [s for s in slots if s.kind == "GRABBER"]
    assert len(slots) == 23
    assert len(aa_slots) == 22
    assert len(grabber_slots) == 1
    g = grabber_slots[0]
    assert math.isclose(g.x_mm, 31.60, abs_tol=1e-3)
    assert math.isclose(g.y_mm, -27.36, abs_tol=1e-3)
    assert math.isclose(g.diameter_mm, 12.80, abs_tol=1e-3)


def test_inter_cell_wall_thickness_and_lip_clearance():
    slots = get_honeycomb_slots()
    inner_lip_half = DIMENSIONS["inner_lip_span_mm"] / 2.0  # 39.15 mm
    inner_lip_corner_r = DIMENSIONS["inner_lip_corner_radius_mm"]  # 1.15 mm
    for i, a in enumerate(slots):
        ra = a.diameter_mm / 2.0
        assert abs(a.x_mm) + ra < inner_lip_half
        assert abs(a.y_mm) + ra < inner_lip_half
        assert is_circle_inside_rounded_rect(a.x_mm, a.y_mm, ra, inner_lip_half, inner_lip_corner_r)
        for b in slots[i + 1 :]:
            rb = b.diameter_mm / 2.0
            dist = math.hypot(a.x_mm - b.x_mm, a.y_mm - b.y_mm)
            wall = dist - (ra + rb)
            assert wall >= 0.79, f"Wall too thin ({wall:.3f} mm) between {a} and {b}"
    # Verify a hypothetical circle encroaching the R1.15 mm corner arc at (38.0, 38.0) is rejected
    assert not is_circle_inside_rounded_rect(38.50, 38.50, 0.50, inner_lip_half, inner_lip_corner_r)


def test_vertical_z_stack_budget():
    assert DIMENSIONS["bottom_floor_z_mm"] + DIMENSIONS["max_aa_height_mm"] <= DIMENSIONS["stacking_seat_z_mm"] - 1.0
    assert DIMENSIONS["top_floor_z_mm"] + DIMENSIONS["max_aa_height_mm"] <= DIMENSIONS["drawer_height_mm"] - 10.0
    grabber_top = DIMENSIONS["bottom_floor_z_mm"] + DIMENSIONS["grabber_length_mm"]
    assert DIMENSIONS["top_bin_top_z_mm"] + 20.0 <= grabber_top <= DIMENSIONS["drawer_height_mm"] - 10.0


def test_onshape_client_connects_to_document():
    client = OnshapeClient.from_env()
    elements = client.get_elements()
    ids = {el["id"] for el in elements}
    assert client.partstudio_eid in ids
