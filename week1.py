"""IH2662 Week 1: run packaged official examples and view their results."""
from pathlib import Path
import argparse
import os
import runpy
import sys

ROOT = Path(__file__).resolve().parent
# Configure the MKL runtime before importing DEVSIM, even when run directly.
bin_dir = ROOT / '.venv' / 'Library' / 'bin'
os.environ['PATH'] = str(bin_dir) + os.pathsep + os.environ.get('PATH', '')
os.environ['DEVSIM_MATH_LIBS'] = str(bin_dir / 'mkl_rt.2.dll')
dll_handle = os.add_dll_directory(str(bin_dir))


def official(folder, filename):
    directory = ROOT / 'examples' / folder
    os.chdir(directory)
    sys.path.insert(0, str(directory))
    runpy.run_path(str(directory / filename), run_name='__main__')


def diode():
    official('diode', 'diode_1d.py')
    import devsim as ds
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    args = dict(device='MyDevice', region='MyRegion')
    fields = ['x', 'Potential', 'Electrons', 'Holes', 'NetDoping']
    data = np.column_stack([ds.get_node_model_values(**args, name=f) for f in fields])
    assert np.isfinite(data).all(), 'Non-finite diode results'
    np.savetxt(ROOT / 'results' / 'diode_1d.csv', data, delimiter=',',
               header='x_cm,Potential_V,Electrons_cm-3,Holes_cm-3,NetDoping_cm-3', comments='')
    fig, axes = plt.subplots(2, 1, figsize=(8, 7), sharex=True)
    axes[0].plot(data[:, 0]*1e4, data[:, 1])
    axes[0].set_ylabel('Potential (V)')
    axes[1].semilogy(data[:, 0]*1e4, data[:, 2], label='Electrons')
    axes[1].semilogy(data[:, 0]*1e4, data[:, 3], label='Holes')
    axes[1].set_ylabel('Carrier density (cm^-3)')
    axes[1].set_xlabel('Position (micrometres)')
    axes[1].legend()
    fig.suptitle('Official DEVSIM 1D diode: final forward bias 0.5 V')
    fig.tight_layout()
    fig.savefig(ROOT / 'results' / 'diode_1d.png', dpi=160)
    print('PASS: official diode completed; CSV and plot in results.')


def mesh():
    import gmsh
    directory = ROOT / 'examples' / 'mobility'
    gmsh.initialize()
    try:
        gmsh.open(str(directory / 'gmsh_mos2d.geo'))
        gmsh.option.setNumber('Mesh.MshFileVersion', 2.2)
        gmsh.model.mesh.generate(2)
        # Separate output keeps the packaged reference mesh available.
        gmsh.write(str(directory / 'gmsh_mos2d_generated.msh'))
    finally:
        gmsh.finalize()
    print('PASS: generated a 2D mesh in Gmsh (MSH 2.2).')


def mos():
    official('mobility', 'gmsh_mos2d.py')
    import devsim as ds
    ds.write_devices(file=str(ROOT / 'results' / 'mos2d'), type='vtk')
    print('PASS: official 2D MOSFET solved and exported to results/mos2d.vtm.')


def view(screenshot=False):
    import pyvista as pv
    data = pv.read(ROOT / 'results' / 'mos2d.vtm')
    grid = data.combine()
    plotter = pv.Plotter(off_screen=screenshot)
    plotter.add_mesh(grid, scalars='Potential', show_edges=True, cmap='viridis',
                     scalar_bar_args={'title': 'Potential (V)'})
    plotter.view_xy()
    plotter.add_text('Official DEVSIM 2D MOSFET - final bias', font_size=12)
    if screenshot:
        plotter.show(screenshot=str(ROOT / 'results' / 'mos2d.png'))
        print('PASS: PyVista rendered results/mos2d.png.')
    else:
        plotter.show()


def gmsh_gui():
    import gmsh
    gmsh.initialize()
    try:
        gmsh.open(str(ROOT / 'examples' / 'mobility' / 'gmsh_mos2d_generated.msh'))
        gmsh.fltk.run()
    finally:
        gmsh.finalize()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['diode', 'mesh', 'mos', 'view', 'screenshot', 'gmsh'])
    action = parser.parse_args().action
    {'diode': diode, 'mesh': mesh, 'mos': mos, 'view': view,
     'screenshot': lambda: view(True), 'gmsh': gmsh_gui}[action]()

