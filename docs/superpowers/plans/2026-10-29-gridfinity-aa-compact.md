# Gridfinity AA Compact Battery Holder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` (Native inline execution — selected by user) to implement this plan task-by-task in the session. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and verify the two-tier `2×2` Gridfinity AA battery holder (`Bottom Bin` and `Top Bin`, holding 44 AA batteries + 1 corner magnetic grabber) in the user's Onshape document `Gridfinity AA Compact` via the Onshape REST API.

**Architecture:** A Python Onshape REST client (`src/onshape_client.py`) and deterministic geometry specification module (`src/gridfinity_spec.py`) drive a parametric Onshape builder (`src/build_onshape_model.py`). The builder defines descriptive custom FeatureScript features in a dedicated `Gridfinity AA Holder Generator` Feature Studio, instantiates named features and sketches in the `AA Battery Holder Bins` Part Studio to produce the `Bottom Bin` and `Top Bin` solid parts, populates `AA Battery Holder Assembly`, and verifies all geometry, naming, bounding boxes, and shaded renders against the live Onshape API.

**Tech Stack:** Python 3, `requests`, `pytest`, Onshape REST API v10, Onshape FeatureScript (`std/geometry.fs`).

**Spec:** `docs/superpowers/specs/2026-10-29-gridfinity-aa-compact-design.md`

## Global Constraints

- Target Onshape Document ID: `b5b3469743d50b565ee40c26`, Workspace ID: `0474acc4041cedb16334c819`, Part Studio Element ID: `3877013e0cee0529c7476669`, Assembly Element ID: `84c8a0fd2b9361f75c2d3a37`.
- Credentials loaded from `/home/kyzik/tmp/onshape_gridifinity_batt/.env` (`ONSHAPE_ACCESS_KEY`, `ONSHAPE_SECRET_KEY`).
- Outer footprint of each `2×2` bin: `83.50 mm × 83.50 mm` (`X, Y ∈ [-41.75, +41.75]`), corner radius `R3.75 mm`, plain solid `2×2` Gridfinity feet (`4.75 mm` foot height, `42.00 mm` grid pitch, no magnet holes).
- Honeycomb `5-4-5-4-5` layout per bin: 22 AA pockets (`Ø15.00 mm`) + 1 front-right corner grabber slot (`Ø12.80 mm` at `X = +31.60 mm, Y = -27.36 mm` with `1.00 mm × 45°` top entry funnel chamfer).
- `Bottom Bin` height: `8U` nominal (`56.00 mm` to stacking seat + `4.40 mm` Gridfinity stacking lip = `60.40 mm` total height; blind pocket floor at `Z = 4.00 mm`).
- `Top Bin` height: `4U` low-profile (`28.00 mm` total height, modeled in stacked position `Z ∈ [56.00, 84.00]`; AA blind pocket floor at `Z = 60.00 mm`; corner grabber hole (`Ø12.80 mm`) cuts completely through the floor and foot; front/back outer walls at `Y = ±41.75 mm` have `40.0 mm × 2.5 mm` finger-lift grooves).
- Mandatory naming: Rename `Part Studio 1` to `AA Battery Holder Bins`, rename `Assembly 1` to `AA Battery Holder Assembly`, name solid parts `Bottom Bin` and `Top Bin`, and ensure every sketch and feature in the Part Studio has a descriptive name (no default names like `Sketch 1`, `Extrude 1`, or `Part 1`).

## Review Focus

