# Gridfinity AA Compact Battery Holder — Design Specification

**Date:** 2026-10-29  
**Onshape Document:** `Gridfinity AA Compact`  
- **Document ID:** `b5b3469743d50b565ee40c26`
- **Workspace ID (`Main`):** `0474acc4041cedb16334c819`
- **Target Element (`Part Studio 1`):** `3877013e0cee0529c7476669` (units: `millimeter`)

---

## 1. Overview & Purpose

Design and generate a compact, two-tier stackable **2×2 Gridfinity AA battery holder** (`83.5 × 83.5 mm` actual footprint) for drawer storage (121 mm vertical drawer clearance). The system holds **44 AA batteries** (22 per bin) in individual vertical pockets accessed from above using a cylindrical magnetic battery grabber (`Ø11.95 mm` max at magnet tip, `105 mm` length), plus an integrated vertical storage slot for the grabber in the front-right corner.

---

## 2. Physical & Dimensional Constraints

### 2.1 Measured Battery & Tool Dimensions
- **Rayovac Fusion Alkaline:** `Ø14.18 mm × 50.50 mm`
- **EBL NiMH:** `Ø14.38 mm × 50.22 mm`
- **PowerOwl NiMH:** `Ø14.30 mm × 50.27 mm`
- **Design Envelope per AA Cell:** `Ø14.38 mm` max diameter, `50.50 mm` max height
- **AA Pocket Bore:** `Ø15.00 mm` (`+0.62 mm` diametral clearance for zero-friction vertical removal via magnetic grabber)
- **Magnetic Grabber Envelope:** `Ø11.95 mm` bottom magnet end (`~Ø7 mm` neck above magnet, `Ø11.0 mm` top handle flare), `105.0 mm` total length
- **Grabber Bore (Receptacle & Pass-Through):** `Ø12.80 mm` (`+0.85 mm` clearance over `11.95 mm` magnet tip) with a `1.0 mm × 45°` entry funnel chamfer at the top of each hole

### 2.2 Gridfinity `2×2` Base & Lip Specification
- **Grid Pitch:** `42.00 mm` (`2×2` nominal = `84.00 mm × 84.00 mm`)
- **Actual Outer Body Dimensions:** `83.50 mm × 83.50 mm` (`-0.25 mm` per side standard clearance), centered on the origin (`X ∈ [-41.75, +41.75]`, `Y ∈ [-41.75, +41.75]`)
- **Outer Corner Radius:** `R3.75 mm` (corner arc centers at `(±38.00, ±38.00)`)
- **Gridfinity Foot Profile (`Z = 0` to `Z = 4.75 mm` on each `42 × 42 mm` cell):**
  - Plain solid feet (no magnet holes)
  - Individual foot top (`Z = 4.75 mm`): `41.50 × 41.50 mm`, corner radius `R3.75 mm`
  - Bottom 45° chamfer (`Z = 0.00` to `0.80 mm`): inset `0.80 mm`
  - Vertical step (`Z = 0.80` to `2.60 mm`): `1.80 mm` height
  - Upper 45° chamfer (`Z = 2.60` to `4.75 mm`): inset `2.15 mm`
  - Bottom contact flat (`Z = 0.00 mm`): `35.60 × 35.60 mm`, corner radius `R0.80 mm`
- **Bottom Bin Top Stacking Lip (`Z = 56.00` to `Z = 60.40 mm`):**
  - Matches standard Gridfinity stacking profile around the `83.50 × 83.50 mm` perimeter so the Top Bin's `2×2` feet drop in by `4.40 mm` and rest at `Z = 56.00 mm`.
  - Inner clear opening of the stacking lip: `78.30 × 78.30 mm` (`2.60 mm` radial lip width: `1.90 mm` bottom 45° bevel + `1.80 mm` vertical + `0.70 mm` top 45° bevel = `4.40 mm` lip height).

### 2.3 Vertical Z-Height Stack Budget (121 mm Drawer Limit)
- **Bottom Bin (`8U` nominal):**
  - `Z = 0.00 mm`: Bottom of Gridfinity feet
  - `Z = 4.00 mm`: Internal floor of all 22 AA pockets and 1 grabber receptacle (`4.00 mm` solid bottom thickness)
  - `Z = 54.50 mm`: Top of tallest `50.50 mm` AA battery inside Bottom Bin (`1.50 mm` clearance below `Z = 56.00 mm`)
  - `Z = 56.00 mm`: Stacking seat plane (shoulder where Top Bin feet rest)
  - `Z = 60.40 mm`: Top tip of Bottom Bin stacking lip
