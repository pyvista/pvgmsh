"""scikit-gmsh package for 3D mesh generation."""

from __future__ import annotations

import datetime
from pathlib import Path
import subprocess
from typing import TYPE_CHECKING
from typing import Optional

import gmsh
import numpy as np
from pygmsh.helpers import extract_to_meshio
import pyvista as pv
import scooby
import shapely

if TYPE_CHECKING:
    from collections.abc import Sequence

    from numpy.typing import ArrayLike

INITIAL_MESH_ONLY_2D = 3
FRONTAL_DELAUNAY_2D = 6
DELAUNAY_3D = 1
INITIAL_MESH_ONLY_3D = 3

SILENT = 0
SIMPLE = 0

TRUE = 1
FALSE = 0

now = datetime.datetime.now(tz=datetime.timezone.utc)

# major, minor, patch
version_info = 0, 3, "dev0"

# Nice string for the version
__version__ = ".".join(map(str, version_info))


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
        core: list[str] = [
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

        # optional packages
        optional: list[str] = [
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


def delaunay_3d(
    edge_source: pv.PolyData,
    target_sizes: float | Sequence[float] | None = None,
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

    target_sizes : float | Sequence[float]
        Target mesh size close to the points.

    Returns
    -------
    pyvista.UnstructuredGrid
        Mesh from the 3D delaunay generation.

    Notes
    -----
    .. versionadded:: 0.2.0

    """
    points = edge_source.points
    faces = edge_source.irregular_faces

    gmsh.initialize()
    if target_sizes is None:
        gmsh.option.set_number("Mesh.Algorithm", INITIAL_MESH_ONLY_3D)
        gmsh.option.set_number("Mesh.MeshSizeExtendFromBoundary", 0)
        gmsh.option.set_number("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.set_number("Mesh.MeshSizeFromCurvature", 0)
    else:
        gmsh.option.set_number("Mesh.Algorithm3D", DELAUNAY_3D)
    gmsh.option.set_number("General.Verbosity", SILENT)
    gmsh.option.set_number("Mesh.AlgorithmSwitchOnFailure", FALSE)
    gmsh.option.set_number("Mesh.RecombinationAlgorithm", SIMPLE)
    gmsh.option.set_number("Mesh.RecombineNodeRepositioning", FALSE)

    if target_sizes is None:
        target_sizes = 0.0

    if isinstance(target_sizes, float):
        target_sizes = [target_sizes] * edge_source.number_of_points

    for i, (point, target_size) in enumerate(zip(points, target_sizes)):
        id_ = i + 1
        gmsh.model.geo.add_point(point[0], point[1], point[2], target_size, id_)

    surface_loop = []
    for i, face in enumerate(faces):
        curve_tags = []
        for j, _ in enumerate(face):
            start_tag = face[j - 1] + 1
            end_tag = face[j] + 1
            curve_tag = gmsh.model.geo.add_line(start_tag, end_tag)
            curve_tags.append(curve_tag)
        gmsh.model.geo.add_curve_loop(curve_tags, i + 1)
        gmsh.model.geo.add_plane_surface([i + 1], i + 1)
        surface_loop.append(i + 1)

    gmsh.model.geo.remove_all_duplicates()
    gmsh.model.geo.synchronize()

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


def frontal_delaunay_2d(  # noqa: C901, PLR0912
    edge_source: pv.PolyData | shapely.geometry.Polygon,
    target_sizes: float | ArrayLike | None = None,
    recombine: bool = False,  # noqa: FBT001, FBT002
) -> pv.UnstructuredGrid | None:
    """
    Frontal-Delaunay 2D mesh algorithm.

    Parameters
    ----------
    edge_source : pyvista.PolyData | shapely.geometry.Polygon
        Specify the source object used to specify constrained
        edges and loops. If set, and lines/polygons are defined, a
        constrained triangulation is created. The lines/polygons
        are assumed to reference points in the input point set
        (i.e. point ids are identical in the input and
        source).

    target_sizes : float | ArrayLike
        Target mesh size close to the points.
        Default max size of edge_source in each direction.

    recombine : bool
        Recombine the generated mesh into quadrangles.

    Returns
    -------
    pyvista.UnstructuredGrid
        Mesh from the 2D delaunay generation.

    Notes
    -----
    .. versionadded:: 0.2.0

    """
    gmsh.initialize()
    if target_sizes is None:
        gmsh.option.set_number("Mesh.Algorithm", INITIAL_MESH_ONLY_2D)
        gmsh.option.set_number("Mesh.MeshSizeExtendFromBoundary", 0)
        gmsh.option.set_number("Mesh.MeshSizeFromPoints", 0)
        gmsh.option.set_number("Mesh.MeshSizeFromCurvature", 0)
    else:
        gmsh.option.set_number("Mesh.Algorithm", FRONTAL_DELAUNAY_2D)
    gmsh.option.set_number("General.Verbosity", SILENT)

    if target_sizes is None:
        target_sizes = 0.0

    if isinstance(edge_source, shapely.geometry.Polygon):
        wire_tags = []

        if isinstance(target_sizes, float):
            target_sizes = [target_sizes] * (len(edge_source.interiors) + 1)

        for target_size, linearring in zip(target_sizes, [edge_source.exterior, *list(edge_source.interiors)]):
            sizes = [target_size] * (len(linearring.coords) - 1) if isinstance(target_size, float) else target_size
            coords = linearring.coords[:-1].copy()
            tags = []
            for size, coord in zip(sizes, coords):
                x, y, z = coord
                tags.append(gmsh.model.geo.add_point(x, y, z, size))
            curve_tags = []
            for i, _ in enumerate(tags):
                start_tag = tags[i - 1]
                end_tag = tags[i]
                curve_tags.append(gmsh.model.geo.add_line(start_tag, end_tag))
            wire_tags.append(gmsh.model.geo.add_curve_loop(curve_tags))
        gmsh.model.geo.add_plane_surface(wire_tags)
        gmsh.model.geo.synchronize()
    else:
        points = edge_source.points
        lines = edge_source.lines

        if isinstance(target_sizes, float):
            target_sizes = [target_sizes] * edge_source.number_of_points

        embedded_points = []
        for target_size, point in zip(target_sizes, points):
            embedded_points.append(gmsh.model.geo.add_point(point[0], point[1], point[2], target_size))

        for i in range(lines[0] - 1):
            id_ = i + 1
            gmsh.model.geo.add_line(lines[i + 1] + 1, lines[i + 2] + 1, id_)

        gmsh.model.geo.add_curve_loop(range(1, lines[0]), 1)
        gmsh.model.geo.add_plane_surface([1], 1)
        gmsh.model.geo.synchronize()
        gmsh.model.mesh.embed(0, embedded_points, 2, 1)

    if recombine:
        gmsh.model.mesh.set_recombine(2, 1)

    gmsh.model.mesh.generate(2)
    mesh = pv.from_meshio(extract_to_meshio())
    gmsh.clear()
    gmsh.finalize()

    ind = []
    for index, cell in enumerate(mesh.cell):
        if cell.type in [pv.CellType.VERTEX, pv.CellType.LINE]:
            ind.append(index)

    return mesh.remove_cells(ind)


class Delaunay2D:
    """
    Delaunay 2D mesh algorithm.

    Parameters
    ----------
    edge_source : pyvista.PolyData | shapely.Polygon
        Specify the source object used to specify constrained
        edges and loops. If set, and lines/polygons are defined, a
        constrained triangulation is created. The lines/polygons
        are assumed to reference points in the input point set
        (i.e. point ids are identical in the input and
        source).

    shell : sequence
        A sequence of (x, y [,z]) numeric coordinate pairs or triples, or
        an array-like with shape (N, 2) or (N, 3).
        Also can be a sequence of Point objects.

    holes : sequence
        A sequence of objects which satisfy the same requirements as the
        shell parameters above.

    cell_size : float | ArrayLike
       Meshing constraint at point.

    constrain_edge_size : bool
        If True, cell size at points are set to their maximum edge length.

    Notes
    -----
    .. versionadded:: 0.2.0

    """

    def __init__(
        self: Delaunay2D,
        *,
        edge_source: pv.PolyData | shapely.Polygon | None = None,
        shell: Sequence[tuple[int]] | None = None,
        holes: Sequence[tuple[int]] | None = None,
        cell_size: float | ArrayLike | None = None,
        constrain_edge_size: bool = False,
    ) -> None:
        """Initialize the Delaunay2D class."""
        if edge_source is not None:
            self._edge_source = edge_source
        else:
            self._edge_source = shapely.Polygon(shell, holes)

        if constrain_edge_size:
            if isinstance(self.edge_source, shapely.Polygon):
                cell_size = [self._compute_cell_size_from_points(self.edge_source.exterior.coords)]
                cell_size += [self._compute_cell_size_from_points(hole.coords) for hole in self.edge_source.interiors]

            else:
                # Only the first line is processed
                lines = edge_source.lines
                line = lines[1 : lines[0] + 1]
                edge_points = edge_source.points[line]
                cell_size = self._compute_cell_size_from_points(edge_points)

        self._cell_size = cell_size

    @staticmethod
    def _compute_cell_size_from_points(points: ArrayLike) -> ArrayLike:
        """Compute cell size from points array."""
        lengths = np.linalg.norm(np.diff(points, axis=0), axis=-1)
        lengths = np.insert(lengths, 0, lengths[-1])

        return np.maximum(lengths[:-1], lengths[1:])

    @property
    def edge_source(self: Delaunay2D) -> pv.PolyData | shapely.geometry.Polygon:
        """Get the edge source."""
        return self._edge_source

    @property
    def mesh(self: Delaunay2D) -> pv.PolyData:
        """Get the mesh."""
        mesh = frontal_delaunay_2d(self._edge_source, target_sizes=self._cell_size)
        return pv.PolyData(mesh.points, mesh.cells)

    @property
    def cell_size(self: Delaunay2D) -> float | ArrayLike | None:
        """Get the cell_size of the mesh."""
        return self._cell_size

    @cell_size.setter
    def cell_size(self: Delaunay2D, size: float | ArrayLike | None) -> None:
        """Set the cell_size of the mesh."""
        self._cell_size = size


class Delaunay3D:
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

    Notes
    -----
    .. versionadded:: 0.2.0

    """

    def __init__(
        self: Delaunay3D,
        edge_source: pv.PolyData,
        cell_size: float | None = None,
    ) -> None:
        """Initialize the Delaunay3D class."""
        self._edge_source = edge_source
        self._cell_size = cell_size

    @property
    def edge_source(self: Delaunay3D) -> pv.PolyData:
        """Get the edge source."""
        return self._edge_source

    @property
    def mesh(self: Delaunay3D) -> pv.UnstructuredGrid:
        """Get the mesh."""
        self._mesh = delaunay_3d(self.edge_source, target_sizes=self.cell_size)
        return self._mesh

    @property
    def cell_size(self: Delaunay3D) -> float | None:
        """Get the cell_size of the mesh."""
        return self._cell_size

    @cell_size.setter
    def cell_size(self: Delaunay3D, size: int) -> None:
        """Set the cell_size of the mesh."""
        self._cell_size = size


class Delaunay2D2:
    """Delaunay2D class."""

    def __init__(self, shell: shapely.Polygon, holes: Optional[list[shapely.Polygon]] = None) -> None:
        """Create a Delaunay2D object."""
        self.shell = shapely.Polygon(shell)
        self.holes = [shapely.Polygon(hole) for hole in holes] if holes else []
        self._generate_mesh()

    def _generate_mesh(self) -> None:
        cell_size = 0.05
        with Path("quad.geo").open("w") as f:
            for linearring in [self.shell.exterior, *list(self.shell.interiors), *self.holes]:
                coords = linearring.coords[:-1].copy()
                for i, coord in enumerate(coords):
                    x = coord[0]
                    y = coord[1]
                    z = coord[2]
                    f.write("Point(" + str(i + 1) + ") = {" + str(x) + "," + str(y) + "," + str(z) + "," + str(cell_size) + "};\n")
                for i, _ in enumerate(coords[:-1]):
                    f.write("Line(" + str(i + 1) + ") = {" + str(i + 1) + ", " + str(i + 2) + "};\n")
                f.write("Line(" + str(len(coords)) + ") = {" + str(len(coords)) + ", 1};\n")
                f.write("Line Loop(1) = {")
                for i in range(len(coords) - 1):
                    f.write(str(i + 1) + ", ")
                f.write(str(len(coords)) + "};\n")
                f.write("Plane Surface(1) = {1};\n")
        subprocess.run(["gmsh", "quad.geo", "-2", "-o", "quad.vtk"], check=False)  # noqa: S603, S607
        self.mesh = pv.read("quad.vtk")