- Corner fillet / inner lip intersection: Verify every hole in the `5-4-5-4-5` honeycomb grid (including corner holes at `(±31.60, ±27.36)`) stays strictly inside the `78.30 × 78.30 mm` (`R1.15 mm` inner corner radius) stacking lip clear opening so no pocket cuts into the stacking lip wall.
- Pass-through hole depth in `Top Bin`: Since `Top Bin` has `4.75 mm` Gridfinity feet (`Z = 56.00` to `60.75 mm`), the `Ø12.80 mm` grabber pass-through hole at `(+31.60, -27.36)` must cut completely through `Z = 56.00` to `84.00 mm` (not stop at the `Z = 60.00 mm` AA pocket floor).
- Foot-to-lip stacking clearance: When `Top Bin` sits on `Bottom Bin` at `Z = 56.00 mm`, the `Bottom Bin` stacking lip (`Z = 56.00` to `60.40 mm`) and `Top Bin` feet (`Z = 56.00` to `60.75 mm`) must not boolean-merge into a single body; they must remain two distinct solid parts named `Bottom Bin` and `Top Bin`.
- Element rename endpoint compatibility: Verify via `GET /api/v10/documents/d/{did}/w/{wid}/elements` that the Part Studio and Assembly tab names actually update in Onshape after calling the rename/metadata endpoint.
- FeatureScript regeneration status: Ensure `GET /api/v10/partstudios/d/{did}/w/{wid}/e/{eid}/features` reports zero `ERROR` or `WARNING` statuses across all features.

---

### Task 1: Geometry Specification & Onshape REST Client

**Files:**
- Create: `src/gridfinity_spec.py`
- Create: `src/onshape_client.py`
- Test: `tests/test_gridfinity_spec.py`

**Interfaces:**
- Consumes: `/home/kyzik/tmp/onshape_gridifinity_batt/.env`
- Produces:
  - `src.gridfinity_spec.SlotSpec(x_mm: float, y_mm: float, diameter_mm: float, kind: str)`
  - `src.gridfinity_spec.get_honeycomb_slots() -> list[SlotSpec]`
  - `src.gridfinity_spec.DIMENSIONS: dict[str, float]`
  - `src.onshape_client.OnshapeClient` with methods `get_elements()`, `get_features(eid)`, `add_feature(eid, feature_payload)`, `delete_feature(eid, fid)`, `create_feature_studio(name)`, `update_feature_studio(feid, code, serialization_version, source_microversion)`, `get_parts(eid)`, `get_bounding_boxes(eid)`, `get_mass_properties(eid)`, `get_shaded_view(eid, view_matrix)`

- [ ] **Step 1: Write the failing geometry and API client tests in `tests/test_gridfinity_spec.py`**

```python
import math
from src.gridfinity_spec import DIMENSIONS, get_honeycomb_slots
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
    for i, a in enumerate(slots):
        ra = a.diameter_mm / 2.0
        assert abs(a.x_mm) + ra < inner_lip_half
        assert abs(a.y_mm) + ra < inner_lip_half
        for b in slots[i + 1 :]:
            rb = b.diameter_mm / 2.0
            dist = math.hypot(a.x_mm - b.x_mm, a.y_mm - b.y_mm)
            wall = dist - (ra + rb)
            assert wall >= 0.79, f"Wall too thin ({wall:.3f} mm) between {a} and {b}"


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
```

- [ ] **Step 2: Run `pytest` to verify the tests fail**

Run: `pytest tests/test_gridfinity_spec.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'src'`

- [ ] **Step 3: Implement `src/gridfinity_spec.py` and `src/onshape_client.py`**

Implement `SlotSpec`, `DIMENSIONS` (matching all values in Section 2 & 3 of the spec), `get_honeycomb_slots()`, and `OnshapeClient` using HTTP Basic Auth (`ONSHAPE_ACCESS_KEY`, `ONSHAPE_SECRET_KEY`) against `https://cad.onshape.com/api/v10`.

- [ ] **Step 4: Run `pytest` to verify Task 1 tests pass**

Run: `pytest tests/test_gridfinity_spec.py -v`
Expected: 4 passed

- [ ] **Step 5: Commit Task 1**

```bash
git add src/gridfinity_spec.py src/onshape_client.py tests/test_gridfinity_spec.py
git commit -m "feat: add Gridfinity AA honeycomb geometry spec and Onshape REST client"
```

---

### Task 2: Parametric Onshape Model Generation & Element Naming

