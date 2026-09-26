"""Check pinned packages and exercise meshing, output and a small diode solve.
All generated test files are confined to a temporary directory.
"""
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
MACOS_ONLY_EXCLUDED = {
    'intel-cmplr-lib-ur', 'intel-openmp', 'mkl',
    'onemkl-license', 'tbb', 'tcmlib', 'umf',
}

def main():
    mismatches = []
    for line in (ROOT / 'requirements-lock.txt').read_text(encoding='utf-8-sig').splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        name, expected = line.split('==', 1)
        if sys.platform == 'darwin' and name.lower() in MACOS_ONLY_EXCLUDED:
            continue
        try:
            actual = version(name)
        except PackageNotFoundError:
            actual = 'not installed'
        if actual != expected:
            mismatches.append(f'{name}: expected {expected}, found {actual}')
    if mismatches:
        raise RuntimeError('Package versions differ from requirements-lock.txt:\n' + '\n'.join(mismatches))
    print('PASS: all applicable pinned package versions match.', flush=True)
    import gmsh
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import pyvista as pv
    import meshio
    with tempfile.TemporaryDirectory(prefix='ih2662-setup-') as folder:
        tmp = Path(folder)
        gmsh.initialize()
        try:
            gmsh.option.setNumber('General.Terminal', 0)
            gmsh.model.add('setup_check')
            gmsh.model.occ.addRectangle(0, 0, 0, 1, 1)
            gmsh.model.occ.synchronize()
            gmsh.option.setNumber('Mesh.MeshSizeMax', .25)
            gmsh.model.mesh.generate(2)
            assert len(gmsh.model.mesh.getNodes()[0]) > 0
            gmsh.write(str(tmp / 'check.msh'))
        finally:
            gmsh.finalize()
        mesh = meshio.read(tmp / 'check.msh')
        assert len(mesh.points) > 0
        grid = pv.PolyData(np.array([[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]]), faces=[3,0,1,2])
        grid.save(tmp / 'check.vtp')
        assert pv.read(tmp / 'check.vtp').n_points == 3
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])
        fig.savefig(tmp / 'check.png')
        plt.close(fig)
        assert (tmp / 'check.png').stat().st_size > 0
        print('PASS: Gmsh meshing, meshio, PyVista file output and Matplotlib plotting.', flush=True)
        # Same bundled solver backend as the project; original diode solves in temp.
        program = ('import sys,runpy; sys.path.insert(0,sys.argv[1]); '
                   'import devsim.umfpack.umfshim; runpy.run_path(sys.argv[2],run_name="__main__")')
        example = ROOT / 'examples' / 'diode' / 'diode_1d.py'
        result = subprocess.run([sys.executable, '-c', program, str(example.parent), str(example)],
                                cwd=tmp, env=os.environ.copy(), capture_output=True, text=True, timeout=180)
        if result.returncode:
            raise RuntimeError('DEVSIM diode solve failed:\n' + (result.stdout + result.stderr)[-8000:])
        print('PASS: DEVSIM 1D diode example completed with the project solver backend.', flush=True)
    print('All environment checks passed; simulation results were not modified.', flush=True)

if __name__ == '__main__':
    main()
