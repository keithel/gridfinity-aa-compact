"""Onshape REST API v10 client for the Gridfinity AA Compact Battery Holder."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
import requests


DEFAULT_DID = "b5b3469743d50b565ee40c26"
DEFAULT_WID = "0474acc4041cedb16334c819"
DEFAULT_PARTSTUDIO_EID = "3877013e0cee0529c7476669"
DEFAULT_ASSEMBLY_EID = "84c8a0fd2b9361f75c2d3a37"
BASE_URL = "https://cad.onshape.com/api/v10"


def _load_env_file(env_path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not env_path.exists():
        return values
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        values[key.strip()] = val.strip().strip("'\"")
    return values


class OnshapeClient:
    """Thin HTTP Basic Auth wrapper around the Onshape REST API v10."""

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        did: str = DEFAULT_DID,
        wid: str = DEFAULT_WID,
        partstudio_eid: str = DEFAULT_PARTSTUDIO_EID,
        assembly_eid: str = DEFAULT_ASSEMBLY_EID,
        base_url: str = BASE_URL,
    ) -> None:
        self.access_key = access_key
        self.secret_key = secret_key
        self.did = did
        self.wid = wid
        self.partstudio_eid = partstudio_eid
        self.assembly_eid = assembly_eid
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.auth = (access_key, secret_key)
        self.session.headers.update(
            {
                "Accept": "application/json;charset=UTF-8; qs=0.09",
                "Content-Type": "application/json;charset=UTF-8; qs=0.09",
            }
        )

    @classmethod
    def from_env(cls, env_path: str | Path | None = None) -> OnshapeClient:
        resolved_path = (
            Path(env_path)
            if env_path is not None
            else Path(__file__).resolve().parent.parent / ".env"
        )
        env_vars = _load_env_file(resolved_path)
        access_key = os.environ.get("ONSHAPE_ACCESS_KEY") or env_vars.get("ONSHAPE_ACCESS_KEY", "")
        secret_key = os.environ.get("ONSHAPE_SECRET_KEY") or env_vars.get("ONSHAPE_SECRET_KEY", "")
        if not access_key or not secret_key:
            raise RuntimeError(f"Missing ONSHAPE_ACCESS_KEY or ONSHAPE_SECRET_KEY in {resolved_path}")
        return cls(access_key=access_key, secret_key=secret_key)

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def get_elements(self) -> list[dict[str, Any]]:
        resp = self.session.get(self._url(f"documents/d/{self.did}/w/{self.wid}/elements"), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def rename_element(self, eid: str, new_name: str) -> dict[str, Any]:
        payload = {
            "properties": [
                {
                    "propertyId": "57f3fb8efa3416c06701d60d",  # Name property ID in Onshape metadata
                    "value": new_name,
                }
            ]
        }
        resp = self.session.post(
            self._url(f"metadata/d/{self.did}/w/{self.wid}/e/{eid}"),
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def get_features(self, eid: str) -> dict[str, Any]:
        resp = self.session.get(
            self._url(f"partstudios/d/{self.did}/w/{self.wid}/e/{eid}/features"),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def add_feature(self, eid: str, feature_payload: dict[str, Any]) -> dict[str, Any]:
        resp = self.session.post(
            self._url(f"partstudios/d/{self.did}/w/{self.wid}/e/{eid}/features"),
            json=feature_payload,
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()

    def delete_feature(self, eid: str, fid: str) -> dict[str, Any]:
        resp = self.session.delete(
            self._url(f"partstudios/d/{self.did}/w/{self.wid}/e/{eid}/features/featureid/{fid}"),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json() if resp.text else {}

    def create_feature_studio(self, name: str) -> dict[str, Any]:
        resp = self.session.post(
            self._url(f"featurestudios/d/{self.did}/w/{self.wid}"),
            json={"name": name},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def get_feature_studio_contents(self, feid: str) -> dict[str, Any]:
        resp = self.session.get(
            self._url(f"featurestudios/d/{self.did}/w/{self.wid}/e/{feid}"),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def update_feature_studio(
        self,
        feid: str,
        code: str,
        serialization_version: str | None = None,
        source_microversion: str | None = None,
    ) -> dict[str, Any]:
        if serialization_version is None or source_microversion is None:
            current = self.get_feature_studio_contents(feid)
            serialization_version = current["serializationVersion"]
            source_microversion = current["sourceMicroversion"]
        payload = {
            "btType": "BTFeatureStudioContents-2239",
            "contents": code,
            "serializationVersion": serialization_version,
            "sourceMicroversion": source_microversion,
        }
        resp = self.session.post(
            self._url(f"featurestudios/d/{self.did}/w/{self.wid}/e/{feid}"),
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()

    def get_parts(self, eid: str) -> list[dict[str, Any]]:
        resp = self.session.get(
            self._url(f"parts/d/{self.did}/w/{self.wid}/e/{eid}"),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def get_bounding_boxes(self, eid: str) -> dict[str, Any]:
        resp = self.session.get(
            self._url(f"partstudios/d/{self.did}/w/{self.wid}/e/{eid}/boundingboxes"),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def get_part_bounding_box(self, eid: str, part_id: str) -> dict[str, Any]:
        resp = self.session.get(
            self._url(f"parts/d/{self.did}/w/{self.wid}/e/{eid}/partid/{part_id}/boundingboxes"),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def get_mass_properties(self, eid: str) -> dict[str, Any]:
        resp = self.session.get(
            self._url(f"partstudios/d/{self.did}/w/{self.wid}/e/{eid}/massproperties"),
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        bodies = data.setdefault("bodies", {})
        for part in self.get_parts(eid):
            pid = part.get("partId")
            if pid and pid not in bodies:
                part_resp = self.session.get(
                    self._url(f"parts/d/{self.did}/w/{self.wid}/e/{eid}/partid/{pid}/massproperties"),
                    timeout=30,
                )
                part_resp.raise_for_status()
                bodies.update(part_resp.json().get("bodies", {}))
        return data

    def get_shaded_view(
        self,
        eid: str,
        view_matrix: str = "isometric",
        output_height: int = 800,
        output_width: int = 800,
    ) -> dict[str, Any]:
        resp = self.session.get(
            self._url(f"partstudios/d/{self.did}/w/{self.wid}/e/{eid}/shadedviews"),
            params={
                "viewMatrix": view_matrix,
                "outputHeight": output_height,
                "outputWidth": output_width,
                "pixelSize": 0,
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()

    def get_assembly_definition(self, aeid: str | None = None) -> dict[str, Any]:
        target_aeid = aeid or self.assembly_eid
        resp = self.session.get(
            self._url(f"assemblies/d/{self.did}/w/{self.wid}/e/{target_aeid}"),
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def add_assembly_instance(
        self,
        part_id: str,
        part_studio_eid: str | None = None,
        aeid: str | None = None,
    ) -> dict[str, Any]:
        target_aeid = aeid or self.assembly_eid
        target_pseid = part_studio_eid or self.partstudio_eid
        payload = {
            "documentId": self.did,
            "elementId": target_pseid,
            "partId": part_id,
            "isAssembly": False,
            "isWholePartStudio": False,
        }
        resp = self.session.post(
            self._url(f"assemblies/d/{self.did}/w/{self.wid}/e/{target_aeid}/instances"),
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json() if resp.text else {}
