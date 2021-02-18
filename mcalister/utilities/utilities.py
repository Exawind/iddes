# ========================================================================
#
# Imports
#
# ========================================================================
import numpy as np
import pandas as pd
import yaml
import definitions as defs


# ========================================================================
#
# Function definitions
#
# ========================================================================
def get_merged_csv(fnames, **kwargs):
    lst = []
    for fname in fnames:
        try:
            df = pd.read_csv(fname, **kwargs)
            lst.append(df)
        except pd.io.common.EmptyDataError:
            pass
    return pd.concat(lst, ignore_index=True)


# ========================================================================
def parse_ic(fname):
    """Parse the Nalu yaml input file for the initial conditions"""
    with open(fname, "r") as stream:
        try:
            #dat = yaml.load(stream, Loader=yaml.FullLoader)
            dat = yaml.load(stream)
            u0 = float(
                dat["realms"][0]["initial_conditions"][0]["value"]["velocity"][0]
            )
            v0 = float(
                dat["realms"][0]["initial_conditions"][0]["value"]["velocity"][1]
            )
            try:
                w0 = float(
                    dat["realms"][0]["initial_conditions"][0]["value"]["velocity"][2]
                )
            except IndexError:
                w0 = 0.0
            umag = np.sqrt(u0 ** 2 + v0 ** 2 + w0 ** 2)
            rho0 = float(
                dat["realms"][0]["material_properties"]["specifications"][0]["value"]
            )
            mu = float(
                dat["realms"][0]["material_properties"]["specifications"][1]["value"]
            )
            flow_angle = np.arctan2(v0, u0)
            return u0, v0, w0, umag, rho0, mu, flow_angle

        except yaml.YAMLError as exc:
            print(exc)


# ========================================================================
def get_meshname(fname):
    """Parse the Nalu yaml input file for the mesh name"""
    with open(fname, "r") as stream:
        try:
            #dat = yaml.load(stream, Loader=yaml.FullLoader)
            dat = yaml.load(stream)
            return dat["realms"][0]["mesh"]

        except yaml.YAMLError as exc:
            print(exc)


# ========================================================================
def get_wing_slices(dim):
    """Return the wing slices"""
    return pd.DataFrame(defs.get_wing_slices(dim), columns=["zslice"])


# ========================================================================
def get_vortex_slices():
    """Return the vortex slices"""
    return pd.DataFrame(defs.get_vortex_slices(), columns=["xslice"])


# ========================================================================
def get_renames():
    return {
        "Points:0": "x",
        "Points:1": "y",
        "Points:2": "z",
        "pressure": "p",
        "iblank": "iblank",
        "iblank_cell": "iblank_cell",
        "absIBlank": "absIBlank",
        "pressure_force_:0": "fpx",
        "pressure_force_:1": "fpy",
        "pressure_force_:2": "fpz",
        "tau_wall": "tau_wall",
        "velocity_:0": "ux",
        "velocity_:1": "uy",
        "velocity_:2": "uz",
        "element_courant": "element_courant",
        "time": "time",
        "GlobalNodeId": "GlobalNodeId",
        "ObjectId": "ObjectId",
        "PedigreeElementId": "PedigreeElementId",
        "PedigreeNodeId": "PedigreeNodeId",
        "vtkValidPointMask": "vtkValidPointMask",
        "arc_length": "arc_length",
    }
