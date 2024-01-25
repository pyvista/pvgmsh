"""PvGmsh package for 3D mesh generation."""

from __future__ import annotations

import gmsh
import numpy as np
import pyvista as pv
import scooby
from pygmsh.helpers import extract_to_meshio

FRONTAL_DELAUNAY_2D = 6
DELAUNAY_3D = 1

# major, minor, patch
version_info = 0, 0, "dev0"

# Nice string for the version
__version__ = ".".join(map(str, version_info))


def frontal_delaunay_2d(
    edge_source: pv.PolyData,
    target_size: float | None,
) -> pv.PolyData | None:
    """
    Frontal-Delaunay 2D mesh algorithm.

    Parameters
    ----------
    edge_source : pyvista.PolyData
        Specify the source object used to specify constrained
        edges and loops. If set, and lines/polygons are defined, a
        constrained triangulation is created. The lines/polygons
        are assumed to reference points in the input point set
        (i.e. point ids are identical in the input and
        source).

    target_size : float, optional
        Target mesh size close to the points.
        Default max size of edge_source in each direction.

    Returns
    -------
    pyvista.PolyData
        Mesh from the 2D delaunay generation.

    Examples
    --------
    Use the ``edge_source`` parameter to create a constrained delaunay
    triangulation.

    >>> import pyvista as pv
    >>> import pvgmsh as pm

    >>> edge_source = pv.Polygon(n_sides=4, radius=8, fill=False)
    >>> mesh = pm.frontal_delaunay_2d(edge_source, target_size=2.0)

    >>> mesh
    PolyData (...)
      N Cells:    ...
      N Points:   ...
      N Strips:   0
      X Bounds:   -8.000e+00, 8.000e+00
      Y Bounds:   -8.000e+00, 8.000e+00
      Z Bounds:   0.000e+00, 0.000e+00
      N Arrays:   0

    >>> plotter = pv.Plotter(off_screen=True)
    >>> _ = plotter.add_mesh(mesh, show_edges=True, line_width=4, color="white", lighting=False, edge_color=[153, 153, 153])
    >>> _ = plotter.add_mesh(edge_source, show_edges=True, line_width=4, color=[214, 39, 40])
    >>> _ = plotter.add_points(edge_source.points, style="points", point_size=20, color=[214, 39, 40])
    >>> _ = plotter.add_legend([[" edge source", [214, 39, 40]], [" mesh ", [153, 153, 153]]], bcolor="white", face="r", size=(0.3, 0.3))
    >>> plotter.show(cpos="xy", screenshot="frontal_delaunay_2d_01.png")
    """
    points = edge_source.points
    lines = edge_source.lines
    bounds = edge_source.bounds

    gmsh.initialize()
    gmsh.option.set_number("Mesh.Algorithm", FRONTAL_DELAUNAY_2D)

    if target_size is None:
        target_size = np.max(np.abs(bounds[1] - bounds[0]), np.abs(bounds[3] - bounds[2]), np.abs(bounds[5] - bounds[4]))

    for i, point in enumerate(points):
        id_ = i + 1
        gmsh.model.geo.add_point(point[0], point[1], point[2], target_size, id_)

    for i in range(lines[0] - 1):
        id_ = i + 1
        gmsh.model.geo.add_line(lines[i + 1] + 1, lines[i + 2] + 1, id_)

    gmsh.model.geo.add_curve_loop(range(1, lines[0]), 1)
    gmsh.model.geo.add_plane_surface([1], 1)
    gmsh.model.geo.synchronize()
    gmsh.model.mesh.generate(2)
    mesh = extract_to_meshio()
    gmsh.clear()
    gmsh.finalize()

    for cell in mesh.cells:
        if cell.type == "triangle":
            return pv.PolyData.from_regular_faces(mesh.points, cell.data)
    return None


