#!/usr/bin/env python3

# ========================================================================
#
# Imports
#
# ========================================================================
import argparse
import os
import matplotlib.pyplot as plt
import pandas as pd


# ========================================================================
#
# Some defaults variables
#
# ========================================================================
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
        description="A simple plot tool for solver convergence stats"
    )
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
    for i, folder in enumerate(args.folders):

        # Setup
        fdir = os.path.abspath(folder)
        oname = os.path.join(fdir, "mcalister.o")

        times = []
        msns = []
        with open(oname, "r") as f:
            for line in f:
                if "Mean System Norm" in line:
                    line = line.split()
                    times.append(float(line[-1]))
                    msns.append(float(line[-3]))

        df = pd.DataFrame({"time": times, "msn": msns})

        # Plot
        plt.figure(0)
        p = plt.plot(df.time, df.msn, ls="-", lw=2, color=cmap[i])
        plt.yscale("log")
        plt.savefig("msn.png", format="png", dpi=300)
