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
# Function definitions
#
# ========================================================================
def sort_by_angle(x, y, var):
    """Radial sort of variable on x and y for plotting

    Inspired from:
    http://stackoverflow.com/questions/35606712/numpy-way-to-sort-out-a-messy-array-for-plotting

    """

    # Get the angle wrt the mean of the cloud of points
    x0, y0 = x.mean(), y.mean()
    angle = np.arctan2(y - y0, x - x0)

    # Sort based on this angle
    idx = angle.argsort()
    idx = np.append(idx, idx[0])

    return x[idx], y[idx], var[idx]


# ========================================================================
#
# Main
#
# ========================================================================
if __name__ == "__main__":

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="A simple plot tool for wing quantities"
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
        fname = "avg_slice.csv"
        dim = defs.get_dimension(yname)
        half_wing_length = defs.get_half_wing_length()

        # simulation setup parameters
        u0, v0, w0, umag0, rho0, mu, flow_angle = utilities.parse_ic(yname)
        mname = utilities.get_meshname(yname)
        aoa = defs.get_aoa(mname)
        chord = 1

        # experimental values
        edir = os.path.abspath(os.path.join("exp_data", f"aoa-{aoa}"))
        zslices = utilities.get_wing_slices(dim)
        zslices["zslicen"] = zslices.zslice / half_wing_length

        # data from other CFD simulations (SA model)
        sadir = os.path.abspath(os.path.join("sitaraman_data", f"aoa-{aoa}"))

        # Read in data
        df = pd.read_csv(os.path.join(fdir, "wing_slices", fname), delimiter=",")
        renames = utilities.get_renames()
        df.columns = [renames[col] for col in df.columns]

        # Project coordinates on to chord axis
        chord_angle = np.radians(aoa) - flow_angle
        crdvec = np.array([np.cos(chord_angle), -np.sin(chord_angle)])
        rotcen = 0.25
        df["xovc"] = (
            np.dot(np.asarray([df.x - rotcen, df.y]).T, crdvec) / chord + rotcen
        )

        # Calculate the negative of the surface pressure coefficient
        df["cp"] = -df.p / (0.5 * rho0 * umag0 ** 2)

        # Plot cp in each slice
        for k, (index, row) in enumerate(zslices.iterrows()):
            subdf = df[np.fabs(df.z - row.zslice) < 1e-5]

            # Sort for a pretty plot
            x, y, cp = sort_by_angle(subdf.xovc.values, subdf.y.values, subdf.cp.values)

            # plot
            plt.figure(k)
            p = plt.plot(x, cp, ls="-", lw=2, color=cmap[i], label=f"SST {aoa} {dim}D")
            p[0].set_dashes(dashseq[i])

            # Load corresponding exp data
            if i == 0:
                try:
                    ename = glob.glob(
                        os.path.join(edir, f"cp_*_{row.zslicen:.3f}.txt")
                    )[0]
                    exp_df = pd.read_csv(ename, header=0, names=["x", "cp"])
                    plt.plot(
                        exp_df.x,
                        exp_df.cp,
                        ls="",
                        color=cmap[-1],
                        marker=markertype[0],
                        ms=6,
                        mec=cmap[-1],
                        mfc=cmap[-1],
                        label="Exp.",
                    )
                except IndexError:
                    pass

                # Load corresponding SA data
                satname = os.path.join(sadir, f"cp_{row.zslicen:.3f}_top.csv")
                sabname = os.path.join(sadir, f"cp_{row.zslicen:.3f}_bot.csv")
                try:
                    satop = pd.read_csv(satname)
                    sabot = pd.read_csv(sabname)
                except FileNotFoundError:
                    continue
                satop.sort_values(by=["x"], inplace=True)
                sabot.sort_values(by=["x"], inplace=True, ascending=False)
                p = plt.plot(
                    np.concatenate((satop.x, sabot.x), axis=0),
                    np.concatenate((satop.cp, sabot.cp), axis=0),
                    ls="-",
                    color=cmap[-2],
                    label="Sitaraman et al. (2010)",
                )
                p[0].set_dashes(dashseq[-1])

    # Save plots
    fname = "wing_cp.pdf"
    with PdfPages(fname) as pdf:

        for k, (index, row) in enumerate(zslices.iterrows()):
            plt.figure(k)
            ax = plt.gca()
            plt.xlabel(r"$x/c$", fontsize=22, fontweight="bold")
            plt.ylabel(r"$-c_p$", fontsize=22, fontweight="bold")
            plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight="bold")
            plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight="bold")
            plt.xlim([0, chord])
            plt.ylim([-1.5, 5.5])
            if args.legend and k == 11:
                legend = ax.legend(loc="best")
                handles, labels = plt.gca().get_legend_handles_labels()
                labels[0] = "SST/BASE"
                labels[3] = "SST/OVS-low"
                order = [0, 3, 2, 1]
                plt.legend(
                    [handles[idx] for idx in order], [labels[idx] for idx in order]
                )
                # ax.set_title(r"$z/s={0:.3f}$".format(row.zslicen))
            plt.tight_layout()
            pdf.savefig(dpi=300)

    if args.show:
        plt.show()