**Files:**
- Create: `src/featurescript_generator.py`
- Create: `src/build_onshape_model.py`
- Test: `tests/test_onshape_verification.py`

**Interfaces:**
- Consumes: `src.gridfinity_spec.DIMENSIONS`, `src.gridfinity_spec.get_honeycomb_slots()`, `src.onshape_client.OnshapeClient`
- Produces:
  - `src.featurescript_generator.generate_feature_studio_code() -> str`
  - `src.build_onshape_model.build_and_publish() -> dict`
  - Live Onshape document updates:
    - Feature Studio tab named `Gridfinity AA Holder Generator`
    - Part Studio tab (`3877013e0cee0529c7476669`) renamed to `AA Battery Holder Bins`
    - Assembly tab (`84c8a0fd2b9361f75c2d3a37`) renamed to `AA Battery Holder Assembly`
    - Named features in `AA Battery Holder Bins`: `Bottom Bin (2x2 8U) Generator` and `Top Bin (2x2 4U) Generator`
    - Named solid parts in `AA Battery Holder Bins`: `Bottom Bin` and `Top Bin`

- [ ] **Step 1: Write the failing verification tests in `tests/test_onshape_verification.py`**

```python
import math
from pathlib import Path
from src.onshape_client import OnshapeClient


def test_element_tab_names_are_descriptive():
    client = OnshapeClient.from_env()
    elements = {el["id"]: el["name"] for el in client.get_elements()}
    assert elements[client.partstudio_eid] == "AA Battery Holder Bins"
    assert elements[client.assembly_eid] == "AA Battery Holder Assembly"
    for name in elements.values():
        assert not name.startswith("Part Studio ")
        assert not name.startswith("Assembly ")


def test_features_have_descriptive_names_and_no_errors():
    client = OnshapeClient.from_env()
    data = client.get_features(client.partstudio_eid)
    features = data.get("features", [])
    assert len(features) >= 2
    statuses = {
        s["featureId"]: s["statusType"]
        for s in data.get("featureStates", [])
        if "featureId" in s and "statusType" in s
    }
    for feat in features:
        name = feat.get("name", "")
        assert name and not name.startswith(("Sketch ", "Extrude ", "Chamfer "))
        fid = feat.get("featureId")
        if fid in statuses:
            assert statuses[fid] == "OK", f"Feature {name} ({fid}) has status {statuses[fid]}"


def test_solid_parts_names_bounding_boxes_and_volumes():
    client = OnshapeClient.from_env()
    parts = client.get_parts(client.partstudio_eid)
    part_by_name = {p["name"]: p for p in parts}
    assert set(part_by_name.keys()) == {"Bottom Bin", "Top Bin"}

    mass_props = client.get_mass_properties(client.partstudio_eid)
    bodies = mass_props.get("bodies", {})
    for part_name, p in part_by_name.items():
        pid = p["partId"]
        bbox = client.get_part_bounding_box(client.partstudio_eid, pid)
        dx = (bbox["highX"] - bbox["lowX"]) * 1000.0
        dy = (bbox["highY"] - bbox["lowY"]) * 1000.0
        dz = (bbox["highZ"] - bbox["lowZ"]) * 1000.0
        assert math.isclose(dx, 83.50, abs_tol=0.1), f"{part_name} dx={dx}"
        assert math.isclose(dy, 83.50, abs_tol=0.1), f"{part_name} dy={dy}"
        if part_name == "Bottom Bin":
            assert math.isclose(bbox["lowZ"] * 1000.0, 0.0, abs_tol=0.1)
            assert math.isclose(dz, 60.40, abs_tol=0.1), f"Bottom Bin dz={dz}"
        else:
            assert math.isclose(bbox["lowZ"] * 1000.0, 56.00, abs_tol=0.1)
            assert math.isclose(dz, 28.00, abs_tol=0.1), f"Top Bin dz={dz}"
        assert bodies[pid]["volume"][0] > 1e-5
```

- [ ] **Step 2: Run `pytest tests/test_onshape_verification.py` to confirm it fails against the empty document**

