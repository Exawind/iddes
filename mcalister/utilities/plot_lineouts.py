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
        description="A simple plot tool for lineout quantities"
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

    # Constants
    chord = 1
    num_figs = 4
    tunnel_half_height = 2

    # Loop on folders
    for i, folder in enumerate(args.folders):

        # Setup
        fdir = os.path.abspath(folder)
        yname = os.path.join(fdir, "mcalister.yaml")
        half_wing_length = defs.get_half_wing_length()

        # simulation setup parameters
        u0, v0, w0, umag0, rho0, mu, flow_angle = utilities.parse_ic(yname)

        # Read in data (all time steps)
        prefix = "output"
        suffix = ".csv"

        # Get time steps
        pattern = prefix + "*" + suffix
        fnames = sorted(glob.glob(os.path.join(fdir, "lineouts", pattern)))
        times = []
        for fname in fnames:
            times.append(int(re.findall(r"\d+", fname)[-1]))
        times = np.unique(sorted(times))

        # Loop over each time step and get the dataframe
        for time in times:
            pattern = prefix + "*." + str(time) + suffix
            fnames = sorted(glob.glob(os.path.join(fdir, "lineouts", pattern)))
            df = utilities.get_merged_csv(fnames)
            df["time"] = time
            renames = utilities.get_renames()
            df.columns = [renames[col] for col in df.columns]
            xlocs = np.unique(df.x)
            for k, xloc in enumerate(xlocs):
                subdf = df[np.fabs(df.x - xloc) < 1e-5].copy()

                plt.figure(k * num_figs + 0)
                p = plt.plot(subdf.ux / umag0, subdf.y / chord, ls="-", lw=1)

                plt.figure(k * num_figs + 1)
                p = plt.plot(subdf.uy / umag0, subdf.y / chord, ls="-", lw=1)

                pdf = subdf[subdf.y > 0].copy()
                mdf = subdf[subdf.y <= 0].copy()

                fig = plt.figure(k * num_figs + 2)
                ax0 = plt.subplot(2, 1, 1)
                p = ax0.plot(
                    pdf.ux / umag0, (tunnel_half_height - pdf.y) / chord, ls="-", lw=1
                )
                ax0.set_yscale("log")
                ax0.set_ylim(ax0.get_ylim()[::-1])
                ax1 = plt.subplot(2, 1, 2, sharex=ax0)
                p = ax1.plot(
                    mdf.ux / umag0, (tunnel_half_height + mdf.y) / chord, ls="-", lw=1
                )
                ax1.set_yscale("log")

                fig = plt.figure(k * num_figs + 3)
                ax2 = plt.subplot(2, 1, 1)
                p = ax2.plot(
                    pdf.uy / umag0, (tunnel_half_height - pdf.y) / chord, ls="-", lw=1
                )
                ax2.set_yscale("log")
                ax2.set_ylim(ax0.get_ylim()[::-1])
                ax3 = plt.subplot(2, 1, 2, sharex=ax0)
                p = ax3.plot(
                    mdf.uy / umag0, (tunnel_half_height + mdf.y) / chord, ls="-", lw=1
                )
                ax3.set_yscale("log")

    # Save plots
    fname = "lineouts.pdf"
    with PdfPages(fname) as pdf:
        for k, xloc in enumerate(xlocs):
            plt.figure(k * num_figs + 0)
            ax = plt.gca()
            plt.xlabel(r"$u_x/u_\infty$", fontsize=22, fontweight="bold")
            plt.ylabel(r"$y/c$", fontsize=22, fontweight="bold")
            plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight="bold")
            plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight="bold")
            plt.tight_layout()
            pdf.savefig(dpi=300)

            plt.figure(k * num_figs + 1)
            ax = plt.gca()
            plt.xlabel(r"$u_y/u_\infty$", fontsize=22, fontweight="bold")
            plt.ylabel(r"$y/c$", fontsize=22, fontweight="bold")
            plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight="bold")
            plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight="bold")
            plt.tight_layout()
            pdf.savefig(dpi=300)

            plt.figure(k * num_figs + 2)
            plt.xlabel(r"$u_x/u_\infty$", fontsize=22, fontweight="bold")
            plt.ylabel(r"$\delta/c$", fontsize=22, fontweight="bold")
            plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight="bold")
            plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight="bold")
            plt.tight_layout()
            pdf.savefig(dpi=300)

            plt.figure(k * num_figs + 3)
            plt.xlabel(r"$u_y/u_\infty$", fontsize=22, fontweight="bold")
            plt.ylabel(r"$\delta/c$", fontsize=22, fontweight="bold")
            plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight="bold")
            plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight="bold")
            plt.tight_layout()
            pdf.savefig(dpi=300)
