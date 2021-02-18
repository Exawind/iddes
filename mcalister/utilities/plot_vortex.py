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
        description="A simple plot tool for vortex quantities"
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
    ninterp = 200
    mm2ft = 0.003_281
    mm2m = 1e-3
    num_figs = 3
    chord = 1
    exp_chord = 0.52

    # Loop on folders
    for i, folder in enumerate(args.folders):

        # Setup
        fdir = os.path.abspath(folder)
        yname = os.path.join(fdir, "mcalister.yaml")
        fname = "avg_slice.csv"
        half_wing_length = defs.get_half_wing_length()

        # simulation setup parameters
        u0, v0, w0, umag0, rho0, mu, flow_angle = utilities.parse_ic(yname)
        mname = utilities.get_meshname(yname)
        aoa = defs.get_aoa(mname)

        # experimental values
        edir = os.path.abspath(os.path.join("exp_data", f"aoa-{aoa}"))
        xslices = utilities.get_vortex_slices()
        xslices["xslicet"] = xslices.xslice + 1

        # data from other CFD simulations (SA model)
        sadir = os.path.abspath(os.path.join("sitaraman_data", f"aoa-{aoa}"))

        # Read in data
        df = pd.read_csv(os.path.join(fdir, "vortex_slices", fname), delimiter=",")
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

        # Lineout through vortex core in each slice
        vortex_core = []
        for k, (index, row) in enumerate(xslices.iterrows()):
            subdf = df[np.fabs(df.xr - row.xslicet) < 1e-3].copy()
            idx = subdf.p.idxmin()
            ymin, ymax = np.min(subdf.yr), np.max(subdf.yr)
            zmin, zmax = np.min(subdf.z), np.max(subdf.z)

            # vortex center location
            xc = np.array([subdf.xr.loc[idx]])
            yc = np.array([subdf.yr.loc[idx]])
            zc = np.array([subdf.z.loc[idx]])
            pc = np.array([subdf.p.loc[idx]])
            vortex_core.append([xc[0], yc[0], zc[0], pc[0]])

            # interpolate across the vortex core
            yline = np.linspace(ymin, ymax, ninterp)
            zline = np.linspace(zmin, zmax, ninterp)
            ux_yc = spi.griddata(
                (subdf.yr, subdf.z),
                subdf.uxr,
                (yc[:, None], zline[None, :]),
                method="cubic",
            )
            uy_yc = spi.griddata(
                (subdf.yr, subdf.z),
                subdf.uyr,
                (yc[:, None], zline[None, :]),
                method="cubic",
            )

            plt.figure(k * num_figs + 0)
            p = plt.plot(
                zline / chord,
                ux_yc[0, :] / umag0,
                ls="-",
                lw=2,
                color=cmap[i],
                label=f"SST {aoa}",
            )
            data = plt.gca().get_lines()[0].get_xydata()
            np.savetxt(f"{k}_ux.csv", data)
            p[0].set_dashes(dashseq[i])

            plt.figure(k * num_figs + 1)
            p = plt.plot(
                zline / chord,
                uy_yc[0, :] / umag0,
                ls="-",
                lw=2,
                color=cmap[i],
                label=f"SST {aoa}",
            )
            data = plt.gca().get_lines()[0].get_xydata()
            np.savetxt(f"{k}_uy.csv", data)
            p[0].set_dashes(dashseq[i])

            # Plot contours
            if i == len(args.folders) - 1:
                yi = np.linspace(ymin, ymax, ninterp)
                zi = np.linspace(zmin, zmax, ninterp)

                vcols = ["ux", "uy", "uz"]
                subdf["magvel"] = np.sqrt(np.square(subdf[vcols]).sum(axis=1))

                vi = spi.griddata(
                    (subdf.yr, subdf.z),
                    subdf.magvel,
                    (yi[None, :], zi[:, None]),
                    method="linear",
                )

                plt.figure(k * num_figs + 2)
                plt.imshow(vi.T, extent=[zmin, zmax, ymin, ymax], origin="lower")
                # plt.plot(subdf.z, subdf.yr, "ko", ms=1)
                plt.plot(zc, yc, "ok", ms=5)
                plt.plot(
                    zline, yc * np.ones(zline.shape), ls="--", lw=1, color=cmap[-1]
                )
                plt.colorbar()
                plt.xlim(zmin, zmax)
                plt.ylim(ymin, ymax)

            # Experimental data
            if i == 0:
                try:
                    ux_ename = glob.glob(
                        os.path.join(edir, f"ux_*_{row.xslice:.1f}.txt")
                    )[0]
                    uy_ename = glob.glob(
                        os.path.join(edir, f"uz_*_{row.xslice:.1f}.txt")
                    )[0]
                    exp_ux_df = pd.read_csv(ux_ename, header=0, names=["z", "ux"])
                    exp_uy_df = pd.read_csv(uy_ename, header=0, names=["z", "uy"])

                    # Change units
                    exp_ux_df["z"] = exp_ux_df.z * mm2m / exp_chord
                    exp_uy_df["z"] = exp_uy_df.z * mm2m / exp_chord

                    plt.figure(k * num_figs + 0)
                    plt.plot(
                        exp_ux_df.z,
                        exp_ux_df.ux,
                        ls="-",
                        lw=1,
                        color=cmap[-1],
                        marker=markertype[0],
                        mec=cmap[-1],
                        mfc=cmap[-1],
                        ms=6,
                        label="Exp.",
                    )

                    plt.figure(k * num_figs + 1)
                    plt.plot(
                        exp_uy_df.z,
                        exp_uy_df.uy,
                        ls="-",
                        lw=1,
                        color=cmap[-1],
                        marker=markertype[0],
                        mec=cmap[-1],
                        mfc=cmap[-1],
                        ms=6,
                        label="Exp.",
                    )
                except IndexError:
                    pass

            # Load corresponding SA data
            if i == 0:
                saname = os.path.join(sadir, f"uz_{row.xslicet:.1f}.csv")
                try:
                    sadf = pd.read_csv(saname)
                except FileNotFoundError:
                    continue
                yshift = -0.15
                p = plt.plot(
                    sadf.y + yshift,
                    sadf.uz,
                    ls="-",
                    color=cmap[-2],
                    label="Sitaraman et al. (2010)",
                )
                p[0].set_dashes(dashseq[-1])

        vortex_core = pd.DataFrame(vortex_core, columns=["xc", "yc", "zc", "pc"])
        plt.figure("vortex_core")
        p = plt.plot(
            vortex_core.xc,
            vortex_core.pc,
            lw=2,
            marker=markertype[i],
            color=cmap[i],
            label="SST",
        )
        p[0].set_dashes(dashseq[i])

    # Save plots
    fname = "vortex.pdf"
    with PdfPages(fname) as pdf:
        for k, (index, row) in enumerate(xslices.iterrows()):
            plt.figure(k * num_figs + 0)
            ax = plt.gca()
            plt.xlabel(r"$z/c$", fontsize=22, fontweight="bold")
            plt.ylabel(r"$u_x/u_\infty$", fontsize=22, fontweight="bold")
            plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight="bold")
            plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight="bold")
            ax.set_xlim([zmin, zmax])
            # if args.legend and k == 1:
            #     # ax.set_title(r"$x={0:.2f}$".format(row.xslicet))
            #     legend = ax.legend(loc="best")
            #     plt.figure(4 * num_figs + 1)
            #     handles, labels = plt.gca().get_legend_handles_labels()
            #     labels[0] = "SST/BASE"
            #     labels[3] = "SST/OVS-low"
            #     labels[4] = "SST/OVS-high"
            #     labels[5] = "SST-DES/OVS-low"
            #     labels[6] = "SST-DES/OVS-high"
            #     order = [0, 3, 4, 5, 6, 2, 1]
            #     plt.figure(k * num_figs + 0)
            #     plt.legend(
            #         [handles[idx] for idx in order], [labels[idx] for idx in order]
            #     )

            plt.tight_layout()
            pdf.savefig(dpi=300)

            plt.figure(k * num_figs + 1)
            ax = plt.gca()
            plt.xlabel(r"$z/c$", fontsize=22, fontweight="bold")
            plt.ylabel(r"$u_y/u_\infty$", fontsize=22, fontweight="bold")
            plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight="bold")
            plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight="bold")
            ax.set_xlim([zmin, zmax])
            # if args.legend:
            #     ax.set_title(r"$x={0:.2f}$".format(row.xslicet))
            plt.tight_layout()
            pdf.savefig(dpi=300)

            plt.figure(k * num_figs + 2)
            ax = plt.gca()
            plt.xlabel(r"$z/c$", fontsize=22, fontweight="bold")
            plt.ylabel(r"$y/c$", fontsize=22, fontweight="bold")
            plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight="bold")
            plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight="bold")
            ax.axis("equal")
            ax.set_xlim([zmin, zmax])
            ax.set_ylim([ymin, ymax])
            if args.legend:
                ax.set_title(r"$x={0:.2f}$".format(row.xslicet))
            plt.tight_layout()
            pdf.savefig(dpi=300)

        plt.figure("vortex_core")
        ax = plt.gca()
        plt.xlabel(r"$x/c$", fontsize=22, fontweight="bold")
        plt.ylabel(r"$p$", fontsize=22, fontweight="bold")
        plt.setp(ax.get_xmajorticklabels(), fontsize=16, fontweight="bold")
        plt.setp(ax.get_ymajorticklabels(), fontsize=16, fontweight="bold")
        # if args.legend:
        #     legend = ax.legend(loc="best")
        #     handles, labels = plt.gca().get_legend_handles_labels()
        #     labels[0] = "SST/BASE"
        #     labels[1] = "SST/OVS-low"
        #     labels[2] = "SST/OVS-high"
        #     labels[3] = "SST-DES/OVS-low"
        #     labels[4] = "SST-DES/OVS-high"
        #     order = [0, 1, 2, 3, 4]
        #     plt.legend([handles[idx] for idx in order], [labels[idx] for idx in order])
        plt.tight_layout()
        pdf.savefig(dpi=300)

    if args.show:
        plt.show()