- **Top Bin (`4U` low-profile, modeled in stacked position `Z_base = 56.00 mm` or alongside with clean offset):**
  - Total height of Top Bin part: `28.00 mm` (`4U`, flat top rim with no upper stacking lip)
  - When stacked on Bottom Bin (`Z_top_bin_bottom = 56.00 mm`):
    - `Z = 56.00 to 60.75 mm`: Top Bin Gridfinity feet (seated inside Bottom Bin lip)
    - `Z = 60.00 mm`: Internal floor of Top Bin's 22 AA pockets (`4.00 mm` above Top Bin bottom, yielding `24.00 mm` pocket depth to prevent tipping)
    - `Z = 84.00 mm`: Top rim of Top Bin
    - `Z = 109.00 mm`: Top tip of `105.0 mm` magnetic grabber (`4.00 + 105.00 mm`), protruding **`25.00 mm` above the Top Bin rim** for easy finger access
    - `Z = 110.50 mm`: Top of `50.50 mm` AA batteries in Top Bin (`60.00 + 50.50 mm`), protruding **`26.50 mm` above the Top Bin rim** with **`10.50 mm` vertical clearance** under the `121.00 mm` drawer lip

---

## 3. Honeycomb `5-4-5-4-5` Cell Coordinates

All 23 hole centers lie comfortably inside the `78.30 × 78.30 mm` inner lip boundary:
- **X-Pitch (`P_x`):** `15.80 mm` (`15.00 mm` AA bore + `0.80 mm` minimum wall thickness between adjacent holes in the same row)
- **Y-Row Pitch (`P_y`):** `13.68 mm` (`15.80 × sin(60°) = 13.683 mm`, maintaining `15.80 mm` diagonal center-to-center spacing and `0.80 mm` diagonal wall thickness)
- **5 Rows (`j ∈ {-2, -1, 0, +1, +2}`, `Y_j = j × 13.68 mm` → `Y ∈ {-27.36, -13.68, 0.00, +13.68, +27.36}`):**
  - **Row `j = -2` (`Y = -27.36 mm`, Front Row — 5 slots):**
    - `X ∈ {-31.60, -15.80, 0.00, +15.80}` → **4 AA pockets (`Ø15.00 mm`)**
    - `X = +31.60, Y = -27.36 mm` (Front-Right Corner) → **1 Grabber slot (`Ø12.80 mm`)**
  - **Row `j = -1` (`Y = -13.68 mm` — 4 slots):**
    - `X ∈ {-23.70, -7.90, +7.90, +23.70}` → **4 AA pockets (`Ø15.00 mm`)**
  - **Row `j = 0` (`Y = 0.00 mm`, Center Row — 5 slots):**
    - `X ∈ {-31.60, -15.80, 0.00, +15.80, +31.60}` → **5 AA pockets (`Ø15.00 mm`)**
  - **Row `j = +1` (`Y = +13.68 mm` — 4 slots):**
    - `X ∈ {-23.70, -7.90, +7.90, +23.70}` → **4 AA pockets (`Ø15.00 mm`)**
  - **Row `j = +2` (`Y = +27.36 mm`, Rear Row — 5 slots):**
    - `X ∈ {-31.60, -15.80, 0.00, +15.80, +31.60}` → **5 AA pockets (`Ø15.00 mm`)**
- **Bounding Span Check:**
  - Max X extent of holes: `31.60 + 7.50 = 39.10 mm` (`< 39.15 mm` inner stacking lip wall, and `2.65 mm` inside the `41.75 mm` outer wall)
  - Max Y extent of holes: `27.36 + 7.50 = 34.86 mm` (`4.29 mm` inside the `39.15 mm` inner stacking lip wall, and `6.89 mm` inside the `41.75 mm` outer Y wall!)

---

## 4. Ergonomic Details on Both Parts

1. **Grabber Funnel Chamfers:**
   - Top of the Bottom Bin grabber receptacle (`Z = 56.00 mm` shoulder) and top of the Top Bin grabber pass-through hole have a `1.00 mm × 45°` conical lead-in chamfer (`Ø14.80 mm` tapering to `Ø12.80 mm`) so dropping the `Ø11.95 mm` magnet tip through the Top Bin into the Bottom Bin self-centers smoothly.
2. **Top Bin Finger-Lift Recesses:**
   - Taking advantage of the extra `6.89 mm` wall thickness along the front and back walls (`Y = ±41.75 mm`), horizontal finger-grip grooves (`40.0 mm` wide along X, `2.5 mm` deep into Y, positioned near the upper half of the Top Bin front/back outer walls) provide a positive grip to lift the Top Bin off the Bottom Bin.

---

## 5. Onshape API Access, References & Endpoint Guide

To ensure any agent or fresh session has everything needed to authenticate, build, and verify the CAD model without prior chat context:

### 5.1 Reference Documentation & Links
- **API Explorer:** https://cad.onshape.com/glassworks/explorer/
- **Onshape REST Documentation:** https://onshape-public.github.io/docs/api-intro/
- **Onshape Public Sample Code:** https://github.com/onshape-public
- **Base API URL:** `https://cad.onshape.com/api/v10`

### 5.2 Authentication & Credentials
- **Authentication Method:** HTTP Basic Auth (`access_key:secret_key`) or environment variables from `.env` in the workspace root (`/home/kyzik/tmp/onshape_gridifinity_batt/.env`):
  - `ONSHAPE_ACCESS_KEY=<ACCESS KEY HERE>`
  - `ONSHAPE_SECRET_KEY=<SECRET KEY HERE>`