Run: `pytest tests/test_onshape_verification.py -v`
Expected: FAIL (Part Studio is still named `Part Studio 1` and has 0 parts/features)

- [ ] **Step 3: Implement `src/featurescript_generator.py` and `src/build_onshape_model.py` and execute the build**

In `src/featurescript_generator.py`, generate clean FeatureScript (`FeatureScript 2411; import(path : "onshape/std/geometry.fs", version : "2411.0");`) defining two custom features:
1. `buildBottomBin`:
   - Constructs the `2×2` plain solid Gridfinity feet (`Z = 0` to `4.75 mm`, four `42.0 mm`-spaced feet with `0.8 mm` bottom 45° chamfer, `1.8 mm` vertical wall, and `2.15 mm` upper 45° chamfer),
   - Constructs the main `83.50 × 83.50 mm` (`R3.75 mm`) body (`Z = 4.75` to `56.00 mm`),
   - Constructs the standard Gridfinity top stacking lip (`Z = 56.00` to `60.40 mm`, `78.30 × 78.30 mm` inner clear opening tapering out to `83.50 × 83.50 mm`),
   - Subtracts the 22 AA blind pockets (`Ø15.00 mm`, `Z = 4.00` to `60.40 mm`) and the front-right corner grabber blind receptacle (`Ø12.80 mm` at `(+31.60, -27.36)`, `Z = 4.00` to `56.00 mm` with a `1.00 mm × 45°` funnel chamfer from `Ø14.80 mm` at `Z = 56.00 mm` to `Ø12.80 mm` at `Z = 55.00 mm`),
   - Calls `setProperty(context, { "entities" : qCreatedBy(id, EntityType.BODY), "propertyType" : PropertyType.NAME, "value" : "Bottom Bin" })` and assigns distinct appearance colors so the two bins are visually clear.
2. `buildTopBin`:
   - Constructs the `2×2` plain solid Gridfinity feet at `Z = 56.00` to `60.75 mm`,
   - Constructs the `83.50 × 83.50 mm` (`R3.75 mm`) low-profile body from `Z = 60.75` to `84.00 mm` (`28.00 mm` total height),
   - Subtracts the 22 AA blind pockets (`Ø15.00 mm`, floor at `Z = 60.00 mm` up to `84.00 mm`),
   - Subtracts the front-right corner grabber through-hole (`Ø12.80 mm` at `(+31.60, -27.36)`, cutting completely through `Z = 56.00` to `84.00 mm` with a `1.00 mm × 45°` funnel chamfer at `Z = 84.00 mm`),
   - Subtracts the front and rear finger-lift grooves (`40.0 mm` wide in `X ∈ [-20, +20]`, `2.5 mm` deep into `Y = ±41.75 mm`, `Z ∈ [72.0, 80.0 mm]` with chamfered edges),
   - Calls `setProperty(context, { "entities" : qCreatedBy(id, EntityType.BODY), "propertyType" : PropertyType.NAME, "value" : "Top Bin" })`.

In `src/build_onshape_model.py`, push the Feature Studio (`Gridfinity AA Holder Generator`), instantiate both named features (`Bottom Bin (2x2 8U) Generator` and `Top Bin (2x2 4U) Generator`) in `AA Battery Holder Bins`, rename the Part Studio and Assembly tabs, insert both parts into `AA Battery Holder Assembly`, and export shaded view PNGs to `docs/renders/`.

- [ ] **Step 4: Run `python3 -m src.build_onshape_model` and `pytest` to verify all tests pass**

Run: `python3 -m src.build_onshape_model && pytest -v`
Expected: All unit and live Onshape verification tests PASS.

- [ ] **Step 5: Visually inspect shaded view renders and commit**

Verify `docs/renders/isometric.png` and `docs/renders/top.png` using `read_file`, then commit all source files, tests, and renders:
```bash
git add src/ tests/ docs/renders/
git commit -m "feat: generate and verify 2x2 Gridfinity AA battery holder bins in Onshape"
```
