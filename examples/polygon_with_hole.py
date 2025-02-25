r"""
Polygon with hole geometry example
----------------------------------

Polygon with hole geometry example.

"""

# sphinx_gallery_thumbnail_number = 2 # noqa:ERA001

from __future__ import annotations

import skgmsh as sg

shell = [(0, 0, 0), (0, 10, 0), (10, 10, 0), (10, 0, 0), (0, 0, 0)]
holes = [[(2, 2, 0), (2, 4, 0), (4, 4, 0), (4, 2, 0), (2, 2, 0)]]
alg = sg.Delaunay2D2(shell=shell, holes=holes)

# %%
# Generate the mesh.

alg.mesh.plot(show_edges=True, cpos="xy", color="white", line_width=2)

# %%
# Change the cell size of the mesh.

alg.cell_size = 2.0
alg.mesh.plot(show_edges=True, cpos="xy", color="white", line_width=2)
