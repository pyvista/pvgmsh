<h1 align="center">
  <a href="https://github.com/pyvista/scikit-gmsh#--------">
    <img src="https://raw.githubusercontent.com/pyvista/scikit-gmsh/main/docs/_static/logo.svg"
         alt="scikit-gmsh"
         width="200"></a>
</h1>

> Scikit for Gmsh to generate 3D finite element mesh.

[![Status](https://badgen.net/badge/status/alpha/d8624d)](https://badgen.net/badge/status/alpha/d8624d)
[![All Contributors](https://img.shields.io/github/all-contributors/pyvista/scikit-gmsh?color=ee8449)](https://scikit-gmsh.readthedocs.io/en/latest/reference/about.html#contributors)
[![Contributing](https://img.shields.io/badge/PR-Welcome-%23FF8300.svg)](https://github.com/pyvista/scikit-gmsh/issues)
[![Documentation Status](https://readthedocs.org/projects/scikit-gmsh/badge/?version=latest)](https://scikit-gmsh.readthedocs.io/en/latest/?badge=latest)
[![GitHub Repo stars](https://img.shields.io/github/stars/pyvista/scikit-gmsh)](https://github.com/pyvista/scikit-gmsh/stargazers)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Contributor Covenant](https://img.shields.io/badge/contributor%20covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)

The `scikit-gmsh` package provides a simple interface to:

- Christophe Geuzaine and Jean-François Remacle's [Gmsh](https://pypi.org/project/gmsh/)

The library has following main objectives:

1. Provide an intuitive, object-oriented API for mesh creation like [scipy.spatial.Delaunay class](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.Delaunay.html).
1. Integrate seamlessly with other libraries in the [Scientific Python ecosystem](https://scientific-python.org/).

`scikit-gmsh` does not use the PythonAPI of gmsh.
This library provides a Python interface for creating geometry files and executing them with the gmsh command.

## Installation

[![pypi](https://img.shields.io/pypi/v/scikit-gmsh?label=pypi&logo=python&logoColor=white)](https://pypi.org/project/scikit-gmsh/)

```shell
pip install scikit-gmsh
```

## Gallery

Check out the example galleries organized by subject here:

<p align="center">
  <a href="https://scikit-gmsh.readthedocs.io/en/latest/examples/icosahedron.html">
    <img src="https://scikit-gmsh.readthedocs.io/en/latest/_images/sphx_glr_icosahedron_thumb.png" height="190px"/>
  </a>
  <a href="https://scikit-gmsh.readthedocs.io/en/latest/examples/polygon_with_hole.html">
    <img src="https://scikit-gmsh.readthedocs.io/en/latest/_images/sphx_glr_polygon_with_hole_thumb.png" height="190px"/>
  </a>
  <a href="https://scikit-gmsh.readthedocs.io/en/latest/examples/cylinder.html">
    <img src="https://scikit-gmsh.readthedocs.io/en/latest/_images/sphx_glr_cylinder_thumb.png" height="190px"/>
  </a>
  <a href="https://scikit-gmsh.readthedocs.io/en/latest/examples/quad.html">
    <img src="https://scikit-gmsh.readthedocs.io/en/latest/_images/sphx_glr_quad_thumb.png" height="190px"/>
  </a>
</p>

## Other Resources

This library may not meet your needs and if this is this case, consider checking out these other resources:

- [meshwell](https://github.com/simbilod/meshwell) - GMSH wrapper, with integrated photonics focus.
- [objectgmsh](https://github.com/nemocrys/objectgmsh) - Object oriented Gmsh modeling.
- [optimesh](https://github.com/meshpro/optimesh) - Mesh optimization, mesh smoothing.
- [pandamesh](https://github.com/Deltares/pandamesh) - 🐼 From geodataframe to mesh ▦.
- [pygalmesh](https://github.com/meshpro/pygalmesh) - A Python interface to CGAL's meshing tools.
- [pygmsh](https://github.com/nschloe/pygmsh) - Gmsh for Python.

## License

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

This software is published under the [GPLv3 license](https://www.gnu.org/licenses/gpl-3.0.en.html).

## Contributions

Contributions are _very welcome_ .
This project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md).
By participating in this project, We want you to know that you agree to follow its terms.

## Star History

Enjoying scikit-gmsh? Show your support with a [GitHub star](https://github.com/pyvista/scikit-gmsh) — it’s a simple click that means the world to us and helps others discover it, too! ⭐️

[![Star History Chart](https://api.star-history.com/svg?repos=pyvista/scikit-gmsh&type=Date)](https://star-history.com/#pyvista/scikit-gmsh&Date)
