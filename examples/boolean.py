"""Boolean operations on a sphere, a box and two cylinders."""

# This reimplements gmsh/examples/boolean/boolean.geo in Python.
from __future__ import annotations

import sys

import gmsh
import pyvista as pv

R = 1.4
Rs = R * 0.7
Rt = R * 1.25

# %%
# Behavior due to flipped normals
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Note that these boolean filters behave differently depending on the
# orientation of the normals.
#
# Boolean difference with both cube and sphere normals pointed
# outward.  This is the "normal" behavior.

cube = pv.Cube().triangulate().subdivide(3)
sphere = pv.Sphere(radius=0.6)
result = cube.boolean_difference(sphere)
result.plot(show_edges=True, color="white")

gmsh.initialize(sys.argv)

gmsh.model.add("boolean")

# from http://en.wikipedia.org/wiki/Constructive_solid_geometry

gmsh.option.setNumber("Mesh.Algorithm", 6)
gmsh.option.setNumber("Mesh.MeshSizeMin", 0.4)
gmsh.option.setNumber("Mesh.MeshSizeMax", 0.4)

gmsh.model.occ.addBox(-R, -R, -R, 2 * R, 2 * R, 2 * R, 1)
gmsh.model.occ.addSphere(0, 0, 0, Rt, 2)
gmsh.model.occ.intersect([(3, 1)], [(3, 2)], 3)
gmsh.model.occ.addCylinder(-2 * R, 0, 0, 4 * R, 0, 0, Rs, 4)
gmsh.model.occ.addCylinder(0, -2 * R, 0, 0, 4 * R, 0, Rs, 5)
gmsh.model.occ.addCylinder(0, 0, -2 * R, 0, 0, 4 * R, Rs, 6)
gmsh.model.occ.fuse([(3, 4), (3, 5)], [(3, 6)], 7)
gmsh.model.occ.cut([(3, 3)], [(3, 7)], 8)

gmsh.model.occ.synchronize()

gmsh.model.mesh.generate(3)

gmsh.write("boolean.msh")

gmsh.finalize()

mesh = pv.read("boolean.msh")
mesh.plot(show_edges=True, color="white")
