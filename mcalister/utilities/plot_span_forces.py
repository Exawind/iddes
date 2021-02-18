#!/usr/bin/env python3

# ========================================================================
#
# Imports
#
# ========================================================================
import argparse
import os
import glob as glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import scipy.interpolate as spi
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
# Main
#
# ========================================================================
if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="A simple plot tool for span quantities"
    )
    parser.add_argument("-s", "--show", help="Show the plots", action="store_true")
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
        fname = os.path.join(fdir, "span_forces", "output.csv")

        # Simulation setup parameters
        u0, v0, w0, umag0, rho0, mu, flow_angle = utilities.parse_ic(yname)
        dynPres = rho0 * 0.5 * (umag0 ** 2)
        mname = utilities.get_meshname(yname)
        aoa = defs.get_aoa(mname)
        half_wing_length = defs.get_half_wing_length()

        # Nalu data
        df = pd.read_csv(fname)
        df["cl"] = (df.pfy + df.vfy) / (dynPres * df.area)
        df["cd"] = (df.pfx + df.vfx) / (dynPres * df.area)
        print(f"Integrated cl: {np.sum(df.cl*df.area)/3.3}")
        print(f"Integrated cd: {np.sum(df.cd*df.area)/3.3}")

        plt.figure("cl")
        p = plt.plot(df.z / half_wing_length, df.cl, ls="-", lw=2, color=cmap[0])
        p[0].set_dashes(dashseq[i])

        plt.figure("cd")
        p = plt.plot(df.z / half_wing_length, df.cd, ls="-", lw=2, color=cmap[0])
        p[0].set_dashes(dashseq[i])

        # Experimental data
        edir = os.path.abspath(os.path.join("exp_data", f"aoa-{aoa}"))
        exp_span = pd.read_csv(os.path.join(edir, "cl_cd_vs_y.txt"))
        print(f"Integrated exp cl: {np.trapz(exp_span.cl, exp_span.y)}")
        print(f"Integrated exp cd: {np.trapz(exp_span.cd, exp_span.y)}")

        plt.figure("cl")
        plt.plot(
            exp_span.y,
            exp_span.cl,
            ls="",
            color=cmap[-1],
            marker=markertype[0],
            ms=6,
            mec=cmap[-1],
            mfc=cmap[-1],
            label="Exp.",
        )

        plt.figure("cd")
        plt.plot(
            exp_span.y,
            exp_span.cd,
            ls="",
            color=cmap[-1],
            marker=markertype[0],
            ms=6,
            mec=cmap[-1],
            mfc=cmap[-1],
            label="Exp.",
        )

        # Save plots
        fname = "span_forces.pdf"
        with PdfPages(fname) as pdf:
            plt.figure("cl")
            ax = plt.gca()
            plt.xlabel(r"$z/c$", fontsize=22, fontweight="bold")
            plt.ylabel(r"$c_l$", fontsize=22, fontweight="bold")
            plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight="bold")
            plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight="bold")
            plt.xlim([0, 1])
            plt.tight_layout()
            pdf.savefig(dpi=300)

            plt.figure("cd")
            ax = plt.gca()
            plt.xlabel(r"$z/c$", fontsize=22, fontweight="bold")
            plt.ylabel(r"$c_d$", fontsize=22, fontweight="bold")
            plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight="bold")
            plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight="bold")
            plt.xlim([0, 1])
            plt.tight_layout()
            pdf.savefig(dpi=300)
