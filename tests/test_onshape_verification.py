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
    raw_states = data.get("featureStates", {})
    if isinstance(raw_states, dict):
        statuses = {
            fid: state.get("featureStatus") or state.get("statusType")
            for fid, state in raw_states.items()
            if isinstance(state, dict)
        }
    else:
        statuses = {
            s["featureId"]: s.get("featureStatus") or s.get("statusType")
            for s in raw_states
            if "featureId" in s
        }
    for feat in features:
        name = feat.get("name", "")
        assert name and not name.startswith(("Sketch ", "Extrude ", "Chamfer "))
        fid = feat.get("featureId")
        assert fid in statuses, f"Missing status for feature {name} ({fid})"
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


def test_assembly_contains_bins_and_battery_grabber():
    client = OnshapeClient.from_env()
    elements = {el["name"]: el["id"] for el in client.get_elements()}
    assert "Battery Grabber" in elements
    grabber_eid = elements["Battery Grabber"]

    grabber_parts = {p["name"]: p["partId"] for p in client.get_parts(grabber_eid)}
    assert set(grabber_parts.keys()) == {"Main Body", "Support Fins"}

    grabber_bbox = client.get_part_bounding_box(grabber_eid, grabber_parts["Main Body"])
    assert math.isclose((grabber_bbox["highX"] - grabber_bbox["lowX"]) * 1000.0, 12.0, abs_tol=0.1)
    assert math.isclose((grabber_bbox["highZ"] - grabber_bbox["lowZ"]) * 1000.0, 105.0, abs_tol=0.1)

    bin_parts = client.get_parts(client.partstudio_eid)
    expected_keys = {(client.partstudio_eid, p["partId"]) for p in bin_parts} | {
        (grabber_eid, grabber_parts["Main Body"])
    }
    instances = client.get_assembly_instances()
    instance_keys = {(inst.get("elementId"), inst.get("partId")) for inst in instances}
    assert len(instances) == 3
    assert instance_keys == expected_keys
