"""Build, name, assemble, and render the 2x2 Gridfinity AA Compact Battery Holder in Onshape."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

from src.featurescript_generator import generate_feature_studio_code
from src.gridfinity_spec import DIMENSIONS, get_honeycomb_slots
from src.onshape_client import OnshapeClient


FEATURE_STUDIO_NAME = "Gridfinity AA Holder Generator"
PART_STUDIO_NAME = "AA Battery Holder Bins"
GRABBER_PART_STUDIO_NAME = "Battery Grabber"
ASSEMBLY_NAME = "AA Battery Holder Assembly"

GRABBER_SOURCE_DID = "c8113e21846b3e243f4047b0"
GRABBER_SOURCE_WID = "85c21653a7b2a35730264c4a"
GRABBER_SOURCE_EID = "efc09f3688cba75a14ed5637"


def _get_grabber_assembly_transform() -> list[float]:
    """Return 4x4 row-major transform (meters) seating Main Body magnet-down in the grabber pocket."""
    grabber_slot = next(s for s in get_honeycomb_slots() if s.kind == "GRABBER")
    tx_m = grabber_slot.x_mm / 1000.0
    ty_m = grabber_slot.y_mm / 1000.0
    # 180 deg rotation about X-axis: local Z=105mm (magnet head) -> Z=4mm floor; local Z=0mm (pommel) -> Z=109mm
    tz_m = (DIMENSIONS["bottom_floor_z_mm"] + DIMENSIONS["grabber_length_mm"]) / 1000.0
    return [
        1.0,  0.0,  0.0, tx_m,
        0.0, -1.0,  0.0, ty_m,
        0.0,  0.0, -1.0, tz_m,
        0.0,  0.0,  0.0, 1.0,
    ]


def _ensure_grabber_part_studio(client: OnshapeClient) -> str:
    """Find or copy the Battery Grabber Part Studio (Main Body + Support Fins) into the document."""
    for el in client.get_elements():
        if el.get("elementType") == "PARTSTUDIO" and el.get("name") == GRABBER_PART_STUDIO_NAME:
            return el["id"]
    copied = client.copy_element_from_document(
        source_did=GRABBER_SOURCE_DID,
        source_wid=GRABBER_SOURCE_WID,
        source_eid=GRABBER_SOURCE_EID,
    )
    return copied["id"]



def _ensure_feature_studio(client: OnshapeClient) -> tuple[str, str]:
    """Find or create the Feature Studio and upload the FeatureScript generator code."""
    elements = client.get_elements()
    feid: str | None = None
    for el in elements:
        if el.get("elementType") == "FEATURESTUDIO" and el.get("name") == FEATURE_STUDIO_NAME:
            feid = el["id"]
            break

    if feid is None:
        created = client.create_feature_studio(FEATURE_STUDIO_NAME)
        feid = created["id"]

    code = generate_feature_studio_code()
    updated = client.update_feature_studio(feid, code)
    microversion = updated["sourceMicroversion"]
    return feid, microversion


def _make_custom_feature_payload(
    name: str,
    feature_type: str,
    feid: str,
    fs_microversion: str,
    ps_serialization_version: str,
    ps_microversion: str,
) -> dict[str, Any]:
    return {
        "btType": "BTFeatureDefinitionCall-1406",
        "serializationVersion": ps_serialization_version,
        "sourceMicroversion": ps_microversion,
        "feature": {
            "btType": "BTMFeature-134",
            "featureType": feature_type,
            "name": name,
            "namespace": f"e{feid}::m{fs_microversion}",
            "suppressed": False,
            "parameters": [],
        },
        "imports": [
            {
                "btType": "BTMImport-136",
                "path": feid,
                "version": fs_microversion,
                "namespace": f"e{feid}::m{fs_microversion}",
            }
        ],
    }


def build_and_publish() -> dict[str, Any]:
    """Execute the end-to-end Onshape build, element naming, assembly population, and rendering."""
    client = OnshapeClient.from_env()

    # 1. Rename Part Studio and Assembly tabs
    client.rename_element(client.partstudio_eid, PART_STUDIO_NAME)
    client.rename_element(client.assembly_eid, ASSEMBLY_NAME)

    # 2. Ensure Feature Studio exists and has latest FeatureScript
    feid, fs_microversion = _ensure_feature_studio(client)

    # 3. Clear any prior features in the Part Studio so rebuild is idempotent
    ps_features = client.get_features(client.partstudio_eid)
    for feat in ps_features.get("features", []):
        fid = feat.get("featureId")
        if fid:
            client.delete_feature(client.partstudio_eid, fid)

    # 4. Instantiate Bottom Bin and Top Bin custom features
    for feat_name, feat_type in [
        ("Bottom Bin (2x2 8U) Generator", "buildBottomBin"),
        ("Top Bin (2x2 4U) Generator", "buildTopBin"),
    ]:
        ps_state = client.get_features(client.partstudio_eid)
        payload = _make_custom_feature_payload(
            name=feat_name,
            feature_type=feat_type,
            feid=feid,
            fs_microversion=fs_microversion,
            ps_serialization_version=ps_state["serializationVersion"],
            ps_microversion=ps_state["sourceMicroversion"],
        )
        client.add_feature(client.partstudio_eid, payload)

    # 5. Ensure Battery Grabber Part Studio (Main Body + Support Fins) is in the document
    grabber_eid = _ensure_grabber_part_studio(client)
    grabber_parts = client.get_parts(grabber_eid)
    grabber_main_pid = next(
        p["partId"] for p in grabber_parts if p.get("name") == "Main Body"
    )

    # 6. Verify parts and populate Assembly cleanly (purging any stale instances first)
    parts = client.get_parts(client.partstudio_eid)
    expected_keys = {(client.partstudio_eid, p["partId"]) for p in parts} | {
        (grabber_eid, grabber_main_pid)
    }
    existing_instances = client.get_assembly_instances(client.assembly_eid)
    kept_keys: set[tuple[str, str]] = set()
    for inst in existing_instances:
        node_id = inst.get("id")
        key = (inst.get("elementId", ""), inst.get("partId", ""))
        if key in expected_keys and key not in kept_keys:
            kept_keys.add(key)
        elif node_id:
            client.delete_assembly_instance(node_id=node_id, aeid=client.assembly_eid)
    for part in parts:
        key = (client.partstudio_eid, part["partId"])
        if key not in kept_keys:
            client.add_assembly_instance(
                part_id=part["partId"], part_studio_eid=client.partstudio_eid
            )
    if (grabber_eid, grabber_main_pid) not in kept_keys:
        client.add_assembly_instance(
            part_id=grabber_main_pid, part_studio_eid=grabber_eid
        )

    # Seat Main Body in the front-right grabber pocket (magnet-end down, handle up)
    updated_instances = client.get_assembly_instances(client.assembly_eid)
    grabber_inst = next(
        inst
        for inst in updated_instances
        if inst.get("elementId") == grabber_eid and inst.get("partId") == grabber_main_pid
    )
    client.transform_assembly_occurrence(
        node_id=grabber_inst["id"],
        transform=_get_grabber_assembly_transform(),
        aeid=client.assembly_eid,
    )

    # 7. Export shaded view renders of the complete assembly
    renders_dir = Path(__file__).resolve().parent.parent / "docs" / "renders"
    renders_dir.mkdir(parents=True, exist_ok=True)
    for view_name, view_matrix in [
        ("isometric", "isometric"),
        ("top", "top"),
    ]:
        view_data = client.get_assembly_shaded_view(
            client.assembly_eid, view_matrix=view_matrix
        )
        images = view_data.get("images", [])
        if images:
            img_bytes = base64.b64decode(images[0])
            (renders_dir / f"{view_name}.png").write_bytes(img_bytes)

    return {
        "feature_studio_eid": feid,
        "grabber_part_studio_eid": grabber_eid,
        "parts": [p["name"] for p in parts] + [p["name"] for p in grabber_parts],
        "renders_dir": str(renders_dir),
    }


if __name__ == "__main__":
    result = build_and_publish()
    print(f"Built Onshape model successfully: {result}")
