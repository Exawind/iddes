#!/usr/bin/env python3
#
# This makes a dataframe containing a temporal average of navg last slices


# ========================================================================
#
# Imports
#
# ========================================================================
import os
import re
import glob
import argparse
import numpy as np
import pandas as pd
import utilities

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
    parser = argparse.ArgumentParser(description="Average slices over time")
    parser.add_argument(
        "-f", "--folder", help="Folder where files are stored", type=str, required=True
    )
    parser.add_argument(
        "-n", "--navg", help="Number of time steps to average over", type=int, default=1
    )
    args = parser.parse_args()

    # Setup
    fdir = os.path.abspath(args.folder)
    oname = os.path.join(fdir, "avg_slice.csv")
    prefix = "output"
    suffix = ".csv"

    # Get time steps, keep only last navg steps
    pattern = prefix + "*" + suffix
    fnames = sorted(glob.glob(os.path.join(fdir, pattern)))
    times = []
    for fname in fnames:
        times.append(int(re.findall(r"\d+", fname)[-1]))
    times = np.unique(sorted(times))[-args.navg :]

    # Loop over each time step and get the dataframe
    lst = []
    for time in times:
        pattern = prefix + "*" + str(time) + suffix
        fnames = sorted(glob.glob(os.path.join(fdir, pattern)))
        df = utilities.get_merged_csv(fnames)
        lst.append(df)
        df["time"] = time
    df = pd.concat(lst, ignore_index=True)

    # Average
    avgdf = df.groupby(["Points:0", "Points:1", "Points:2"], as_index=False).mean()

    # Output to file
    avgdf.to_csv(oname, index=False)
