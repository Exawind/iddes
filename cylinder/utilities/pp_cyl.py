# ========================================================================
#
# Imports
#
# ========================================================================
import argparse
import os
import numpy as np
import scipy.spatial.qhull as qhull
import pandas as pd
from mpi4py import MPI
import stk
from scipy.interpolate import griddata


# ========================================================================
#
# Functions
#
# ========================================================================
def p0_printer(par):
    iproc = par.rank

    def printer(*args, **kwargs):
        if iproc == 0:
            print(*args, **kwargs)

    return printer


# ========================================================================
def interp_weights(xyz, uvw):
    """Find the interpolation weights

    See: https://stackoverflow.com/questions/20915502/speedup-scipy-griddata-for-multiple-interpolations-between-two-irregular-grids
    """
    d = 3
    tri = qhull.Delaunay(xyz)
    simplex = tri.find_simplex(uvw)
    vertices = np.take(tri.simplices, simplex, axis=0)
    temp = np.take(tri.transform, simplex, axis=0)
    delta = uvw - temp[:, d]
    bary = np.einsum("njk,nk->nj", temp[:, :d, :], delta)
    return vertices, np.hstack((bary, 1 - bary.sum(axis=1, keepdims=True)))


# ========================================================================
def interpolate(values, vtx, wts):
    return np.einsum("nj,nj->n", np.take(values, vtx), wts)


# ========================================================================
#
# Main
#
# ========================================================================
if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(description="A simple post-processing tool")
    parser.add_argument(
        "-m",
        "--mfile",
        help="Root name of files to postprocess",
        required=True,
        type=str,
    )
    parser.add_argument("--auto_decomp", help="Auto-decomposition", action="store_true")
    parser.add_argument(
        "-v",
        "--vel_name",
        help="Name of the velocity field",
        default="velocity",
        type=str,
    )
    parser.add_argument(
        "-tavg", help="Time to average over to average", default=10, type=int
    )
    args = parser.parse_args()

    fdir = os.path.dirname(args.mfile)

    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    par = stk.Parallel.initialize()
    printer = p0_printer(par)

    mesh = stk.StkMesh(par)
    printer("Reading meta data for mesh: ", args.mfile)
    mesh.read_mesh_meta_data(args.mfile, auto_decomp=args.auto_decomp)
    printer("Done reading meta data")

    printer("Loading bulk data for mesh: ", args.mfile)
    mesh.populate_bulk_data()
    printer("Done reading bulk data")

    num_time_steps = mesh.stkio.num_time_steps
    max_time = mesh.stkio.max_time
    tsteps = np.array(mesh.stkio.time_steps)
    printer(f"""Num. time steps = {num_time_steps}\nMax. time step  = {max_time}""")

    # Figure out the times over which to average
    tmp_tavg = np.sort(
        tsteps[-1] - np.arange(args.tavg)
    )
    dist = np.abs(np.array(tsteps)[:, np.newaxis] - tmp_tavg)
    idx = dist.argmin(axis=0)
    tavg = tsteps[idx]
    tavg_instantaneous = tsteps[idx[0] :]
    printer("Averaging the following steps:")
    printer(tavg)

    # Extract time and spanwise average pressure on wall
    p_data = None
    for tstep in tavg_instantaneous:
        ftime, missing = mesh.stkio.read_defined_input_fields(tstep)
        printer(f"Loading pressure fields for time: {ftime}")

        coords = mesh.meta.coordinate_field
        wall = mesh.meta.get_part("cylinder")
        sel = wall & mesh.meta.locally_owned_part
        press = mesh.meta.get_field("pressure")
        names = ["x", "y", "z", "pressure"]
        nnodes = sum(bkt.size for bkt in mesh.iter_buckets(sel, stk.StkRank.NODE_RANK))

        cnt = 0
        data = np.zeros((nnodes, len(names)))
        for bkt in mesh.iter_buckets(sel, stk.StkRank.NODE_RANK):
            xyz = coords.bkt_view(bkt)
            tw = press.bkt_view(bkt)
            data[cnt : cnt + bkt.size, :] = np.hstack((xyz, tw.reshape(-1, 1)))
            cnt += bkt.size

        if p_data is None:
            p_data = np.zeros(data.shape)
        p_data += data / len(tavg_instantaneous)

    lst = comm.gather(p_data, root=0)
    comm.Barrier()
    if rank == 0:
        # Save x, y, z, P file
        df = pd.DataFrame(np.vstack(lst), columns=names)
        P = df.groupby("x", as_index=False).mean().sort_values(by=["x"])
        fname = os.path.join(fdir, "cylpressure.dat")
        P.to_csv(fname, index=False)

