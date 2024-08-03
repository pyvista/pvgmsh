"""scikit-gmsh package for 3D mesh generation test."""

from __future__ import annotations

import pyvista as pv

import skgmsh as sg

edge_source = pv.Cylinder(resolution=4)
edge_source.plot(show_edges=True)
mesh = sg.delaunay_3d(edge_source)
mesh.plot(show_edges=True)
