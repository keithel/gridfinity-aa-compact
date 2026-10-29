"""Build, name, assemble, and render the 2x2 Gridfinity AA Compact Battery Holder in Onshape."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

from src.featurescript_generator import generate_feature_studio_code
from src.onshape_client import OnshapeClient


FEATURE_STUDIO_NAME = "Gridfinity AA Holder Generator"
PART_STUDIO_NAME = "AA Battery Holder Bins"
ASSEMBLY_NAME = "AA Battery Holder Assembly"


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

    # 5. Verify parts and populate Assembly if empty
    parts = client.get_parts(client.partstudio_eid)
    asm_def = client.get_assembly_definition(client.assembly_eid)
    existing_instances = asm_def.get("rootAssembly", {}).get("instances", [])
    existing_part_ids = {inst.get("partId") for inst in existing_instances}
    for part in parts:
        pid = part["partId"]
        if pid not in existing_part_ids:
            client.add_assembly_instance(part_id=pid)

    # 6. Export shaded view renders
    renders_dir = Path(__file__).resolve().parent.parent / "docs" / "renders"
    renders_dir.mkdir(parents=True, exist_ok=True)
    for view_name, view_matrix in [
        ("isometric", "isometric"),
        ("top", "top"),
    ]:
        view_data = client.get_shaded_view(client.partstudio_eid, view_matrix=view_matrix)
        images = view_data.get("images", [])
        if images:
            img_bytes = base64.b64decode(images[0])
            (renders_dir / f"{view_name}.png").write_bytes(img_bytes)

    return {
        "feature_studio_eid": feid,
        "parts": [p["name"] for p in parts],
        "renders_dir": str(renders_dir),
    }


if __name__ == "__main__":
    result = build_and_publish()
    print(f"Built Onshape model successfully: {result}")
