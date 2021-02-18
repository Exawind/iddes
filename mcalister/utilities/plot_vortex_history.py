#!/usr/bin/env python3

# ========================================================================
#
# Imports
#
# ========================================================================
import argparse
import os
import re
import glob as glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import utilities
import definitions as defs


# ========================================================================
#
# Some defaults variables
#
# ========================================================================
plt.rc("text", usetex=True)
plt.rc("figure", max_open_warning=100)
cmap_med = [
    "#F15A60",
    "#7AC36A",
    "#5A9BD4",
    "#FAA75B",
    "#9E67AB",
    "#CE7058",
    "#D77FB4",
    "#737373",
]
cmap = [
    "#EE2E2F",
    "#008C48",
    "#185AA9",
    "#F47D23",
    "#662C91",
    "#A21D21",
    "#B43894",
    "#010202",
]
dashseq = [
    (None, None),
    [10, 5],
    [10, 4, 3, 4],
    [3, 3],
    [10, 4, 3, 4, 3, 4],
    [3, 3],
    [3, 3],
]
markertype = ["s", "d", "o", "p", "h"]


# ========================================================================
#
# Function definitions
#
# ========================================================================


# ========================================================================
#
# Main
#
# ========================================================================
if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="A simple plot tool for vortex history quantities"
    )
    parser.add_argument(
        "-f",
        "--folders",
        nargs="+",
        help="Folder where files are stored",
        type=str,
        required=True,
    )
    parser.add_argument("-l", "--legend", help="Annotate figures", action="store_true")
    args = parser.parse_args()

    # Loop on folders
    for i, folder in enumerate(args.folders):

        # Setup
        fdir = os.path.abspath(folder)
        yname = os.path.join(fdir, "mcalister.yaml")
        half_wing_length = defs.get_half_wing_length()
        xslices = utilities.get_vortex_slices()
        xslices["xslicet"] = xslices.xslice + 1

        # simulation setup parameters
        u0, v0, w0, umag0, rho0, mu, flow_angle = utilities.parse_ic(yname)
        mname = utilities.get_meshname(yname)
        aoa = defs.get_aoa(mname)

        prefix = "output"
        suffix = ".csv"
        pattern = prefix + "*" + suffix
        fnames = sorted(glob.glob(os.path.join(fdir, "vortex_slices", pattern)))
        times = []
        for fname in fnames:
            times.append(int(re.findall(r"\d+", fname)[-1]))
        times = np.unique(sorted(times))

        # Loop over each time step and get the dataframe
        lst = []
        for time in times:
            pattern = prefix + "*." + str(time) + suffix
            fnames = sorted(glob.glob(os.path.join(fdir, "vortex_slices", pattern)))
            df = utilities.get_merged_csv(fnames)
            lst.append(df)
            df["time"] = time
        df = pd.concat(lst, ignore_index=True)
        renames = utilities.get_renames()
        df.columns = [renames[col] for col in df.columns]
        df.z -= half_wing_length

        # Rotation transform
        c, s = np.cos(flow_angle), np.sin(flow_angle)
        x0, y0 = 1, 0
        df["xr"] = c * (df.x - x0) + s * (df.y - y0) + x0
        df["yr"] = -s * (df.x - x0) + c * (df.y - y0) + y0
        df["uxr"] = c * df.ux + s * df.uy
        df["uyr"] = -s * df.ux + c * df.uy

        # Get the vortex core location
        vortex_core = []
        for k, (index, row) in enumerate(xslices.iterrows()):
            for time in times:
                subdf = df[
                    (np.fabs(df.xr - row.xslicet) < 1e-3) & (df.time == time)
                ].copy()

                # vortex center location
                idx = subdf.p.idxmin()
                xc = np.array([subdf.xr.loc[idx]])
                yc = np.array([subdf.yr.loc[idx]])
                zc = np.array([subdf.z.loc[idx]])
                pc = np.array([subdf.p.loc[idx]])
                vortex_core.append([time, row.xslicet, xc[0], yc[0], zc[0], pc[0]])

        vortex_core = pd.DataFrame(
            vortex_core, columns=["time", "slice", "xc", "yc", "zc", "pc"]
        )

        # Plot
        grouped = vortex_core.groupby("slice")
        for k, (name, group) in enumerate(grouped):
            plt.figure(0)
            p = plt.plot(
                group.time,
                np.sqrt(group.yc ** 2 + group.zc ** 2),
                ls="-",
                lw=2,
                color=cmap[k],
                label=f"x={name}",
            )
            p[0].set_dashes(dashseq[i])

            plt.figure(1)
            p = plt.plot(
                group.time, group.pc, ls="-", lw=2, color=cmap[k], label=f"SST {aoa}"
            )
            p[0].set_dashes(dashseq[i])

        # Save plots
        fname = "vortex_history.pdf"
        with PdfPages(fname) as pdf:
            plt.figure(0)
            ax = plt.gca()
            plt.xlabel(r"$s$", fontsize=22, fontweight="bold")
            plt.ylabel(r"$x_c$", fontsize=22, fontweight="bold")
            plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight="bold")
            plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight="bold")
            plt.tight_layout()
            pdf.savefig(dpi=300)

            plt.figure(1)
            ax = plt.gca()
            plt.xlabel(r"$s$", fontsize=22, fontweight="bold")
            plt.ylabel(r"$p$", fontsize=22, fontweight="bold")
            plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight="bold")
            plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight="bold")
            plt.tight_layout()
            pdf.savefig(dpi=300)