- **Example `curl` invocation:**
  ```bash
  curl -s -u "$ONSHAPE_ACCESS_KEY:$ONSHAPE_SECRET_KEY" \
    "https://cad.onshape.com/api/v10/documents/d/b5b3469743d50b565ee40c26/w/0474acc4041cedb16334c819/elements"
  ```

### 5.3 Key Onshape REST Endpoints for This Project
All Part Studio endpoints use:
- `did = b5b3469743d50b565ee40c26`
- `wid = 0474acc4041cedb16334c819`
- `eid = 3877013e0cee0529c7476669` (`Part Studio 1`)

1. **Inspect existing features & `serializationVersion` / `sourceMicroversion`:**
   - `GET /api/v10/partstudios/d/{did}/w/{wid}/e/{eid}/features`
2. **Evaluate FeatureScript queries / expressions:**
   - `POST /api/v10/partstudios/d/{did}/w/{wid}/e/{eid}/featurescript`
3. **Add or update features in Part Studio (e.g., sketches, extrudes, chamfers, or custom FeatureScript feature definitions):**
   - `POST /api/v10/partstudios/d/{did}/w/{wid}/e/{eid}/features`
   - Or update full feature studio / custom feature studio element if using a Feature Studio (`POST /api/v10/featurestudios/d/{did}/w/{wid}` to create a Feature Studio, `POST /api/v10/featurestudios/d/{did}/w/{wid}/e/{feid}` to push clean FeatureScript code, and `POST /api/v10/partstudios/d/{did}/w/{wid}/e/{eid}/features` to instantiate the custom feature in `Part Studio 1`).
4. **Verify generated solid parts & names:**
   - `GET /api/v10/parts/d/{did}/w/{wid}/e/{eid}`
5. **Verify exact bounding boxes:**
   - `GET /api/v10/partstudios/d/{did}/w/{wid}/e/{eid}/boundingboxes`
6. **Verify mass & volume properties:**
   - `GET /api/v10/partstudios/d/{did}/w/{wid}/e/{eid}/massproperties`
7. **Render shaded views (visual inspection PNG):**
   - `GET /api/v10/partstudios/d/{did}/w/{wid}/e/{eid}/shadedviews?viewMatrix=isometric&outputHeight=800&outputWidth=800`

8. **Rename Elements & Set Part Properties/Names:**
   - Update element metadata/names (e.g., rename `Part Studio 1` to `AA Battery Holder Bins` and `Assembly 1` to `AA Battery Holder Stack Assembly`) via `POST /api/v10/metadata/d/{did}/w/{wid}/e/{eid}` or FeatureScript `setProperty(..., PropertyType.NAME, ...)`.
   - Every sketch, feature, custom feature, part, and tab MUST have a clear, descriptive name.

---

## 6. Naming Conventions (No Default Names Allowed)

All elements, features, sketches, and generated parts in the Onshape document MUST be explicitly named with descriptive titles—never leave default names like `Part Studio 1`, `Assembly 1`, `Part 1`, `Sketch 1`, or `Extrude 1`:

1. **Document Tabs (Elements):**
   - Part Studio (`3877013e0cee0529c7476669`): Rename from `Part Studio 1` → **`AA Battery Holder Bins`**
   - Assembly (`84c8a0fd2b9361f75c2d3a37`): Rename from `Assembly 1` → **`AA Battery Holder Assembly`**
   - Feature Studio (if created): Name **`Gridfinity AA Holder Generator`**
2. **Generated Solid Parts:**
   - Lower bin part: **`Bottom Bin`**
   - Upper bin part: **`Top Bin`**
3. **Sketches & Features in the Feature Tree:**
   - Every sketch and modeling feature in the Part Studio feature tree must carry an explicit descriptive `name` field in its `BTMFeature` JSON payload (e.g., `Base Gridfinity Feet Sketch`, `Main Body Extrude`, `Stacking Lip Profile`, `Honeycomb 22xAA Pocket Cut`, `Corner Grabber Receptacle`, `Top Bin Finger Lift Grooves`, etc.).

---

## 7. Implementation & Verification Criteria

1. **Onshape Construction:**
   - Build both parts cleanly in the Part Studio (`3877013e0cee0529c7476669`) of document `b5b3469743d50b565ee40c26` via the Onshape REST API.
   - Apply all naming conventions from Section 6 to tabs, features, sketches, and solid bodies.
   - Position the two parts cleanly (e.g., either stacked in-place at `Z = 0` and `Z = 56.00 mm`, or side-by-side at `Z = 0` for immediate 3D printing export, plus assembled in `AA Battery Holder Assembly` `84c8a0fd2b9361f75c2d3a37`).
2. **Automated Verification:**
   - Query the Onshape REST API for element names, feature tree names, feature regeneration status (zero errors/warnings), part names, bounding boxes, and mass/volume properties.
   - Export/render shaded thumbnail views from Onshape to visually verify the `2×2` base feet, `5-4-5-4-5` honeycomb pockets, corner grabber pass-through/receptacle, stacking lip, and finger-lift recesses.
