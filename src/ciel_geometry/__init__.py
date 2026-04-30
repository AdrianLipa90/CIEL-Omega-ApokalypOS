"""ciel_geometry — Poincaré disk geometry engine for CIEL orbital system (Foundation Pack P5+P6).

Submodules:
  loader         — load sectors, couplings, entities, bridge state from integration/
  disk           — Poincaré disk math (radius, distance, geodesic arcs)
  edges          — geodesic edge construction from coupling matrix
  layout         — build_layout() → DiskLayout snapshot
  semantic_mass  — P3: M_sem operator (EC+ZS+dep+prov+exec), Kepler orbit period
  subjective_time— P3: Δτ operator (hyperbolic dilation + coherence + mass)
  renderer_ascii — terminal ASCII render (debug/verification)
  renderer_mpl   — matplotlib interactive cockpit (P6 MVP)
"""

from .layout import DiskLayout, DiskNode, DiskEdge, build_layout

__all__ = ["DiskLayout", "DiskNode", "DiskEdge", "build_layout"]