def delaunay_3d(
    edge_source: pv.PolyData,
    target_size: float | None,
) -> pv.UnstructuredGrid | None:
    """
    Delaunay 3D mesh algorithm.

    Parameters
    ----------
    edge_source : pyvista.PolyData
        Specify the source object used to specify constrained
        edges and loops. If set, and lines/polygons are defined, a
        constrained triangulation is created. The lines/polygons
        are assumed to reference points in the input point set
        (i.e. point ids are identical in the input and
        source).

    target_size : float
        Target mesh size close to the points.

    Returns
    -------
    pyvista.UnstructuredGrid
        Mesh from the 3D delaunay generation.

    Examples
    --------
    >>> import pyvista as pv
    >>> import pvgmsh as pm

    >>> edge_source = pv.Cube()
    >>> mesh = pm.delaunay_3d(edge_source, target_size=0.4)

    >>> mesh
    UnstructuredGrid (...)
      N Cells:    ...
      N Points:   ...
      X Bounds:   -5.000e-01, 5.000e-01
      Y Bounds:   -5.000e-01, 5.000e-01
      Z Bounds:   -5.000e-01, 5.000e-01
      N Arrays:   0

    >>> plotter = pv.Plotter(off_screen=True)
    >>> _ = plotter.add_mesh(mesh, show_edges=True, line_width=4, color="white", lighting=False, edge_color=[153, 153, 153])
    >>> _ = plotter.add_mesh(edge_source.extract_all_edges(), line_width=4, color=[214, 39, 40])
    >>> _ = plotter.add_points(edge_source.points, style="points", point_size=20, color=[214, 39, 40])
    >>> plotter.enable_parallel_projection()
    >>> _ = plotter.add_axes(
    ...     box=True,
    ...     box_args={
    ...         "opacity": 0.5,
    ...         "color_box": True,
    ...         "x_face_color": "white",
    ...         "y_face_color": "white",
    ...         "z_face_color": "white",
    ...     },
    ... )
    >>> plotter.show(screenshot="delaunay_3d_01.png")
    """
    points = edge_source.points
    faces = edge_source.regular_faces

    gmsh.initialize()
    gmsh.option.set_number("Mesh.Algorithm3D", DELAUNAY_3D)

    for i, point in enumerate(points):
        id_ = i + 1
        gmsh.model.geo.add_point(point[0], point[1], point[2], target_size, id_)

    surface_loop = []
    for i, face in enumerate(faces):
        gmsh.model.geo.add_line(face[0] + 1, face[1] + 1, i * 4 + 0)
        gmsh.model.geo.add_line(face[1] + 1, face[2] + 1, i * 4 + 1)
        gmsh.model.geo.add_line(face[2] + 1, face[3] + 1, i * 4 + 2)
        gmsh.model.geo.add_line(face[3] + 1, face[0] + 1, i * 4 + 3)
        gmsh.model.geo.add_curve_loop([i * 4 + 0, i * 4 + 1, i * 4 + 2, i * 4 + 3], i + 1)
        gmsh.model.geo.add_plane_surface([i + 1], i + 1)
        gmsh.model.geo.remove_all_duplicates()
        gmsh.model.geo.synchronize()
        surface_loop.append(i + 1)

    gmsh.model.geo.add_surface_loop(surface_loop, 1)
    gmsh.model.geo.add_volume([1], 1)

    gmsh.model.geo.synchronize()
    gmsh.model.mesh.generate(3)

    mesh = pv.wrap(extract_to_meshio())
    gmsh.clear()
    gmsh.finalize()

    ind = []
    for i, cell in enumerate(mesh.cell):
        if cell.type != pv.CellType.TETRA:
            ind.append(i)
    mesh = mesh.remove_cells(ind)
    mesh.clear_data()

    return mesh


PACKAGES_CORE: list[str] = [
    "matplotlib",
    "numpy",
    "pooch",
    "pyvista",
    "scooby",
    "vtk",
    "gmsh",
    "meshio",
    "pygmsh",
    "pyvista",
]

PACKAGES_OPTIONAL: list[str] = [
    "imageio",
    "pyvistaqt",
    "PyQt5",
    "IPython",
    "colorcet",
    "cmocean",
    "ipywidgets",
    "scipy",
    "tqdm",
    "jupyterlab",
    "pytest_pyvista",
    "trame",
    "trame_client",
    "trame_server",
    "trame_vtk",
    "trame_vuetify",
    "jupyter_server_proxy",
    "nest_asyncio",
]


class Report(scooby.Report):  # type: ignore[misc]
    """
    Generate an environment package and hardware report.

    Parameters
    ----------
    ncol : int, default: 3
        Number of package-columns in html table; only has effect if
        ``mode='HTML'`` or ``mode='html'``.

    text_width : int, default: 80
        The text width for non-HTML display modes.

    """

    def __init__(self: Report, ncol: int = 3, text_width: int = 80) -> None:  # numpydoc ignore=PR01
        """Generate a :class:`scooby.Report` instance."""
        # mandatory packages
        core = PACKAGES_CORE

        # optional packages
        optional = PACKAGES_OPTIONAL

        extra_meta = [
            ("GPU Details", "None"),
        ]

        super().__init__(
            core=core,
            optional=optional,
            ncol=ncol,
            text_width=text_width,
            extra_meta=extra_meta,
        )
