#!/usr/bin/env python3

# ========================================================================
#
# Imports
#
# ========================================================================
import argparse
import os
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
# Main
#
# ========================================================================
if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(description="A simple plot tool for wing forces")
    parser.add_argument("-s", "--show", help="Show the plots", action="store_true")
    parser.add_argument(
        "-f",
        "--folders",
        nargs="+",
        help="Folder where files are stored",
        type=str,
        required=True,
    )
    args = parser.parse_args()

    # Loop on folders
    for k, folder in enumerate(args.folders):

        # Setup
        fdir = os.path.abspath(folder)
        yname = os.path.join(fdir, "mcalister.yaml")
        oname = os.path.join(fdir, "forces.dat")
        df = pd.read_csv(oname, delim_whitespace=True)
        dim = defs.get_dimension(yname)

        u0, v0, w0, umag0, rho0, mu, flow_angle = utilities.parse_ic(yname)
        dynPres = rho0 * 0.5 * (umag0 ** 2)
        mname = utilities.get_meshname(yname)
        aoa = defs.get_aoa(mname)

        # Multiply area by 2 if mesh is full wing
        area = (
            2 * defs.get_wing_area(dim)
            if "mirror" in mname
            else defs.get_wing_area(dim)
        )

        # Lift and drag (rotate in to flow if necessary)
        c, s = np.cos(flow_angle), np.sin(flow_angle)
        df["cl"] = ((df.Fpy + df.Fvy) * c - (df.Fpx + df.Fvx) * s) / (dynPres * area)
        df["cd"] = ((df.Fpy + df.Fvy) * s + (df.Fpx + df.Fvx) * c) / (dynPres * area)
        print(f"""Final cl: {df.cl.iloc[-1]}""")
        print(f"""Final cd: {df.cd.iloc[-1]}""")

        # Experimental values
        edir = os.path.abspath(os.path.join("exp_data", f"aoa-{aoa}"))
        df_cl_cd = pd.read_csv(os.path.join(edir, "cl_cd.txt"), comment="#")
        cl_exp = df_cl_cd.cl.iloc[0]
        cd_exp = df_cl_cd.cd.iloc[0]
        print(f"""Experimental cl: {cl_exp}""")
        print(f"""Experimental cd: {cd_exp}""")

        plt.figure(0)
        p = plt.plot(
            df.Time, df.cl, ls="-", lw=2, color=cmap[k], label=f"SST {aoa} {dim}D"
        )
        p[0].set_dashes(dashseq[k])
        if k == 0:
            plt.plot(
                [df.Time.min(), df.Time.max()],
                [cl_exp, cl_exp],
                lw=1,
                color=cmap[-1],
                label="Exp.",
            )

        plt.figure(1)
        p = plt.plot(
            df.Time, df.cd, ls="-", lw=2, color=cmap[k], label=f"SST {aoa} {dim}D"
        )
        p[0].set_dashes(dashseq[k])
        if k == 0:
            plt.plot(
                [df.Time.min(), df.Time.max()],
                [cd_exp, cd_exp],
                lw=1,
                color=cmap[-1],
                label="Exp.",
            )

    fname = "wing_forces.pdf"
    with PdfPages(fname) as pdf:
        # Format plots
        plt.figure(0)
        ax = plt.gca()
        plt.xlabel(r"$t$", fontsize=22, fontweight="bold")
        plt.ylabel(r"$c_l$", fontsize=22, fontweight="bold")
        plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight="bold")
        plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight="bold")
        plt.ylim([0.5, 1.5])
        # plt.ylim([0.2, 0.5])
        plt.tight_layout()
        legend = ax.legend(loc="best")
        pdf.savefig(dpi=300)

        plt.figure(1)
        ax = plt.gca()
        plt.xlabel(r"$t$", fontsize=22, fontweight="bold")
        plt.ylabel(r"$c_d$", fontsize=22, fontweight="bold")
        plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight="bold")
        plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight="bold")
        plt.ylim([0.02, 0.1])
        # plt.ylim([0.0, 0.1])
        plt.tight_layout()
        pdf.savefig(dpi=300)

    if args.show:
        plt.show()
