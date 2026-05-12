"""Build HDF5 seed store for CIEL-LNS/Ω."""
from __future__ import annotations

import json
from pathlib import Path

import h5py
import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def build() -> Path:
    nodes = json.loads((ROOT / "data/json/seed_nodes.json").read_text(encoding="utf-8"))
    relations = json.loads((ROOT / "data/json/seed_relations.json").read_text(encoding="utf-8"))
    out = ROOT / "data/hdf5/ciel_lingophysics_seed.h5"
    out.parent.mkdir(parents=True, exist_ok=True)

    axes = ["truth", "care", "creation", "value", "agency", "polarity", "temporality", "identity"]
    axis_index = {a: i for i, a in enumerate(axes)}

    with h5py.File(out, "w") as h5:
        h5.attrs["ciel_lns_version"] = "0.6.0-draft"
        h5.attrs["description"] = "Handcrafted seed store for CIEL-LNS/Ω lingophysics."
        h5.create_dataset("axes", data=np.array(axes, dtype=h5py.string_dtype("utf-8")))

        g_nodes = h5.create_group("nodes")
        ids = np.array([n["id"] for n in nodes], dtype=h5py.string_dtype("utf-8"))
        labels = np.array([n["surface"]["label"] for n in nodes], dtype=h5py.string_dtype("utf-8"))
        languages = np.array([n["language"] for n in nodes], dtype=h5py.string_dtype("utf-8"))
        masses = np.array([n.get("semantic_mass", {}).get("m_s", 0.0) for n in nodes], dtype="f8")
        phases = np.zeros((len(nodes), len(axes)), dtype="f8")
        for i, n in enumerate(nodes):
            for axis, value in n.get("phase", {}).items():
                if axis in axis_index:
                    phases[i, axis_index[axis]] = float(value)
        g_nodes.create_dataset("ids", data=ids)
        g_nodes.create_dataset("labels", data=labels)
        g_nodes.create_dataset("languages", data=languages)
        g_nodes.create_dataset("semantic_mass", data=masses)
        g_nodes.create_dataset("phases", data=phases)

        g_rel = h5.create_group("relations")
        g_rel.create_dataset("ids", data=np.array([r["id"] for r in relations], dtype=h5py.string_dtype("utf-8")))
        g_rel.create_dataset("source", data=np.array([r["source"] for r in relations], dtype=h5py.string_dtype("utf-8")))
        g_rel.create_dataset("target", data=np.array([r["target"] for r in relations], dtype=h5py.string_dtype("utf-8")))
        g_rel.create_dataset("types", data=np.array([r["type"] for r in relations], dtype=h5py.string_dtype("utf-8")))
        g_rel.create_dataset("axes", data=np.array([r.get("axis", "") for r in relations], dtype=h5py.string_dtype("utf-8")))
        g_rel.create_dataset("weights", data=np.array([r.get("weight", 0.0) for r in relations], dtype="f8"))
        g_rel.create_dataset("phase_delta", data=np.array([r.get("phase_delta", 0.0) for r in relations], dtype="f8"))

    return out


if __name__ == "__main__":
    print(build())
