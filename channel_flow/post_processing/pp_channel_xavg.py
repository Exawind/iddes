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
import sys

# ========================================================================
#
# Define constants
#
# ========================================================================

ninterp         = 201
Lx              = 8.0
Ly              = 3.0
Lz              = 2.0
Ox              = 0.0
Oy              = 0.0
Oz              = 0.0

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
        "-navg", help="Number of times to average", default=10, type=int
    )
    parser.add_argument(
        "--flowthrough", help="Flowthrough time (L/u)", default=0.4, type=float
    )
    parser.add_argument(
        "--factor",
        help="Factor of flowthrough time between time steps used in average",
        type=float,
        default=1.2,
    )
    parser.add_argument(
        "-i",
        "--interiorname",
        help="Name of interior block (i.e. fluid-hex)",
        type=str,
        default="fluid-hex",
    )
    parser.add_argument(
        "-sdx",
        help="Streamwise cell length",
        type=float,
        default=0.1,
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
        tsteps[-1] - args.flowthrough * args.factor * np.arange(args.navg)
    )
    dist = np.abs(np.array(tsteps)[:, np.newaxis] - tmp_tavg)
    idx = dist.argmin(axis=0)
    tavg = tsteps[idx]
    tavg_instantaneous = tsteps[idx[0] :]
    printer("Averaging the following steps:")
    printer(tavg)

    # Extract time and spanwise average tau_wall on wall
    tw_data = None
    for tstep in tavg_instantaneous:
        ftime, missing = mesh.stkio.read_defined_input_fields(tstep)
        printer(f"Loading tau_wall fields for time: {ftime}")

        coords = mesh.meta.coordinate_field
        wall = mesh.meta.get_part("wall_bottom")
        sel = wall & mesh.meta.locally_owned_part
        tauw = mesh.meta.get_field("tau_wall")
        names = ["x", "y", "z", "tauw"]
        nnodes = sum(bkt.size for bkt in mesh.iter_buckets(sel, stk.StkRank.NODE_RANK))

        cnt = 0
        data = np.zeros((nnodes, len(names)))
        for bkt in mesh.iter_buckets(sel, stk.StkRank.NODE_RANK):
            xyz = coords.bkt_view(bkt)
            tw = tauw.bkt_view(bkt)
            data[cnt : cnt + bkt.size, :] = np.hstack((xyz, tw.reshape(-1, 1)))
            cnt += bkt.size

        if tw_data is None:
            tw_data = np.zeros(data.shape)
        tw_data += data / len(tavg_instantaneous)

    lst = comm.gather(tw_data, root=0)
    comm.Barrier()
    if rank == 0:
        df = pd.DataFrame(np.vstack(lst), columns=names)
        tw = df.groupby("x", as_index=False).mean().sort_values(by=["x"])
        twname = os.path.join(fdir, "tw.dat")
        tw.to_csv(twname, index=False)


    # Extract (average) velocity data
    vel_data = None
    rij_data = None

    for tstep in tavg:
        ftime, missing = mesh.stkio.read_defined_input_fields(tstep)
        printer(f"Loading fields for time: {ftime}")

        interior = mesh.meta.get_part(args.interiorname)
        sel = interior & mesh.meta.locally_owned_part
        velocity = mesh.meta.get_field(args.vel_name)
        turbvisc = mesh.meta.get_field("turbulent_viscosity")
        turbke = mesh.meta.get_field("turbulent_ke")
        names = ["x", "y", "z", "u", "v", "w", "nut","k"]
        nnodes = sum(bkt.size for bkt in mesh.iter_buckets(sel, stk.StkRank.NODE_RANK))

        cnt = 0
        data = np.zeros((nnodes, len(names)))
        for bkt in mesh.iter_buckets(sel, stk.StkRank.NODE_RANK):
            xyz = coords.bkt_view(bkt)
            vel = velocity.bkt_view(bkt)
            tv = turbvisc.bkt_view(bkt)
            tke = turbke.bkt_view(bkt)
            data[cnt : cnt + bkt.size, :] = np.hstack((xyz, vel, tv.reshape(-1, 1), tke.reshape(-1, 1)))
            cnt += bkt.size

        if vel_data is None:
            vel_data = np.zeros(data.shape)
        vel_data += data / len(tavg)
    
    # Second loop for fluctuating vels
    for tstep in tavg:
        ftime, missing = mesh.stkio.read_defined_input_fields(tstep)
        printer(f"Loading fields for time: {ftime}")

        interior = mesh.meta.get_part(args.interiorname)
        sel = interior & mesh.meta.locally_owned_part
        velocity = mesh.meta.get_field(args.vel_name)
        rijnames = ["x", "y", "z","uu","vv","ww","uv"]
        nnodes = sum(bkt.size for bkt in mesh.iter_buckets(sel, stk.StkRank.NODE_RANK))

        cnt = 0
        rijdata = np.zeros((nnodes, len(rijnames)))
        for bkt in mesh.iter_buckets(sel, stk.StkRank.NODE_RANK):
            xyz = coords.bkt_view(bkt)
            vel = velocity.bkt_view(bkt)
            rijdata[cnt : cnt + bkt.size, :] = np.hstack((xyz, vel, 0*vel[:,0].reshape(-1, 1)))
            cnt += bkt.size

        if rij_data is None:
            rij_data = np.zeros(rijdata.shape)
        rij_data[:,0] = rijdata[:,0] 
        rij_data[:,1] = rijdata[:,1] 
        rij_data[:,2] = rijdata[:,2] 
        rij_data[:,3] += ((rijdata[:,3] - vel_data[:,3])**2) / len(tavg)
        rij_data[:,4] += ((rijdata[:,4] - vel_data[:,4])**2) / len(tavg)
        rij_data[:,5] += ((rijdata[:,5] - vel_data[:,5])**2) / len(tavg)
        rij_data[:,6] += (rijdata[:,3] - vel_data[:,3])*(rijdata[:,4] - vel_data[:,4]) / len(tavg)

    # Subset the velocities on planes
    #dx = 0.05 * 4
    planes = []
    fplanes = []
    dx = args.sdx

    #for x in utilities.xplanes():
    npointsx = (int(Lx/dx)+1)
    xavg = pd.DataFrame()
    fxavg = pd.DataFrame()

    for x in np.linspace(Ox,Lx,num=npointsx):
        print(" === x=%f ==="%x)
        # subset the data around the plane of interest
        sub = vel_data[(x - dx/1.5 <= vel_data[:, 0]) & (vel_data[:, 0] <= x + dx/1.5), :]
        fsub = rij_data[(x - dx/1.5 <= rij_data[:, 0]) & (rij_data[:, 0] <= x + dx/1.5), :]

        sub[:,0] = np.around(np.ones(np.shape(sub[:,0]))*x,decimals=3) 
        sub[:,1] = np.around(sub[:,1],decimals=3) 
        sub[:,2] = np.around(sub[:,2],decimals=6)
        fsub[:,0] = np.around(np.ones(np.shape(fsub[:,0]))*x,decimals=3)
        fsub[:,1] = np.around(fsub[:,1],decimals=4)
        fsub[:,2] = np.around(fsub[:,2],decimals=6)

        lst = comm.gather(sub, root=0)
        flst = comm.gather(fsub, root=0)

        comm.Barrier()
        if rank == 0:
            xi = np.array([x])
            df = (
                pd.DataFrame(np.vstack(lst), columns=names)
                .groupby(["x", "z"], as_index=False)
                .mean()
                .sort_values(by=["x", "z"])
            )
            fdf = (
                pd.DataFrame(np.vstack(flst), columns=rijnames)
                .groupby(["x", "z"], as_index=False)
                .mean()
                .sort_values(by=["x", "z"])
            )
            
            print("npointsx: " + str(npointsx))
            planes.append(df)
            if x == Ox:
                print("First avg")
                xavg = df.div(npointsx)
            if x > Ox:
                print("More avg" + str(xavg.z.max()))
                xavg += df.div(npointsx)
            
            fplanes.append(fdf)
            if x == Ox:
                fxavg = fdf.div(npointsx)
            if x > Ox:
                fxavg += fdf.div(npointsx)
            
    if rank == 0:
        xavg.x = np.around(xavg.x,decimals=3) 
        xavg.z = np.around(xavg.z,decimals=6) 
        xavg.y = np.around(xavg.y,decimals=3)
        fxavg.x = np.around(fxavg.x,decimals=3) 
        fxavg.z = np.around(fxavg.z,decimals=6) 
        fxavg.y = np.around(fxavg.y,decimals=3)

        df = pd.concat(planes)
        df.to_csv(os.path.join(fdir, "profiles.dat"), index=False)
        xavg.to_csv(os.path.join(fdir, "xavg.dat"), index=False)

        fdf = pd.concat(fplanes)
        fdf.to_csv(os.path.join(fdir, "rij_profiles.dat"), index=False)
        fxavg.to_csv(os.path.join(fdir, "rij_xavg.dat"), index=False)
